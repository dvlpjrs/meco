import ast
import os
from bson.objectid import ObjectId


from app.utils.helper import random_id
from app.core.mongo_session import get_async_session


class FunctionExtractor(ast.NodeVisitor):
    def __init__(self, source_code, filename):
        self.source_code = source_code
        self.filename = filename
        self.functions = []
        self.imports = {}
        self.current_class = None

    def visit_Import(self, node):
        # Handle 'import module' statements
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # Handle 'from module import name' statements
        module = node.module
        for alias in node.names:
            self.imports[alias.asname or alias.name] = f"{module}.{alias.name}"
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Keep track of the current class (if needed)
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        func_info = {
            "id": random_id(),
            "name": node.name,
            "args": [],
            "returns": None,
            "body": ast.get_source_segment(self.source_code, node),
            "filename": self.filename,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "class": self.current_class,
        }

        # Extract arguments
        for arg in node.args.args:
            arg_name = arg.arg
            arg_type = ast.unparse(arg.annotation) if arg.annotation else None
            func_info["args"].append({"name": arg_name, "type": arg_type})

        # Extract return type
        if node.returns:
            func_info["returns"] = ast.unparse(node.returns)

        self.functions.append(func_info)
        self.generic_visit(node)


def extract_functions_from_file(filepath):
    with open(filepath, "r") as file:
        source_code = file.read()
    tree = ast.parse(source_code)
    extractor = FunctionExtractor(source_code, filepath)
    extractor.visit(tree)
    return extractor.functions, extractor.imports


class PydanticModelExtractor(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.models = {}

    def visit_ClassDef(self, node):
        bases = [base.id if isinstance(base, ast.Name) else None for base in node.bases]
        if "BaseModel" in bases:
            model_fields = {}
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign):
                    field_name = stmt.target.id
                    field_type = ast.unparse(stmt.annotation)
                    model_fields[field_name] = field_type
            self.models[node.name] = model_fields
        self.generic_visit(node)


def extract_pydantic_models(filepath):
    with open(filepath, "r") as file:
        source_code = file.read()
    tree = ast.parse(source_code)
    extractor = PydanticModelExtractor(source_code)
    extractor.visit(tree)
    return extractor.models


def assemble_function_data(functions, models, imports):
    for func in functions:
        # Resolve argument types
        for arg in func["args"]:
            if arg["type"] in imports:
                imported_type = imports[arg["type"]]
                if imported_type in models:
                    arg["fields"] = models[imported_type]
            elif arg["type"] in models:
                arg["fields"] = models[arg["type"]]

        # Resolve return type
        if func["returns"] in imports:
            imported_type = imports[func["returns"]]
            if imported_type in models:
                func["return_fields"] = models[imported_type]
        elif func["returns"] in models:
            func["return_fields"] = models[func["returns"]]
    return functions


def get_python_files(root_dir):
    python_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                python_files.append(os.path.join(dirpath, filename))
    return python_files


def extract_called_functions(function_body):
    """
    Extract all the function calls from a function body.
    """

    class FunctionCallExtractor(ast.NodeVisitor):
        def __init__(self):
            self.called_functions = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                self.called_functions.append(node.func.id)
            self.generic_visit(node)

    tree = ast.parse(function_body)
    extractor = FunctionCallExtractor()
    extractor.visit(tree)
    return extractor.called_functions


async def fetch_function_and_linked_sub_functions(
    job_id: str,
    function_id: str,
):
    db = get_async_session()

    # Step 1: Fetch the main function by ID
    codebase = await db.codebase.find_one({"job_id": ObjectId(job_id)})
    if not codebase:
        raise Exception(f"No codebase found for job_id {job_id}")

    functions = codebase["functions"]
    main_function = next((f for f in functions if f["id"] == function_id), None)

    if not main_function:
        raise Exception(f"No function found with ID {function_id}")

    # Step 2: Extract called functions from the main function's body
    called_function_names = extract_called_functions(main_function["body"])

    # Step 3: Fetch all linked sub-functions that are called within the main function
    sub_functions = []
    for func in functions:
        if func["name"] in called_function_names:
            sub_functions.append(
                {
                    "name": func["name"],
                    "body": func["body"],
                    "args": func["args"],
                    "returns": func["returns"],
                }
            )

    # Step 4: Return the main function and the linked sub-functions
    return {"main_function": main_function, "linked_sub_functions": sub_functions}
