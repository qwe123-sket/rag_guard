from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path("data")
    chroma_dir: Path = Path("data/chroma")
    report_dir: Path = Path("reports")
    collection: str = "enterprise_kb"
    chunk_size: int = 400
    chunk_overlap: int = 60
    top_k: int = 4
    min_score: float = 0.62
    signing_key: str = "ragguard-dev-key"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


settings = Settings()
