from typing import Iterable, List
from pathlib import Path
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentPortalException
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".pptx", ".ppt", ".xlsx", ".xls", ".csv", ".md", ".sql", ".jpg", ".jpeg", ".png"}

def load_documents(path: Path) -> List[Document]:
    """Load docs using appropriate loader based on extension."""
    docs: List[Document] = []
    try:
        
        ext = path.suffix.lower()
        ext = path.suffix.lower()
        if ext == ".pdf":
            loader = PyPDFLoader(str(path))
        else:
            log.warning("Unsupported extension skipped", path=str(path))
            return docs
        docs.extend(loader.load())
        log.info("Documents loaded", count=len(docs))
        return docs
    except Exception as e:
        log.error("Failed loading documents", error=str(e))
        raise DocumentPortalException("Error loading documents", e) from e