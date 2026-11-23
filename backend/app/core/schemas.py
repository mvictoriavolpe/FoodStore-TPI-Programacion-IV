from pydantic import model_validator
from sqlmodel import SQLModel


class PartialUpdate(SQLModel):
    @model_validator(mode="before")
    @classmethod
    def reject_null_fields(cls, values):
        if isinstance(values, dict) and any(value is None for value in values.values()):
            raise ValueError(
                "Los campos enviados no admiten null; omitilos para conservar su valor"
            )
        return values
