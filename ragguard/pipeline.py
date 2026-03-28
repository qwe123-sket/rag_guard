from ragguard.config import settings
from ragguard.defense.acl import acl_filter
from ragguard.defense.trust import is_trusted_source
from ragguard.ingestion.indexer import DocumentIndexer
from ragguard.models import QueryResult, SourceDoc
from ragguard.retrieval.filter import apply_threshold, build_hits
from ragguard.retrieval.provenance import format_citations, render_provenance
from ragguard.retrieval.store import VectorStore


class SecureRAGPipeline:
    def __init__(self, store: VectorStore | None = None):
        self.store = store or VectorStore()
        self.indexer = DocumentIndexer(self.store)

    def bootstrap(self, docs: list[SourceDoc]) -> None:
        self.store.reset()
        self.indexer.index_batch(docs)

    def ingest(self, doc: SourceDoc) -> None:
        self.indexer.index(doc)

    def close(self) -> None:
        self.store.close()

    def query(
        self,
        question: str,
        user_dept: str = "ops",
        top_k: int | None = None,
        secure: bool = True,
    ) -> QueryResult:
        k = top_k or settings.top_k
        raw = self.store.search(question, self.indexer.embedder, k)
        hits = build_hits(raw)

        if not secure:
            return QueryResult(
                question=question,
                answer=self._compose_answer(question, hits),
                citations=format_citations(hits),
                hits=hits,
                blocked_hits=[],
                risks=[],
            )

        acl_ok, acl_denied = acl_filter(hits, user_dept)
        accepted, blocked = apply_threshold(acl_ok)
        blocked.extend(acl_denied)

        answer = self._compose_answer(question, accepted)
        citations = format_citations(accepted)
        risks = self._detect_risks(accepted, blocked)

        return QueryResult(
            question=question,
            answer=answer,
            citations=citations,
            hits=accepted,
            blocked_hits=blocked,
            risks=risks,
        )

    def _compose_answer(self, question: str, hits: list) -> str:
        if not hits:
            return "检索未返回符合权限与置信度要求的文档片段。"
        top = hits[0].text.strip()
        return f"根据内部文档：{top}"

    def _detect_risks(self, accepted: list, blocked: list) -> list[str]:
        risks: list[str] = []
        if any(not h.signature_valid for h in blocked):
            risks.append("检测到签名无效片段，已拦截")
        if any(h.score < settings.min_score for h in blocked):
            risks.append("存在低置信度检索结果，已过滤")
        if any(h.department == "external" for h in blocked):
            risks.append("拦截未授权外部文档")
        if any(not is_trusted_source(h.metadata.get("author", "")) for h in blocked):
            risks.append("拦截未认证来源文档")
        if not accepted:
            risks.append("无可用检索结果，存在上下文污染或越权风险")
        return risks

    def explain(self, result: QueryResult) -> str:
        parts = [
            f"Q: {result.question}",
            f"A: {result.answer}",
            render_provenance(result.citations),
        ]
        if result.risks:
            parts.append("风险提示: " + "; ".join(result.risks))
        if result.blocked_hits:
            parts.append(f"已拦截 {len(result.blocked_hits)} 条检索片段")
        return "\n".join(parts)
