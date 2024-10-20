from fastapi import FastAPI, APIRouter


from app.schemas.endpoints.codebase import SubmitCodebaseRequest, SubmitCodebaseResponse

router = APIRouter()


@router.post("/")
async def submit_codebase(request: SubmitCodebaseRequest) -> SubmitCodebaseResponse:
    print(request)
    return SubmitCodebaseResponse(job_id="123")
