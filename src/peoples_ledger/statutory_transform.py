from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Literal

from .paths import SCHEMA_DIR
from .schema_validator import SchemaRegistry


TransformStatus = Literal["applied", "abstained"]
TransformOperation = Literal["replace_text", "insert_after", "delete_text", "renumber_text"]


@dataclass(frozen=True)
class SourceSpan:
    source_record_id: str
    locator: str
    text_hash: str


@dataclass(frozen=True)
class AffectedAuthority:
    type: str
    citation: str


@dataclass(frozen=True)
class TransformRequest:
    id: str
    analysis_unit_id: str
    operation: TransformOperation
    current_text: str
    source_span: SourceSpan
    affected_authority: list[AffectedAuthority]
    target_text: str
    replacement_text: str | None = None
    insertion_text: str | None = None


@dataclass(frozen=True)
class TransformResult:
    status: TransformStatus
    before_text: str
    after_text: str | None
    transformation: dict[str, Any] | None
    review_triggers: list[str]
    unresolved_reason: str | None


def stable_text_hash(text: str) -> str:
    return "sha256:" + sha256(text.encode("utf-8")).hexdigest()


def apply_transform(request: TransformRequest) -> TransformResult:
    matches = request.current_text.count(request.target_text)
    if matches == 0:
        return _abstain(request, "target_text_not_found")
    if matches > 1:
        return _abstain(request, "target_text_ambiguous")

    if request.operation == "replace_text":
        if request.replacement_text is None:
            return _abstain(request, "replacement_text_required")
        after_text = request.current_text.replace(request.target_text, request.replacement_text, 1)
        schema_operation = "modify"
    elif request.operation == "renumber_text":
        if request.replacement_text is None:
            return _abstain(request, "replacement_text_required")
        after_text = request.current_text.replace(request.target_text, request.replacement_text, 1)
        schema_operation = "renumber"
    elif request.operation == "insert_after":
        if request.insertion_text is None:
            return _abstain(request, "insertion_text_required")
        after_text = request.current_text.replace(request.target_text, request.target_text + request.insertion_text, 1)
        schema_operation = "add"
    elif request.operation == "delete_text":
        after_text = request.current_text.replace(request.target_text, "", 1)
        schema_operation = "delete"
    else:
        return _abstain(request, "unsupported_operation")

    transformation = {
        "id": request.id,
        "analysis_unit_id": request.analysis_unit_id,
        "operation": schema_operation,
        "source_span": {
            "source_record_id": request.source_span.source_record_id,
            "locator": request.source_span.locator,
            "text_hash": request.source_span.text_hash,
        },
        "affected_authority": [
            {"type": authority.type, "citation": authority.citation}
            for authority in request.affected_authority
        ],
        "before_text_hash": stable_text_hash(request.current_text),
        "after_text_hash": stable_text_hash(after_text),
        "validation": {
            "deterministic": True,
            "round_trip_valid": _round_trip_valid(request, after_text),
            "reconciled": True,
            "unresolved_reason": None,
        },
    }
    SchemaRegistry(SCHEMA_DIR).validate("statutory_transformation", transformation)
    return TransformResult(
        status="applied",
        before_text=request.current_text,
        after_text=after_text,
        transformation=transformation,
        review_triggers=[],
        unresolved_reason=None,
    )


def _round_trip_valid(request: TransformRequest, after_text: str) -> bool:
    restored = reverse_transform(request, after_text)
    if restored is not None:
        return restored == request.current_text
    if request.operation == "delete_text":
        return request.target_text not in after_text
    return False


def reverse_transform(request: TransformRequest, after_text: str) -> str | None:
    if request.operation in {"replace_text", "renumber_text"} and request.replacement_text is not None:
        if after_text.count(request.replacement_text) != 1:
            return None
        return after_text.replace(request.replacement_text, request.target_text, 1)
    if request.operation == "insert_after" and request.insertion_text is not None:
        inserted = request.target_text + request.insertion_text
        if after_text.count(inserted) != 1:
            return None
        return after_text.replace(inserted, request.target_text, 1)
    return None


def _abstain(request: TransformRequest, reason: str) -> TransformResult:
    return TransformResult(
        status="abstained",
        before_text=request.current_text,
        after_text=None,
        transformation=None,
        review_triggers=[f"statutory_transform_abstained:{reason}"],
        unresolved_reason=reason,
    )
