import gc
import shutil
import uuid
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from ragguard.config import settings
from ragguard.models import ChunkRecord


class VectorStore:
    def __init__(self, workspace: Path | None = None):
        self._workspace = workspace or (settings.chroma_dir / uuid.uuid4().hex[:8])
        self._workspace.mkdir(parents=True, exist_ok=True)
        self._client: Chroma | None = None

    @property
    def workspace(self) -> Path:
        return self._workspace

    def _bind(self, embedder: Embeddings) -> Chroma:
        if self._client is None:
            self._client = Chroma(
                collection_name=settings.collection,
                embedding_function=embedder,
                persist_directory=str(self._workspace),
            )
        return self._client

    def close(self) -> None:
        self._client = None
        gc.collect()

    def reset(self) -> None:
        self.close()
        if self._workspace.exists():
            shutil.rmtree(self._workspace, ignore_errors=True)
        self._workspace.mkdir(parents=True, exist_ok=True)

    def upsert(self, records: list[ChunkRecord], embedder: Embeddings) -> None:
        if not records:
            return
        db = self._bind(embedder)
        db.add_texts(
            texts=[r.text for r in records],
            metadatas=[
                {
                    "chunk_id": r.chunk_id,
                    "doc_id": r.doc_id,
                    "signature": r.signature,
                    "department": r.department,
                    "classification": r.classification,
                    "source_title": r.source_title,
                    "chunk_index": r.chunk_index,
                    "author": r.author,
                    "version": r.version,
                }
                for r in records
            ],
            ids=[r.chunk_id for r in records],
        )

    def search(
        self,
        query: str,
        embedder: Embeddings,
        top_k: int,
        where: dict | None = None,
    ) -> list[tuple[str, dict, float]]:
        db = self._bind(embedder)
        kwargs: dict = {"k": top_k}
        if where:
            kwargs["filter"] = where
        hits = db.similarity_search_with_relevance_scores(query, **kwargs)
        return [(doc.page_content, doc.metadata, score) for doc, score in hits]
