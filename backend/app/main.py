from fastapi import FastAPI

app = FastAPI(
    title="Meridyen API",
    description="Meridyen Dijital Refah ve Kişiselleştirilmiş İçerik Platformu API",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "meridyen-api",
        "version": "0.1.0",
    }