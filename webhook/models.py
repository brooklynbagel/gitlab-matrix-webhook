from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Project(BaseModel):
    id: int
    name: str
    description: str
    web_url: str
    avatar_url: Optional[str] = None
    git_ssh_url: str
    git_http_url: str
    namespace: str
    visibility_level: int
    path_with_namespace: str
    default_branch: str
    homepage: str
    url: str
    ssh_url: str
    http_url: str


class Repository(BaseModel):
    name: str
    url: str
    description: str
    homepage: str
    git_http_url: str
    git_ssh_url: str
    visibility_level: int


class Author(BaseModel):
    name: str
    email: str


class Commit(BaseModel):
    id: str
    message: str
    title: str
    timestamp: datetime
    author: Author
    added: List[str]
    modified: List[str]
    removed: List[str]


class PushEvent(BaseModel):
    object_kind: str
    event_name: str
    before: str
    after: str
    ref: str
    checkout_sha: str
    user_id: int
    user_name: str
    user_username: str
    user_email: str
    user_avatar: str
    project_id: int
    project: Project
    repository: Repository
    commits: List[Commit]
    total_commits_count: int
    # TODO: Add other fields for event, see:
    # https://docs.gitlab.com/ee/user/project/integrations/webhook_events.html#push-events


# class MergeRequestEvent(BaseModel):
#     object_kind: str


# class Event(BaseModel):
#     __root__: Union[PushEvent, MergeRequestEvent]
