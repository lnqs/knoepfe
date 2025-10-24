"""Base configuration class for all Pydantic models."""

from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    """Base class for all configuration models.

    Provides strict validation and forbids extra fields by default.
    """

    model_config = ConfigDict(
        extra="forbid",  # Strict by default - no extra fields allowed
        validate_assignment=True,  # Validate on attribute assignment
    )
