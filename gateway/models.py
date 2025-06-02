"""LLM models and response logic"""

from google import genai
from google.genai.types import HttpOptions
from openai import AsyncOpenAI
from typing import Optional, List, Dict, Union
from dotenv import load_dotenv
import os

load_dotenv()

gemini_clients: Dict[str, genai.Client] = dict()
# Vertex ai clients are loaded and used as per location
openai_client: AsyncOpenAI = None  # Single client for all location

SUPPORTED_MODELS = {
    "gemini-2.0-flash": {"provider": "vertex"},
    "gemini-1.5-flash": {"provider": "vertex"},
    "gemini-2.0-flash-001": {"provider": "vertex"},
    "gpt-4": {"provider": "openai"},
}


class ModelSelectionError(ValueError):
    pass


def get_models(
    user_selected_models: Optional[List[str]] = None,
) -> List[str]:
    """Determines the list of LLM models (names) to use for a query, prioritizing user selections.

    User-specified models are filtered against `SUPPORTED_MODELS`.
    If no valid user models are found, return ModelSelectionError
    If no models are specified by the user,
    this function defaults to using all models listed in `SUPPORTED_MODELS`.
    """

    if user_selected_models:

        valid_models = [
            model for model in user_selected_models if model in SUPPORTED_MODELS
        ]

        if not valid_models:
            raise ModelSelectionError(
                f"No selected models - {user_selected_models} are supported."
            )

        return valid_models

    else:
        return list(SUPPORTED_MODELS.keys())


def get_gemini_client(
    location: str, project_id: str = os.environ["VERTEXAI_PROJECT_ID"]
) -> genai.Client:
    """Retrieves or initializes a Google Gemini client for a specific location.

    Clients are cached globally by location.

    Args:
        location: The Google Cloud location (e.g., "us-central1").
        project_id: The Google Cloud Project ID. Defaults to `VERTEXAI_PROJECT_ID`
                    environment variable.
    Returns:
        A `google.genai.Client` instance.
    """
    if location not in gemini_clients:
        gemini_clients[location] = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            http_options=HttpOptions(api_version="v1"),
        )
    return gemini_clients[location]


def get_openai_client() -> AsyncOpenAI:
    """Retrieves or initializes the global OpenAI client.

    Returns:
        An `openai.AsyncOpenAI` instance.
    """
    global openai_client
    if openai_client is None:
        openai_client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    return openai_client


async def get_response_from_openai_model(
    client: AsyncOpenAI, model_name: str, contents: Union[str, List[str]]
) -> str:
    """Gets a response from a specified OpenAI model.

    Args:
        client: The AsyncOpenAI client.
        model_name: The name of the OpenAI model to use.
        contents: The prompt string or list of prompt strings.

    Returns:
        The model's response content as a string.
    """

    if isinstance(contents, str):
        response = await client.responses.create(
            model=model_name, input=contents, store=True
        )
        return response.output_text
    else:
        completion = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": c} for c in contents],
        )
        return completion.choices[0].message.content


async def get_response_from_gemini_model(
    client: genai.Client, model_name: str, contents: Union[str, List[str]]
) -> str:
    """Gets a response from a specified OpenAI model.

    Args:
        client: The AsyncOpenAI client.
        model_name: The name of the OpenAI model to use.
        prompt: The prompt string or list of prompt strings.

    Returns:
        The model's response content as a string.
    """
    response = await client.aio.models.generate_content(
        model=model_name, contents=contents
    )
    return response.text


if __name__ == "__main__":
    import asyncio

    # Test
    models = get_models(["gemini-2.0-flash", "gpt-4o-mini", "gpt-o3"])
    print(models)

    models = get_models()
    print(models)

    # models = get_models(["gpt-o3"])
    # print(models)

    gemini_client = get_gemini_client(location="us-central1")
    openai_client = get_openai_client()

    # response = asyncio.run(
    #     get_response_from_openai_model(
    #         client=openai_client,
    #         model_name="gpt-4o-mini",
    #         contents="How to be American president - in 1 sentence?",
    #     )
    # )

    # response = asyncio.run(
    #     get_response_from_gemini_model(
    #         client=gemini_client,
    #         model_name="gemini-2.0-flash",
    #         contents="How to be American president - in 1 sentence?",
    #     )
    # )
    # print(response)
