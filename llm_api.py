"""
LLM API caller using Groq (Llama models)
"""

from groq import Groq
import time
from config import MODEL


def call_llm(prompt: str, api_key: str) -> str:
    """
    Call Llama via Groq API
    
    Args:
        prompt: The prompt to send
        api_key: Groq API key
        
    Returns:
        Response text from Llama
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Initialize Groq client
            client = Groq(api_key=api_key)
            
            # Make API call
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=MODEL,
                temperature=0.7,
                max_tokens=500,
                top_p=0.95,
            )
            
            # Extract response
            response = chat_completion.choices[0].message.content
            return response.strip()
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle rate limit
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                wait_time = (attempt + 1) * 10
                print(f"  ⏳ Rate limit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            # Handle other errors
            if attempt < max_retries - 1:
                print(f"  ⚠️  Error: {error_msg}. Retry {attempt + 1}/{max_retries}...")
                time.sleep(3)
                continue
            else:
                print(f"\n❌ API Error after {max_retries} retries: {error_msg}")
                return f"[Error: {error_msg}]"
    
    return "[Failed after all retries]"