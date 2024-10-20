import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from git import Repo
import json

from app.core.mongo_session import get_async_session
from app.schemas.endpoints.codebase import SubmitCodebaseRequest, SubmitCodebaseResponse
from app.utils.backgrund import extract_functions, evaluate_functions
from app.utils.docker import generate_base_image, run_code_in_container
from app.utils.inference import get_initial_codebase

router = APIRouter()


@router.post("/")
async def submit_codebase(
    request: SubmitCodebaseRequest,
    background_tasks: BackgroundTasks,
    db=Depends(lambda: get_async_session()),
) -> SubmitCodebaseResponse:
    url = str(request.github_url)
    job = await db.jobs.insert_one({"url": url, "status": "pending"})
    if not job.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to insert job")

    job_id = str(job.inserted_id)
    temp_dir = f"./temp_dir/{job_id}/code/{url.split('/')[-1]}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    try:
        Repo.clone_from(url, temp_dir)
        print(f"Cloned repository to {temp_dir}")
        background_tasks.add_task(extract_functions, path=temp_dir, job_id=job_id)
        return SubmitCodebaseResponse(job_id=job_id)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to clone repository: {str(e)}"
        )
