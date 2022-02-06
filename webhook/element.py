import os

from dotenv import load_dotenv
from nio import AsyncClient


from .models import PushEvent

load_dotenv()
MATRIX_SERVER = os.environ["MATRIX_SERVER"]
MATRIX_USER = os.environ["MATRIX_USER"]
MATRIX_DEVICE_ID = os.getenv("MATRIX_DEVICE_ID")
MATRIX_PASSWORD = os.environ["MATRIX_PASSWORD"]
MATRIX_ROOM_ID = os.environ["MATRIX_ROOM_ID"]


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
        client = AsyncClient(
            homeserver=MATRIX_SERVER, user=MATRIX_USER, device_id=MATRIX_DEVICE_ID
        )
        # TODO: See if can use a secured `token` instead of `password`
        await client.login(password=MATRIX_PASSWORD)
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
