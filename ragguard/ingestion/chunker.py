from langchain_text_splitters import RecursiveCharacterTextSplitter

from ragguard.config import settings
from ragguard.models import SourceDoc


def split_document(doc: SourceDoc) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", "。", "；", " ", ""],
    )
    return splitter.split_text(doc.content)
