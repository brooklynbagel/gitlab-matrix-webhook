import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, Response, Request, status
from pydantic import parse_obj_as, ValidationError

from .models import WebhookEvent, PushEvent
from .element import notify_element


app = FastAPI()

load_dotenv()
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")


@app.post("/", status_code=status.HTTP_200_OK)
async def reciever(
    event: WebhookEvent,
    request: Request,
    response: Response,
    x_gitlab_event: Optional[str] = Header(None),
    x_gitlab_token: Optional[str] = Header(None),
):
    """
    Webhook endpoint.

    This responds to the [**webhook events**](https://docs.gitlab.com/ee/user/project/integrations/webhook_events.html)
    GitLab webhook send.

    Currently, only [**Push Events**](https://docs.gitlab.com/ee/user/project/integrations/webhook_events.html#push-events)
    are supported.

    Returns a JSON object with the following fields:

    * "ok" - Boolean indicating whether the webhook executed successfully.
    * "error" - String containing an error message if there is one.

    """
    if not x_gitlab_token == GITLAB_TOKEN:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"ok": False, "error": "X-Gitlab-Token is not valid"}

    data = await request.json()
    event_type = x_gitlab_event.replace(" ", "").replace("Hook", "Event")

    try:
        event_type = globals()[event_type]
        event = parse_obj_as(event_type, data)
    except KeyError:
        pass
    except ValidationError:
        pass

    if isinstance(event, PushEvent):
        await notify_element(event)

    return {"ok": True, "error": None}


@app.get("/up", status_code=status.HTTP_200_OK)
def up():
    """
    Check that the webhook service is up.

    Returns an empty JSON object.
    """
    # TODO: Check that talking to Matrix works
    return {}
