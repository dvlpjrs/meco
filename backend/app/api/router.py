from fastapi import APIRouter
from app.api.endpoints.codebase import router as codebase_router
from app.api.endpoints.job import router as job_router

router = APIRouter()

router.include_router(codebase_router, prefix="/codebase", tags=["codebase"])
router.include_router(job_router, prefix="/job", tags=["job"])
