from pathlib import Path
from typing import List
import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentPortalException


SUPPORTED_EXTENSIONS = {".pdf"}


# ----------------------------- #
# Helpers (file I/O + loading)  #
# ----------------------------- #

def generate_session_id(prefix: str = "session") -> str:
    ist = ZoneInfo("Asia/Kolkata")
    return f"{prefix}_{datetime.now(ist).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def save_uploaded_file(uploaded_file, target_dir: Path) -> str:
    """Save uploaded files and return local paths."""
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        name = getattr(uploaded_file, "name", "file")
        ext = Path(name).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            log.warning("Unsupported file skipped", filename=name)
            return
        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(name).stem).lower()
        fname = f"{safe_name}_{uuid.uuid4().hex[:6]}{ext}"
        fname = f"{uuid.uuid4().hex[:8]}{ext}"
        out = target_dir / fname
        with open(out, "wb") as f:
            if hasattr(uploaded_file, "read"):
                f.write(uploaded_file.read())
            else:
                f.write(uploaded_file.getbuffer())  # fallback
        log.info("File saved for ingestion", uploaded=name, saved_as=str(out))
        return out
    except Exception as e:
        log.error("Failed to save uploaded files", error=str(e), dir=str(target_dir))
        raise DocumentPortalException("Failed to save uploaded files", e) from e


