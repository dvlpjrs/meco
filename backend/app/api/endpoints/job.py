from fastapi import APIRouter

from app.schemas.endpoints.job import (
    GetJobResponse,
    GetJobFunctionResponse,
    StartJobFunctionEvaluationRequest,
    StartJobFunctionEvaluationResponse,
    GetJobEvolutionResponse,
)

router = APIRouter()


@router.get("/{job_id}")
async def get_job_status() -> GetJobResponse:
    return GetJobResponse(status="success")


@router.get("/function/{job_id}")
async def get_job_function_status() -> GetJobFunctionResponse:
    return GetJobFunctionResponse(function_names=["function1", "function2"])


@router.post("/function/start_evaluation/{job_id}")
async def start_job_function_evaluation(
    request: StartJobFunctionEvaluationRequest,
) -> StartJobFunctionEvaluationResponse:
    return StartJobFunctionEvaluationResponse(status="success")


@router.get("/evolution/{job_id}")
async def get_job_evolution_status() -> GetJobEvolutionResponse:
    return GetJobEvolutionResponse(nodes=[], edges=[])
