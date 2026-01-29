from typing import List, Annotated
import json
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from api.auth import get_current_user_from_cookie
from api.models import User
from src.checker.claims_checker import ClaimsChecker
from src.data_ingestion.data_ingestion import SourcesDataIngestion
from logger import GLOBAL_LOGGER as log

router = APIRouter(tags=["check"])

@router.post("/check-claims")
async def check_claims_endpoint(
    file: UploadFile = File(...),
    sources: str = Form(...), # JSON string of sources
    current_user: User = Depends(get_current_user_from_cookie)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    try:
        source_list = json.loads(sources)
        if not source_list:
             raise HTTPException(status_code=400, detail="No sources provided")
             
        # Initialize Ingestion
        ingestion = SourcesDataIngestion(sources=source_list)
        retriever = ingestion.build_retriever()
        
        # Initialize Checker
        checker = ClaimsChecker()
        
        # For save_uploaded_file compatibility, we need to ensure the file object 
        # behaves as expected or pass the raw file-like object if it has the attributes.
        # FastAPI UploadFile works with the updated utility.
        # However, save_uploaded_file calls .read(). FastAPI's UploadFile.read() is async.
        # But UploadFile.file.read() is sync.
        # Let's wrap it to ensure compatibility.
        
        class FileWrapper:
            def __init__(self, upload_file):
                self.name = upload_file.filename
                self.file = upload_file.file
            def read(self):
                return self.file.read()
        
        wrapped_file = FileWrapper(file)
        
        results = checker.check_claims(wrapped_file, retriever)
        
        return {"results": results}
        
    except Exception as e:
        log.error("Error during claim check", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
