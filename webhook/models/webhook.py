from pydantic import BaseModel


class WebhookEvent(BaseModel):
    object_kind: str
