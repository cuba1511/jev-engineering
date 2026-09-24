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


settings = Settings()
