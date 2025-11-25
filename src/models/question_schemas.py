from typing import List, Optional
from pydantic import BaseModel, Field, validator


class MCQQuestion(BaseModel):
    question: str = Field(..., description="The question to be answered")
    options: List[str] = Field(
        ..., description="The list of 4 possible options for the question"
    )
    correct_answer: str = Field(
        ..., description="The correct answer or answers to the question"
    )

    @validator("question", pre=True)
    def clean_question(cls, value):
        if isinstance(value, dict):
            return value.get("description", str(value))

        return str(value).strip()

    @validator("options", pre=True)
    def clean_options(cls, value):
        if isinstance(value, list):
            return [str(option).strip() for option in value]

        return [str(value).strip()]

    @validator("correct_answer", pre=True)
    def clean_correct_answer(cls, value):
        if isinstance(value, dict):
            return value.get("description", str(value))

        return str(value).strip()


class FillBlankQuestion(BaseModel):
    question: str = Field(
        ..., description="The question text with ____ marking the blank to be answered"
    )
    answer: str = Field(..., description="The correct word or phrase for the blank")

    @validator("question", pre=True)
    def clean_question(cls, value):
        if isinstance(value, dict):
            return value.get("description", str(value))

        return str(value).strip()

    @validator("answer", pre=True)
    def clean_answer(cls, value):
        if isinstance(value, dict):
            return value.get("description", str(value))

        return str(value).strip()
