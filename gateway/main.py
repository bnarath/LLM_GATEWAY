from fastapi import FastAPI
import os
from fastapi.responses import (
    FileResponse,
)


app = FastAPI(
    title="LLM Gateway",
    summary="Entry point to your LLM queries",
    version="0.0.1",
    description="Get you the best response from a variety of LLM providers",
)


@app.get("/", response_class=FileResponse)
def root():
    return FileResponse(
        path=os.path.join("gateway", "static", "index.html"), media_type="text/html"
    )
