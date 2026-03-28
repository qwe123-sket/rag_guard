from ragguard.models import Citation, RetrievalHit


def format_citations(hits: list[RetrievalHit]) -> list[Citation]:
    citations: list[Citation] = []
    for i, hit in enumerate(hits, start=1):
        excerpt = hit.text.strip()
        if len(excerpt) > 120:
            excerpt = excerpt[:117] + "..."
        citations.append(
            Citation(
                index=i,
                doc_id=hit.doc_id,
                source_title=hit.source_title,
                chunk_id=hit.chunk_id,
                excerpt=excerpt,
                score=hit.score,
            )
        )
    return citations


def render_provenance(citations: list[Citation]) -> str:
    if not citations:
        return "引用来源：无匹配结果"
    lines = ["引用来源："]
    for c in citations:
        lines.append(
            f"  [{c.index}] {c.source_title} ({c.doc_id}) "
            f"score={c.score:.3f} — {c.excerpt}"
        )
    return "\n".join(lines)
