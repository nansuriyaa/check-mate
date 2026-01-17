import os
import sys
from pathlib import Path
from io import BytesIO

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.data_ingestion.data_ingestion import SourcesDataIngestion
from src.checker.claims_checker import ClaimsChecker
from data.sources import sources
from logger import GLOBAL_LOGGER as log

class MockUploadedFile:
    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.name
        
    def read(self):
        with open(self.path, "rb") as f:
            return f.read()

def run_integration_test():
    log.info("Starting Integration Test...")
    
    try:
        # 1. Ingest Sources
        log.info("--- Step 1: Ingesting Web Sources ---")
        ingestion = SourcesDataIngestion(
            sources=sources,
            temp_base="data_test",
            faiss_base="faiss_test"
        )
        retriever = ingestion.build_retriever()
        log.info("✅ Retriever built successfully.")
        
        # 2. Check Claims from PDF
        log.info("--- Step 2: Checking Claims from PDF ---")
        checker = ClaimsChecker(
            temp_base="data_test",
            faiss_base="faiss_test"
        )
        
        pdf_path = "data/Donald Trump’s Second Term.pdf"
        if not os.path.exists(pdf_path):
            log.error(f"PDF file not found at {pdf_path}")
            return
            
        uploaded_file = MockUploadedFile(pdf_path)
        
        results = checker.check_claims(uploaded_file, retriever)
        
        log.info("--- Test Results ---")
        for res in results:
            log.info(f"Claim: {res['claim']}")
            log.info(f"Verification: {res['verification']}")
            log.info("-" * 30)
            
        log.info("✅ Integration test completed successfully.")

    except Exception as e:
        log.error(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_integration_test()
