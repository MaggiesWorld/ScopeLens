from dataclasses import dataclass
from pathlib import Path
from typing import Literal


TargetType = Literal["file", "folder"]


@dataclass
class InspectionTarget:
    path: Path
    target_type: TargetType

@dataclass
class InspectionResult:
    path: Path
    target_type: TargetType
    name: str
    details: dict
    candidates: list["Candidate"]
    summary: dict

    def to_dict(self) -> dict:
        details = dict(self.details)

        if "items" in details:
            details["items"] = [
                item.to_dict()
                for item in details["items"]
            ]

        if "structure" in details:
            details["structure"] = (
                details["structure"].to_dict()
            )

        return {
            "path": str(self.path),
            "target_type": self.target_type,
            "name": self.name,
            "details": details,
            "candidates": [
                candidate.to_dict()
                for candidate in self.candidates
            ],
            "summary": self.summary,
        }

@dataclass
class InspectionOptions:
    description: str | None = None
    ignored_names: set[str] | None = None
    max_file_size: int = 1_000_000
    max_candidates: int = 10
    minimum_relevance_score: int = 1
    max_structure_items: int = 500

@dataclass
class DiscoveryItem:
    name: str
    type: str
    category: str | None = None
    size_bytes: int | None = None
    relevance_score: int = 0
    skipped: bool = False
    skip_reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "category": self.category,
            "size_bytes": self.size_bytes,
            "relevance_score": self.relevance_score,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
        }

@dataclass
class Candidate:
    name: str
    type: str
    category: str | None
    size_bytes: int | None
    relevance_score: int
    content: str
    truncated: bool
    relevance_explanation: dict
    facts: dict

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "category": self.category,
            "size_bytes": self.size_bytes,
            "relevance_score": self.relevance_score,
            "content": self.content,
            "truncated": self.truncated,
            "relevance_explanation": self.relevance_explanation,
            "facts": self.facts,
        }

@dataclass
class StructureItem:
    path: str
    type: str
    depth: int

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "type": self.type,
            "depth": self.depth,
        }

@dataclass
class StructureResult:
    items: list[StructureItem]
    truncated: bool
    total_discovered: int

    def to_dict(self) -> dict:
        return {
            "items": [
                item.to_dict()
                for item in self.items
            ],
            "truncated": self.truncated,
            "total_discovered": self.total_discovered,
        }