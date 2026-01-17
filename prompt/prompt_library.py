from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder

fetch_key_claims_prompt = PromptTemplate.from_template(
    """
    You are an expert fact-checker. Extract key claims from the following text that are specific, verifiable, and relevant to the topic of "Donald Trump's Second Term" foreign policy or actions.
    Focus on assertions of fact rather than opinions.
    Return the claims as a numbered list.
    
    Text:
    {text}
    
    Key Claims:
    """
)

fact_check_prompt = PromptTemplate.from_template(
    """
    You are a strict fact-checker. Verify the following claim based ONLY on the provided context retrieved from reliable sources.
    
    Claim: {claim}
    
    Context:
    {context}
    
    Determine if the claim is SUPPORTED, CONTRADICTED, or NOT_MENTIONED by the context.
    Provide a brief explanation citing specific parts of the context.
    
    Output Format:
    **Verdict**: [SUPPORTED / CONTRADICTED / NOT_MENTIONED]
    **Explanation**: [Your explanation here]
    """
)


PROMPT_REGISTRY = {
    "fetch_key_claims": fetch_key_claims_prompt,
    "fact_check": fact_check_prompt,
}

