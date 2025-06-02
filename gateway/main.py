from fastapi import FastAPI, Header
import os
from fastapi.responses import (
    FileResponse,
)

from gateway.schemas import *
from gateway.models import *
from gateway.evaluate import LLMJudge
import asyncio

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

    async def get_eval_result(judge: LLMJudge, model: str, prompt: str, response: str):
        eval_result = await judge(prompt, response)

        return SingleModelOutput(
            name=model,
            output=response,
            score=eval_result["score"],
            reason=eval_result["reason"],
        )

    model_list = get_models(user_selected_models=input.models)
    gemini_client = get_gemini_client(location=location)
    openai_client = get_openai_client()

    tasks = []
    for model in model_list:
        if SUPPORTED_MODELS[model]["provider"] == "vertex":
            tasks.append(
                asyncio.wait_for(
                    get_response_from_gemini_model(
                        client=gemini_client, model_name=model, contents=input.prompt
                    ),
                    timeout=10,
                )
            )
        elif SUPPORTED_MODELS[model]["provider"] == "openai":
            tasks.append(
                asyncio.wait_for(
                    get_response_from_openai_model(
                        client=openai_client, model_name=model, contents=input.prompt
                    ),
                    timeout=10,
                )
            )

    responses = await asyncio.gather(*tasks, return_exceptions=True)
    llm_judge = LLMJudge(client=gemini_client)

    eval_tasks = [
        asyncio.wait_for(
            get_eval_result(
                judge=llm_judge, model=model, prompt=input.prompt, response=response
            ),
            timeout=10,
        )
        for model, response in zip(model_list, responses)
        if not isinstance(response, Exception)
    ]

    eval_results = await asyncio.gather(*eval_tasks, return_exceptions=True)
    eval_results = [res for res in eval_results if not isinstance(res, Exception)]
    best_result = max(eval_results, key=lambda x: x.score)

    return OutputSchema(
        response=best_result.output,
        quality_score=best_result.score,
        reason_of_score=best_result.reason,
        model_used=best_result.name,
        all_models_considered_with_scores=eval_results,
    )

    # Dummy example
    # so = SingleModelOutput(
    #     name="gemini-2.0-flash",
    #     output="I don't know",
    #     score=0.1,
    #     reason="Model doesn't answer but honest",
    # )

    # out = OutputSchema(
    #     response="I don't know",
    #     quality_score=0.1,
    #     reason_of_score="Model doesn't answer but honest",
    #     model_used="gemini-2.0-flash",
    #     all_models_considered_with_scores=[
    #         SingleModelOutput(
    #             name="gemini-2.0-flash",
    #             output="I don't know",
    #             score=0.1,
    #             reason="Model doesn't answer but honest",
    #         )
    #     ],
    # )


# EG

# {
#     "models": ["gemini-2.0-flash", "gemini-1.5-flash"],
#     "prompt": "How Ukrain conduct drone attack in Russia?",
# }

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
