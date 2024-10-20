from pydantic import BaseModel
from typing import Literal


class GetJobResponse(BaseModel):
    status: Literal[
        "pending", "running_function", "running_evolution", "failed", "success"
    ]


class GetJobFunctionResponse(BaseModel):
    function_names: list[str]


class StartJobFunctionEvaluationRequest(BaseModel):
    function_names: list[str]


class StartJobFunctionEvaluationResponse(BaseModel):
    status: Literal["success", "failed"]
    message: str | None = None


class EvolutionNode(BaseModel):
    id: str  # Unique identifier for the node
    status: Literal["pending", "running", "failed", "success"]
    cpu_usage: float
    memory_usage: float
    execution_time: float
    avg_score: float
    position: dict[str, float]
    children: list["EvolutionNode"] = []


class Edge(BaseModel):
    id: str
    source: str
    target: str


class GetJobEvolutionResponse(BaseModel):
    nodes: list[EvolutionNode] = []
    edges: list[Edge] = []
