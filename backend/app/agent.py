import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_openai import ChatOpenAI

from app.tools.weather import get_weather


load_dotenv()


def _build_llm() -> ChatOpenAI:
    """Create a ChatOpenAI client configured for OpenRouter."""
    base_url = "https://openrouter.ai/api/v1"
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Please configure it in your environment."
        )

    app_url = os.getenv("APP_URL", "http://localhost:5173")
    app_name = os.getenv("APP_NAME", "SanchAI Weather")

    return ChatOpenAI(
        base_url=base_url,
        model=model,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": app_url,
            "X-Title": app_name,
        },
        temperature=0.2,
    )


async def _run_agent(inputs: Dict[str, Any]) -> str:
    """
    Minimal LangChain-based agent:
    - Uses LLM to decide if the question is about weather + extract city.
    - If weather-related, calls the `get_weather` tool for real data.
    - Then lets the LLM craft a final natural-language answer.
    """
    user_input = str(inputs.get("input", "")).strip()
    if not user_input:
        return "Please provide a question."

    llm = _build_llm()

    # 1) Ask LLM to decide if this is a weather question and extract city.
    intent_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an intent classifier for SanchAI Weather.\n"
                    "If the question is about weather or clothing/umbrella decisions "
                    "for a location, respond ONLY in this exact JSON format:\n"
                    "{{\"is_weather\": true/false, \"city\": \"<city or empty string>\"}}\n"
                    "Do not add any other text.\n"
                    "Examples:\n"
                    "- Input: \"What is the weather of Pune?\" -> "
                    "{{\"is_weather\": true, \"city\": \"Pune\"}}\n"
                    "- Input: \"Tell me a joke\" -> "
                    "{{\"is_weather\": false, \"city\": \"\"}}\n"
                    "- Input: \"Do I need an umbrella in Mumbai today?\" -> "
                    "{{\"is_weather\": true, \"city\": \"Mumbai\"}}\n"
                ),
            ),
            ("user", "{input}"),
        ]
    )

    intent_chain = intent_prompt | llm
    intent_msg = await intent_chain.ainvoke({"input": user_input})
    intent_text = intent_msg.content if hasattr(intent_msg, "content") else str(intent_msg)

    is_weather = False
    city = ""
    try:
        import json

        parsed = json.loads(intent_text)
        is_weather = bool(parsed.get("is_weather"))
        city = str(parsed.get("city") or "").strip()
    except Exception:
        # Fallback: simple heuristic
        lowered = user_input.lower()
        if "weather" in lowered or "umbrella" in lowered or "rain" in lowered or "jacket" in lowered:
            is_weather = True

    # 2) If weather intent, call the LangChain weather tool for real data.
    weather_info = None
    if is_weather:
        tool_input = city or user_input
        # `get_weather` is an async LangChain tool; use ainvoke.
        weather_info = await get_weather.ainvoke({"city": tool_input})

    # 3) Ask LLM to produce the final answer, using weather_info when present.
    answer_system = (
        "You are SanchAI Weather, a helpful assistant.\n\n"
        "If the user asks about weather for any city (even indirectly), you MUST base "
        "your answer on the provided real weather data and MUST NOT guess temperatures "
        "or conditions.\n\n"
        "If no weather data is provided, answer normally without inventing any real-time "
        "weather information."
    )

    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", answer_system),
            (
                "user",
                "User question: {question}\n\n"
                "Real weather data (may be null): {weather_data}",
            ),
        ]
    )

    answer_chain = answer_prompt | llm
    answer_msg = await answer_chain.ainvoke(
        {"question": user_input, "weather_data": weather_info}
    )
    answer_text = answer_msg.content if hasattr(answer_msg, "content") else str(answer_msg)
    return answer_text


def build_agent_executor() -> Runnable:
    """Expose the agent as a Runnable compatible with .ainvoke()."""
    return RunnableLambda(_run_agent)


# Shared runnable-style executor for app usage
agent_executor: Runnable = build_agent_executor()


