import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("JEV_MODEL", "jev-1.13.0")
    # Source: https://typesafe.ai/
    input_price_per_1m: float = float(os.getenv("INPUT_PRICE_PER_1M_TOKENS", "0.042"))
    output_price_per_1m: float = float(os.getenv("OUTPUT_PRICE_PER_1M_TOKENS", "0"))

    # Optional OpenAI baseline for `make demo`. Check current prices at https://openai.com/api/pricing/
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_input_price_per_1m: float | None = (
        float(os.environ["OPENAI_INPUT_PRICE_PER_1M_TOKENS"]) if os.getenv("OPENAI_INPUT_PRICE_PER_1M_TOKENS") else None
    )
    openai_output_price_per_1m: float | None = (
        float(os.environ["OPENAI_OUTPUT_PRICE_PER_1M_TOKENS"]) if os.getenv("OPENAI_OUTPUT_PRICE_PER_1M_TOKENS") else None
    )


settings = Settings()
