from utils.file_io import generate_session_id
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentPortalException
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from utils.model_loader import ModelLoader
from pathlib import Path
from typing import Optional
from utils.file_io import save_uploaded_file
from utils.document_ops import load_documents
from model.models import PromptLoader
from prompt.prompt_library import PROMPT_REGISTRY
from langchain_core.documents import Document
from typing import List


class SourcesDataIngestion:

    def __init__(self, 
        sources: list[str],
        temp_base: str = "data",
        faiss_base: str = "faiss_index",
        session_id: Optional[str] = None,   
    ):
        try:
            self.sources = sources
            self.model_loader = ModelLoader()
            self.session_id = session_id or generate_session_id()
            
            self.temp_base = Path(temp_base); self.temp_base.mkdir(parents=True, exist_ok=True)
            self.faiss_base = Path(faiss_base); self.faiss_base.mkdir(parents=True, exist_ok=True)
            
            self.temp_dir = self.temp_base / self.session_id
            self.faiss_dir = self.faiss_base / self.session_id
            self.prompt_loader = PROMPT_REGISTRY[PromptLoader.FACT_CHECK.value]
            
            log.info("SourcesDataIngestion initialized",
                          session_id=self.session_id,
                          temp_dir=str(self.temp_dir),
                          faiss_dir=str(self.faiss_dir))
        except Exception as e:
            log.error("Failed to initialize SourcesDataIngestion", error=str(e))
            raise DocumentPortalException("Initialization error in SourcesDataIngestion", e) from e

    def _split(self, docs: List[Document], chunk_size=1000, chunk_overlap=200) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_documents(docs)
        log.info("Documents split", chunks=len(chunks), chunk_size=chunk_size, overlap=chunk_overlap)
        return chunks


    def build_retriever(self):
        try:
            log.info("Loading web sources...")
            web_loader = WebBaseLoader(self.sources)
            web_docs = web_loader.load()
            log.info(f"Loaded {len(web_docs)} web documents.")

            chunks = self._split(web_docs)

            vectorstore = FAISS.from_documents(chunks, self.model_loader.load_embeddings())
            vectorstore.save_local(self.faiss_dir)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            log.info("Vector Store ready.")
            
            return retriever
            
        except Exception as e:
            log.error("Failed to build retriever", error=str(e))
            raise DocumentPortalException("Failed to build retriever", e) from e




