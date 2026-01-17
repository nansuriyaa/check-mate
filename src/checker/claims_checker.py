from utils.file_io import generate_session_id
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from pathlib import Path
from typing import Optional
from utils.file_io import save_uploaded_file
from utils.document_ops import load_documents
from model.models import PromptLoader
from prompt.prompt_library import PROMPT_REGISTRY
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import re

class ClaimsChecker:
    def __init__( self,
        temp_base: str = "data",
        faiss_base: str = "faiss_index",
        session_id: Optional[str] = None,
    ):
        try:
            self.model_loader = ModelLoader()
            self.session_id = session_id or generate_session_id()
            
            self.temp_base = Path(temp_base); self.temp_base.mkdir(parents=True, exist_ok=True)
            self.faiss_base = Path(faiss_base); self.faiss_base.mkdir(parents=True, exist_ok=True)
            
            self.temp_dir = self.temp_base / self.session_id
            self.faiss_dir = self.faiss_base / self.session_id
            
            # Use PROMPT_REGISTRY to load prompts
            self.fetch_claims_prompt = PROMPT_REGISTRY[PromptLoader.FETCH_KEY_CLAIMS.value]
            self.fact_check_prompt = PROMPT_REGISTRY[PromptLoader.FACT_CHECK.value]
            
            log.info("ChatIngestor initialized",
                          session_id=self.session_id,
                          temp_dir=str(self.temp_dir),
                          faiss_dir=str(self.faiss_dir))
        except Exception as e:
            log.error("Failed to initialize ChatIngestor", error=str(e))
            raise DocumentPortalException("Initialization error in ChatIngestor", e) from e

    def check_claims(self, uploaded_file, retriever):
        try:
            
            path = save_uploaded_file(uploaded_file, self.temp_dir)
            docs = load_documents(path)

            pdf_text = "\n".join([doc.page_content for doc in docs])

            log.info(f"PDF Text Length: {len(pdf_text)} characters")

            log.info("Extracting key claims from the PDF...")

            claim_extraction_prompt = self.fetch_claims_prompt

            claim_chain = claim_extraction_prompt | self.model_loader.load_llm() | StrOutputParser()

            # Invoke with the full PDF text (assuming it fits in context, otherwise we'd chunk)
            claims_raw = claim_chain.invoke({"text": pdf_text})

            log.info("--- Raw Extracted Claims ---")
            log.info(claims_raw)

            # Parse and clean claims
            claims = []
            for line in claims_raw.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering/bullets e.g. "1. " or "- "
                    cleaned = re.sub(r'^[\d\-\.\s]+', '', line)
                    if cleaned:
                        claims.append(cleaned)

            log.info(f"\nExtracted {len(claims)} individual claims.")

            verification_chain = (
                {"context": retriever, "claim": RunnablePassthrough()}
                | self.fact_check_prompt
                | self.model_loader.load_llm()
                | StrOutputParser()
            )

            results = []

            for i, claim in enumerate(claims):
                log.info(f"Checking Claim {i+1}/{len(claims)}")
                log.info(f"Claim: {claim}")
                
                try:
                    result = verification_chain.invoke(claim)
                    log.info(result)
                    results.append({"claim": claim, "verification": result})
                except Exception as e:
                    log.error(f"Error verifying claim: {e}")
                
                log.info("-" * 50)

            log.info("Verification Complete.")

            return results

        except Exception as e:
            log.error("Failed to build retriever", error=str(e))
            raise DocumentPortalException("Failed to build retriever", e) from e

