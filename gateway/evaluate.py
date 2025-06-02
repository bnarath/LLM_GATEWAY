"""Evaluators"""

import os
import json
from google.genai import Client
from google.genai.types import GenerateContentConfig
from deepeval.metrics import *
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class DeepEVAL:
    def __init__(self):
        self.correctness_metric = GEval(
            name="correctness",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
            ],
            criteria="Measure how good the 'actual_output' as a response to the 'input'.",
            model="gpt-4o",
        )

    async def __call__(self, prompt: str, response: str):
        test_case = LLMTestCase(input=prompt, actual_output=response)
        score = await self.correctness_metric.a_measure(test_case=test_case)
        return score


class LLMJudge:
    class LLM_Judge_Response_Schema(BaseModel):
        score: float = Field(ge=0, le=1)
        reason: str

    def __init__(self, client: Client):
        self.client = client
        self.model = "gemini-2.0-flash"
        self.response_schema = self.LLM_Judge_Response_Schema
        self.eval_prompt = (
            "You are an expert language model evaluator."
            "Given the original prompt and the model's response, rate the quality of the response from 0 to 1 based on the following criteria.\n"
            "criteria: {criteria}\n"
            "Respond ONLY in JSON with the following keys:\n"
            "- score: a float from 0 to 1 (inclusive -> 1 indicates the best score).\n"
            "- reason: a short explanation for the score.\n"
            "Prompt: {prompt}\n"
            "Response: {response}"
        )

    async def __call__(
        self,
        prompt: str,
        response: str,
        criteria: str = "Quality of Response. How good the Response is with respect to Prompt",
    ):
        try:
            _input = self.eval_prompt.format(
                criteria=criteria, prompt=prompt, response=response
            )
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=_input,
                config=GenerateContentConfig(
                    temperature=0,
                    top_p=1,
                    max_output_tokens=1024,
                    response_mime_type="application/json",
                    response_schema=self.response_schema,
                ),
            )
            return json.loads(response.text)
        except Exception:
            return {"score": 0, "reason": "Internal Evaluation Error"}


if __name__ == "__main__":
    from gateway.models import get_gemini_client
    import asyncio

    # gemini_client = get_gemini_client(
    #     location="us-central1", project_id=os.environ["VERTEXAI_PROJECT_ID"]
    # )
    # llm_gudge = LLMJudge(gemini_client)
    # print(llm_gudge.eval_prompt)

    # response = asyncio.run(llm_gudge(prompt="What is 87+22?", response="Answer is 109"))
    # print(response)

    # de_judge = DeepEVAL()
    # response = asyncio.run(
    #     de_judge(prompt="Explain mathematics", response="I don't know")
    # )
    # print(response)
