import json
from openai import OpenAI
from decouple import config
from pydantic import BaseModel

client = OpenAI(api_key=config("OPENAI_API_KEY"))


def get_initial_codebase(function_body: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Just combine the input main_function and linked_sub_functions together and add required imports do not change the existing code or anything else to the code. at the end call the main_function with the sample inputs",
            },
            {
                "role": "user",
                "content": function_body,
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "code_with_samples",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "main_code": {
                            "type": "string",
                            "description": "combine/structure the main_function and linked_sub_functions to make a final code but try not to modify the existing code. at the end call the main_function with the sample inputs",
                        },
                        "sample_inputs": {
                            "type": "array",
                            "description": "An array of sample inputs to test the main code.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "input": {
                                        "type": "string",
                                        "description": "The sample input to pass to the main code.",
                                    }
                                },
                                "required": ["input"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["main_code", "sample_inputs"],
                    "additionalProperties": False,
                },
            },
        },
    )
    return json.loads(response.choices[0].message.content)


def get_optimized_codebase_openai(codebase: str):
    pass


def get_optimized_codebase_nebius(codebase: str, model_id: str):
    pass
