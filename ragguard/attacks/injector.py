from ragguard.ingestion.signer import sign_chunk
from ragguard.models import SourceDoc


def poison_doc(base: SourceDoc, payload: str) -> SourceDoc:
    """在正文末尾插入误导性段落，模拟投毒文档。"""
    poisoned = f"{base.content}\n\n{payload}"
    return SourceDoc(
        doc_id=f"poison-{base.doc_id}",
        title=base.title,
        content=poisoned,
        department=base.department,
        classification=base.classification,
        author="unknown",
        version="9.9",
    )


def tamper_signature(doc_id: str, chunk_index: int, text: str, meta: dict) -> str:
    """生成错误签名，模拟入库后内容被篡改。"""
    return sign_chunk(doc_id, chunk_index, text + " ", meta)


def unauthorized_doc(title: str, content: str) -> SourceDoc:
    return SourceDoc(
        doc_id="ext-unauth-001",
        title=title,
        content=content,
        department="external",
        classification="confidential",
        author="attacker",
    )
