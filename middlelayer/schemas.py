import datetime

from typing import List
from uuid import UUID
# pylint: disable=no-name-in-module
from pydantic import BaseModel


class WorkflowAsset(BaseModel):
    id: str


class ConsumerBase(BaseModel):
    id: str


class ConsumerCreate(ConsumerBase):
    workflow_backend_id: UUID


class Consumer(ConsumerBase):

    workflow_backend_id: UUID
    workflow_assets: List[WorkflowAsset] = []
    deployment_date: datetime.datetime

    class Config:
        orm_mode = True


class WorkflowBackendDetails(BaseModel):
    url: str
    token: str
