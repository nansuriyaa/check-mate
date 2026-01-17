from enum import Enum

class PromptLoader(str, Enum):
    FETCH_KEY_CLAIMS = "fetch_key_claims"
    FACT_CHECK = "fact_check"
