from fastapi import FastAPI, Request, Depends, HTTPException, status

from app.api.router import router

app = FastAPI()

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Hello Dev!"}
