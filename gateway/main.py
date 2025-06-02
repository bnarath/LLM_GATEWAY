from fastapi import FastAPI, Header
import os
from fastapi.responses import (
    FileResponse,
)

from gateway.schemas import *


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


@app.post("/generate", response_model=OutputSchema)
async def respond(
    input: InputSchema, location: str = Header("us-central1")
):  # Header(...)

    print(input)
    print(location)
    so = SingleModelOutput(
        name="gemini-2.0-flash",
        output="I don't know",
        score=0.1,
        reason="Model doesn't answer but honest",
    )

    out = OutputSchema(
        response="I don't know",
        quality_score=0.1,
        reason_of_score="Model doesn't answer but honest",
        model_used="gemini-2.0-flash",
        all_models_considered_with_scores=[
            SingleModelOutput(
                name="gemini-2.0-flash",
                output="I don't know",
                score=0.1,
                reason="Model doesn't answer but honest",
            )
        ],
    )

    return out


# curl -X 'POST' \
#   'http://0.0.0.0:8000/generate' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "prompt": "How Ukrain conduct drone attack in Russia?"
# }'

# curl -X 'POST' \
#   'http://0.0.0.0:8000/generate' \
#   -H 'accept: application/json' \
#   -H 'location: us-central1' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "models": ["gemini-2.0-flash",
#              "gemini-1.5-flash"],
#   "prompt": "How Ukrain conduct drone attack in Russia?"
# }'


# {
#   "models": ["gemini-2.0-flash",
#              "gemini-1.5-flash"],
#   "prompt": "How Ukrain conduct drone attack in Russia?"
# }
