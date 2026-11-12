
from fastapi import FastAPI

app = FastAPI(
    title="Document Intelligence API",
    description=(
        "An intelligent document processing, "
        "retrieval and question-answering platform."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "document-intelligence-api",
        "version": "0.1.0",
    }
