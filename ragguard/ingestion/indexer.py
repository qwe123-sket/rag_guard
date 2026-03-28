from uuid import uuid4

from langchain_huggingface import HuggingFaceEmbeddings

from ragguard.config import settings
from ragguard.ingestion.chunker import split_document
from ragguard.ingestion.signer import sign_chunk
from ragguard.models import ChunkRecord, SourceDoc
from ragguard.retrieval.store import VectorStore


class DocumentIndexer:
    def __init__(self, store: VectorStore):
        self.store = store
        self._embedder = HuggingFaceEmbeddings(model_name=settings.embedding_model)

    @property
    def embedder(self) -> HuggingFaceEmbeddings:
        return self._embedder

    def index(self, doc: SourceDoc) -> list[ChunkRecord]:
        chunks = split_document(doc)
        records: list[ChunkRecord] = []

        for idx, text in enumerate(chunks):
            meta = {
                "department": doc.department,
                "classification": doc.classification,
                "author": doc.author,
                "version": doc.version,
            }
            signature = sign_chunk(doc.doc_id, idx, text, meta)
            chunk_id = f"{doc.doc_id}::{idx}"
            record = ChunkRecord(
                chunk_id=chunk_id,
                doc_id=doc.doc_id,
                text=text,
                signature=signature,
                department=doc.department,
                classification=doc.classification,
                source_title=doc.title,
                chunk_index=idx,
                author=doc.author,
                version=doc.version,
            )
            records.append(record)

        self.store.upsert(records, self._embedder)
        return records

    def index_batch(self, docs: list[SourceDoc]) -> list[ChunkRecord]:
        all_records: list[ChunkRecord] = []
        for doc in docs:
            all_records.extend(self.index(doc))
        return all_records
