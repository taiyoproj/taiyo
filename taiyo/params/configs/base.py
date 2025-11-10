from pydantic import BaseModel, ConfigDict


class ParamsConfig(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=False)
