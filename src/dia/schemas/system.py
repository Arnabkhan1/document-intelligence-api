from pydantic import BaseModel


class SystemInfoResponse(BaseModel):
    app_name: str
    app_version: str
    environment: str
    api_prefix: str
