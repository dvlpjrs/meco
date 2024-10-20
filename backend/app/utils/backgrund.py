import json
from bson import ObjectId
from app.utils.function_extractor import (
    extract_functions_from_file,
    extract_pydantic_models,
    assemble_function_data,
    get_python_files,
    fetch_function_and_linked_sub_functions,
)
from app.utils.docker import run_code_in_container
from app.utils.inference import get_initial_codebase
from app.core.mongo_session import get_async_session


async def extract_functions(path: str, job_id: str):
    db = get_async_session()
    try:
        await db.jobs.update_one(
            {"_id": ObjectId(job_id)}, {"$set": {"status": "extracting_functions"}}
        )

        python_files = get_python_files(path)
        all_functions = []
        all_models = {}
        all_imports = {}

        for filepath in python_files:
            functions, imports = extract_functions_from_file(filepath)
            models = extract_pydantic_models(filepath)
            all_functions.extend(functions)
            all_models.update(models)
            all_imports.update(imports)
        assembled_functions = assemble_function_data(
            all_functions, all_models, all_imports
        )
        await db.jobs.update_one(
            {"_id": ObjectId(job_id)}, {"$set": {"status": "running_evolution"}}
        )
        await db.codebase.insert_one(
            {
                "job_id": ObjectId(job_id),
                "functions": assembled_functions,
            }
        )
    except Exception as e:
        print(e)
        await db.jobs.update_one(
            {"_id": ObjectId(job_id)}, {"$set": {"status": "failed"}}
        )


async def evaluate_functions(job_id: str, function_ids: list[str]):
    db = get_async_session()
    for function_id in function_ids:
        function = await fetch_function_and_linked_sub_functions(job_id, function_id)
        initial_codebase = get_initial_codebase(function_body=json.dumps(function))
        print(initial_codebase)
        results = run_code_in_container(
            image_id="base_image", code=initial_codebase["main_code"]
        )
        print(results)
