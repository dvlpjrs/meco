from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.core.mongo_session import get_async_session
from app.schemas.endpoints.job import (
    GetJobResponse,
    GetJobFunctionResponse,
    StartJobFunctionEvaluationRequest,
    StartJobFunctionEvaluationResponse,
    GetJobEvolutionResponse,
    FunctionInfo,
    FunctionArg,
)

router = APIRouter()


@router.get("/{job_id}")
async def get_job_status() -> GetJobResponse:
    return GetJobResponse(status="success")


@router.get("/function/{job_id}")
async def get_job_function_status(
    job_id: str, db=Depends(lambda: get_async_session())
) -> GetJobFunctionResponse:
    job = await db.jobs.find_one(
        {
            "_id": ObjectId(job_id),
            "status": {"$ne": ["pending", "extracting_functions"]},
        }
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    else:
        extract_function = await db.codebase.find_one({"job_id": ObjectId(job_id)})
        return GetJobFunctionResponse(
            functions=[
                FunctionInfo(
                    name=func["name"],
                    id=func["id"],
                    code=func["body"],
                    args=[
                        FunctionArg(name=arg["name"], type=arg["type"])
                        for arg in func.get("args", [])  # Ensure 'args' is provided
                    ],
                )
                for func in extract_function.get(
                    "functions", []
                )  # Ensure 'functions' is provided
            ]
        )


@router.post("/function/start_evaluation/{job_id}")
async def start_job_function_evaluation(
    job_id: str,
    request: StartJobFunctionEvaluationRequest,
    db=Depends(lambda: get_async_session()),
) -> StartJobFunctionEvaluationResponse:
    fetch_functions = await db.codebase.find_one({"job_id": ObjectId(job_id)})
    if not fetch_functions:
        raise HTTPException(status_code=404, detail="Codebase not found")
    for function_id in request.function_ids:
        if function_id not in [func["id"] for func in fetch_functions["functions"]]:
            raise HTTPException(status_code=404, detail="Function not found")
    await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": "running_evolution", "function_ids": request.function_ids}},
    )
    return StartJobFunctionEvaluationResponse(status="success")


@router.get("/evolution/{job_id}")
async def get_job_evolution_status() -> GetJobEvolutionResponse:
    return GetJobEvolutionResponse(nodes=[], edges=[])
