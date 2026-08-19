from fastapi import APIRouter


router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "meridyen-api",
        "version": "0.1.0",
    }