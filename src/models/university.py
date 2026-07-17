from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class UniversityModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    country: str
    state_province: str
    domains: list[str]
    web_pages: list[str]
    alpha_two_code: str

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:  # noqa: ANN401
        if not isinstance(data, dict):
            return data
        return {
            "name": data.get("name", ""),
            "country": data.get("country", ""),
            "state_province": data.get("state-province") or "",
            "alpha_two_code": data.get("alpha_two_code", ""),
            "domains": data.get("domains", []),
            "web_pages": data.get("web_pages", []),
        }  # pyright: ignore[reportUnknownVariableType]
