"""
Prompt templates for three experimental conditions
Updated for SQuAD 2.0 with unanswerable questions
"""

def create_prompt_condition_a(question: str) -> str:
    """
    Condition A: No Context
    Input: chỉ có câu hỏi
    """
    return f"Answer this question: {question}"


def create_prompt_condition_b(question: str, evidence: str) -> str:
    """
    Condition B: Evidence-grounded
    Input: question + passage với instruction strict
    """
    return f"""Answer this question using ONLY the information in the passage below. 
If the passage does not contain enough information to answer the question, respond with exactly: "Not enough information"

Passage: {evidence}

Question: {question}

Answer:"""


def create_prompt_condition_c(question: str, evidence: str) -> str:
    """
    Condition C: Evidence-grounded + Self-verification
    Input: question + passage + self-check steps
    """
    return f"""Follow these steps carefully:

Step 1: Read the passage and the question carefully.
Step 2: Try to answer the question using ONLY information from the passage.
Step 3: Quote the specific sentence(s) from the passage that support your answer.
Step 4: Verify if your answer is fully supported by the evidence:
   - If YES: Label your answer as "SUPPORTED" 
   - If NO or UNCERTAIN: Say "Not enough information"

Passage: {evidence}

Question: {question}

Response:"""