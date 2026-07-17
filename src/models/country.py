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

        name_obj: dict[str, object] = data.get("name", {}) or {}  # type: ignore[assignment]
        currencies_obj: dict[str, object] = data.get("currencies", {}) or {}  # type: ignore[assignment]
        currencies_values = list(currencies_obj.values())  # pyright: ignore[reportUnknownArgumentType]
        primary: dict[str, object] = currencies_values[0] if currencies_values else {}  # pyright: ignore[reportAssignmentType]

        return {
            "name": name_obj.get("common", ""),
            "iso_code": data.get("cca2", ""),
            "continent": (data.get("continents") or [""])[0],
            "population": data.get("population", 0),
            "currency_name": primary.get("name", ""),
        }  # pyright: ignore[reportUnknownVariableType]
