from pydantic import BaseModel, ConfigDict


class ParamsMixin(BaseModel):
    model_config = ConfigDict(validate_by_name=True)
