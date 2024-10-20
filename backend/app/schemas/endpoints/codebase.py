from pydantic import BaseModel, HttpUrl


class SubmitCodebaseRequest(BaseModel):
    github_url: HttpUrl


class SubmitCodebaseResponse(BaseModel):
    job_id: str
