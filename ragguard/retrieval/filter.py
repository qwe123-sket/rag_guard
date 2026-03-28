from ragguard.config import settings
from ragguard.defense.trust import is_trusted_source
from ragguard.ingestion.signer import verify_chunk
from ragguard.models import RetrievalHit


def apply_threshold(hits: list[RetrievalHit]) -> tuple[list[RetrievalHit], list[RetrievalHit]]:
    accepted: list[RetrievalHit] = []
    rejected: list[RetrievalHit] = []
    for hit in hits:
        author = hit.metadata.get("author", "")
        trusted = is_trusted_source(author)
        if hit.score >= settings.min_score and hit.signature_valid and trusted:
            accepted.append(hit)
        else:
            rejected.append(hit)
    return accepted, rejected


def build_hits(raw: list[tuple[str, dict, float]]) -> list[RetrievalHit]:
    hits: list[RetrievalHit] = []
    for text, meta, score in raw:
        chunk_meta = {
            "department": meta.get("department", ""),
            "classification": meta.get("classification", ""),
            "author": meta.get("author", ""),
            "version": meta.get("version", ""),
        }
        valid = verify_chunk(
            meta["doc_id"],
            int(meta["chunk_index"]),
            text,
            chunk_meta,
            meta.get("signature", ""),
        )
        hits.append(
            RetrievalHit(
                chunk_id=meta["chunk_id"],
                text=text,
                score=round(score, 4),
                doc_id=meta["doc_id"],
                source_title=meta.get("source_title", ""),
                department=meta.get("department", ""),
                classification=meta.get("classification", ""),
                signature_valid=valid,
                metadata=meta,
            )
        )
    return hits
