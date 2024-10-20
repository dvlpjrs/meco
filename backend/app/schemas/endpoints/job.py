from pydantic import BaseModel
from typing import Literal


class GetJobResponse(BaseModel):
    status: Literal[
        "pending", "extracting_functions", "running_evolution", "failed", "success"
    ]


class FunctionArg(BaseModel):
    name: str
    type: str | None = None


class FunctionInfo(BaseModel):
    name: str
    id: str
    code: str
    args: list[FunctionArg] = []


class GetJobFunctionResponse(BaseModel):
    functions: list[FunctionInfo]


class StartJobFunctionEvaluationRequest(BaseModel):
    function_ids: list[str]


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
