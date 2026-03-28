from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class SourceDoc:
    doc_id: str
    title: str
    content: str
    department: str
    classification: str  # public / internal / confidential
    author: str
    version: str = "1.0"


@dataclass
class ChunkRecord:
    chunk_id: str
    doc_id: str
    text: str
    signature: str
    department: str
    classification: str
    source_title: str
    chunk_index: int
    author: str
    version: str


@dataclass
class RetrievalHit:
    chunk_id: str
    text: str
    score: float
    doc_id: str
    source_title: str
    department: str
    classification: str
    signature_valid: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Citation:
    index: int
    doc_id: str
    source_title: str
    chunk_id: str
    excerpt: str
    score: float


@dataclass
class QueryResult:
    question: str
    answer: str
    citations: list[Citation]
    hits: list[RetrievalHit]
    blocked_hits: list[RetrievalHit]
    risks: list[str]


@dataclass
class AttackReport:
    scenario: str
    injected: bool
    retrieved_poison: bool
    leaked_sensitive: bool
    invalid_citation: bool
    details: list[str]


@dataclass
class ScenarioAudit:
    scenario: str
    question: str
    objective: str
    baseline_answer: str
    hardened_answer: str
    baseline_leaked: bool
    hardened_leaked: bool
    baseline_hit_count: int
    hardened_hit_count: int
    blocked_count: int
    defense_effective: bool
    risks: list[str]
    notes: list[str]


@dataclass
class SecurityAuditReport:
    project: str
    generated_at: str
    doc_count: int
    chunk_count: int
    scenarios: list[ScenarioAudit]
    tamper_blocked: bool
    normal_query: QueryResult
    defense_measures: list[str]
