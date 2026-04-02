from fastapi import APIRouter

from src.api.schemas import Response

router = APIRouter(tags=["健康检查"])


@router.get("/health", response_model=Response[dict])
def health():
    return Response.ok({"status": "ok"})
