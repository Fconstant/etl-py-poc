from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class CountryModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    iso_code: str
    continent: str
    population: int
    currency_name: str

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:  # noqa: ANN401
        if not isinstance(data, dict):
            return data

        names_obj: dict[str, object] = data.get("names", {}) or {}  # type: ignore[assignment]
        currencies_list: list[dict[str, object]] = data.get("currencies") or []  # type: ignore[assignment]
        primary: dict[str, object] = currencies_list[0] if currencies_list else {}  # pyright: ignore[reportUnknownVariableType,reportAssignmentType]
        codes: dict[str, object] = data.get("codes", {}) or {}  # type: ignore[assignment]

        return {
            "name": names_obj.get("common", ""),
            "iso_code": codes.get("alpha_2", ""),
            "continent": (data.get("continents") or [""])[0],
            "population": data.get("population", 0),
            "currency_name": primary.get("name", ""),
        }  # pyright: ignore[reportUnknownVariableType]
