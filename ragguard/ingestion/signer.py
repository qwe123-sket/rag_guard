import hashlib
import hmac
import json
from typing import Any

from ragguard.config import settings


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def sign_chunk(doc_id: str, chunk_index: int, text: str, meta: dict[str, Any]) -> str:
    body = {
        "doc_id": doc_id,
        "chunk_index": chunk_index,
        "text": text,
        "meta": meta,
    }
    digest = hmac.new(
        settings.signing_key.encode(),
        _canonical(body).encode(),
        hashlib.sha256,
    )
    return digest.hexdigest()


def verify_chunk(
    doc_id: str,
    chunk_index: int,
    text: str,
    meta: dict[str, Any],
    signature: str,
) -> bool:
    expected = sign_chunk(doc_id, chunk_index, text, meta)
    return hmac.compare_digest(expected, signature)
