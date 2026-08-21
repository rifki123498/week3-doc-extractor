from pydantic import BaseModel, Field, field_validator


class ManagementMember(BaseModel):
    name: str = Field(min_length=2)
    role: str = Field(min_length=2)


class InvestmentOpportunity(BaseModel):
    company_name: str = Field(min_length=2)
    industry: str = Field(min_length=2)
    funding_stage: str | None = None
    funding_amount: float | None = Field(default=None, ge=0)
    revenue: float | None = Field(default=None, ge=0)
    ebitda: float | None = None
    key_risks: list[str] = []
    management_team: list[ManagementMember] = []

    @field_validator("company_name")
    @classmethod
    def company_name_must_be_known(cls, value):
        if value.strip().lower() in {"unknown", "n/a", "none", ""}:
            raise ValueError("company_name must be explicitly stated in the document")
        return value