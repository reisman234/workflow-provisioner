# generated by datamodel-codegen:
#   filename:  contract-agreement-api.yaml
#   timestamp: 2023-05-16T13:27:30+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

# pylint: disable=no-name-in-module
from pydantic import BaseModel, Field


class ApiErrorDetail(BaseModel):
    invalidValue: Optional[str] = None
    message: Optional[str] = None
    path: Optional[str] = None
    type: Optional[str] = None


class Constraint(BaseModel):
    edctype: str


class CriterionDto(BaseModel):
    operandLeft: Dict[str, Any]
    operandRight: Optional[Dict[str, Any]] = None
    operator: str


class FieldType(Enum):
    SET = 'set'
    OFFER = 'offer'
    CONTRACT = 'contract'


class SortOrder(Enum):
    ASC = 'ASC'
    DESC = 'DESC'


class QuerySpecDto(BaseModel):
    filter: Optional[str] = None
    filterExpression: Optional[List[CriterionDto]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    sortField: Optional[str] = None
    sortOrder: Optional[SortOrder] = None


class Action(BaseModel):
    constraint: Optional[Constraint] = None
    includedIn: Optional[str] = None
    type: Optional[str] = None


class Prohibition(BaseModel):
    action: Optional[Action] = None
    assignee: Optional[str] = None
    assigner: Optional[str] = None
    constraints: Optional[List[Constraint]] = None
    target: Optional[str] = None
    uid: Optional[str] = None


class ContractAgreementDto(BaseModel):
    assetId: str
    consumerAgentId: str
    contractEndDate: Optional[int] = None
    contractSigningDate: Optional[int] = None
    contractStartDate: Optional[int] = None
    id: str
    policy: Policy
    providerAgentId: str


class Duty(BaseModel):
    action: Optional[Action] = None
    assignee: Optional[str] = None
    assigner: Optional[str] = None
    consequence: Optional[Duty] = None
    constraints: Optional[List[Constraint]] = None
    parentPermission: Optional[Permission] = None
    target: Optional[str] = None
    uid: Optional[str] = None


class Permission(BaseModel):
    action: Optional[Action] = None
    assignee: Optional[str] = None
    assigner: Optional[str] = None
    constraints: Optional[List[Constraint]] = None
    duties: Optional[List[Duty]] = None
    target: Optional[str] = None
    uid: Optional[str] = None


class PolicyType(BaseModel):
    field_policytype: Optional[FieldType] = Field(None, alias='@policytype')


class Policy(BaseModel):
    field_type: Optional[PolicyType] = Field(None, alias='@type')
    assignee: Optional[str] = None
    assigner: Optional[str] = None
    extensibleProperties: Optional[Dict[str, Dict[str, Any]]] = None
    inheritsFrom: Optional[str] = None
    obligations: Optional[List[Duty]] = None
    permissions: Optional[List[Permission]] = None
    prohibitions: Optional[List[Prohibition]] = None
    target: Optional[str] = None


ContractAgreementDto.update_forward_refs()
Duty.update_forward_refs()
