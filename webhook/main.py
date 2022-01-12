import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, Response, status
from nio import AsyncClient

from .models import *

app = FastAPI()

load_dotenv()
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
MATRIX_SERVER = os.getenv("MATRIX_SERVER")
MATRIX_USER = os.getenv("MATRIX_USER")
MATRIX_PASSWORD = os.getenv("MATRIX_PASSWORD")
MATRIX_ROOM_ID = os.getenv("MATRIX_ROOM_ID")


async def notify_element(event: PushEvent) -> None:
    # TODO: Consider splitting into smaller components and returning a status
    branch = event.ref.split("/")[-1]
    commit = sorted(event.commits, key=lambda commit: commit.timestamp, reverse=True)[0]

    # TODO: Find way to not have to nearly duplicate `body` and `formatted_body`
    body = (
        f"[{event.project.path_with_namespace}]"
        f" {event.user_username} pushed to {branch}: {commit.message.strip()} -"
        f" {event.project.homepage}/-/commit/{commit.id}"
    )
    formatted_body = (
        f"[<u>{event.project.path_with_namespace}</u>]"
        f" {event.user_username} pushed to <b>{branch}</b>: {commit.message.strip()} -"
        f" {event.project.homepage}/-/commit/{commit.id}"
    )

    try:
        client = AsyncClient(MATRIX_SERVER, MATRIX_USER)
        # TODO: See if can use a secured `token` instead of `password`
        await client.login(MATRIX_PASSWORD)
        await client.room_send(
            room_id=MATRIX_ROOM_ID,
            message_type="m.room.message",
            content={
                "body": body,
                "format": "org.matrix.custom.html",
                "formatted_body": formatted_body,
                "msgtype": "m.notice",
            },
        )
    finally:
        await client.close()


@app.post("/", status_code=status.HTTP_200_OK)
async def reciever(
    event: PushEvent,
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
