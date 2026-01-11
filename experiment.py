"""
Run the experiment across all conditions
"""

import json
import time
from typing import List, Dict
from config import DATASET, RATE_LIMIT_DELAY, RESULTS_FILE, INTERMEDIATE_FILE
from prompts import create_prompt_condition_a, create_prompt_condition_b, create_prompt_condition_c
from llm_api import call_llm


def run_experiment(api_key: str, dataset: List[Dict] = None) -> List[Dict]:
    """
    Run experiment on all questions with 3 conditions
    
    Args:
        api_key: Groq API key
        dataset: List of questions (default: use DATASET from config)
        
    Returns:
        List of results with answers for each condition
    """
    if dataset is None:
        dataset = DATASET
    
    if not dataset:
        print("\n❌ ERROR: Dataset is empty!")
        print("Please run: python prepare_squad_dataset.py first")
        return []
    
    results = []
    
    print(f"\n🚀 Starting experiment with {len(dataset)} questions...")
    print(f"Estimated time: ~{len(dataset) * 3 * 2 // 60} minutes")
    print("="*60)
    
    for i, item in enumerate(dataset, 1):
        print(f"\n{'='*60}")
        print(f"Processing question {i}/{len(dataset)}")
        print(f"Question: {item['question'][:70]}...")
        print(f"{'='*60}")
        
        result = {
            "id": item["id"],
            "question": item["question"],
            "gold_answer": item["gold_answer"],
            "evidence": item["evidence"]
        }
        
        # Condition A: No Context
        print("→ Running Condition A (No Context)...")
        prompt_a = create_prompt_condition_a(item["question"])
        result["answer_a"] = call_llm(prompt_a, api_key)
        time.sleep(RATE_LIMIT_DELAY)
        
        # Condition B: Evidence-grounded
        print("→ Running Condition B (Evidence-grounded)...")
        prompt_b = create_prompt_condition_b(item["question"], item["evidence"])
        result["answer_b"] = call_llm(prompt_b, api_key)
        time.sleep(RATE_LIMIT_DELAY)
        
        # Condition C: Evidence + Self-verification
        print("→ Running Condition C (Evidence + Self-verification)...")
        prompt_c = create_prompt_condition_c(item["question"], item["evidence"])
        result["answer_c"] = call_llm(prompt_c, api_key)
        time.sleep(RATE_LIMIT_DELAY)
        
        results.append(result)
        
        # Save intermediate results (in case of crash)
        with open(INTERMEDIATE_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Completed question {i}/{len(dataset)}")
        
        # Show progress every 10 questions
        if i % 10 == 0:
            print(f"\n📊 Progress: {i}/{len(dataset)} ({i/len(dataset)*100:.1f}%)")
    
    # Save final results
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ Experiment complete! Results saved to: {RESULTS_FILE}")
    print(f"{'='*60}")
    
    return results


def create_evaluation_template(results: List[Dict], output_file: str):
    """
    Create markdown template for manual evaluation
    
    Args:
        results: Experiment results
        output_file: Output file path
    """
    template = """# EVALUATION TEMPLATE - SQUAD 2.0

## Instructions
Fill in 0 or 1 for each metric:
- Correctness: 1 = correct, 0 = incorrect (for unanswerable: 1 if refused correctly, 0 otherwise)
- Hallucination: 1 = hallucinated (info not in passage), 0 = no hallucination
- Abstention: 1 = refused/said "not enough info", 0 = answered
- Citation Faithfulness (C only): 1 = citation supports answer, 0 = citation incorrect

Note: For unanswerable questions (gold_answer = "UNANSWERABLE"):
- Correctness = 1 if model refused/abstained
- Hallucination = 1 if model gave a specific answer
- Abstention = 1 if model refused

"""
    
    for result in results:
        is_unanswerable = result['gold_answer'] == 'UNANSWERABLE'
        
        template += f"""
{'='*80}
## Question {result['id']} {'[UNANSWERABLE]' if is_unanswerable else ''}

**Question:** {result['question']}

**Gold Answer:** {result['gold_answer']}

**Evidence:** {result['evidence']}

---

### Condition A: No Context
**Answer A:** {result['answer_a']}

EVAL_A_CORRECTNESS: 
EVAL_A_HALLUCINATION: 
EVAL_A_ABSTENTION: 

---

### Condition B: Evidence-grounded
**Answer B:** {result['answer_b']}

EVAL_B_CORRECTNESS: 
EVAL_B_HALLUCINATION: 
EVAL_B_ABSTENTION: 

---

### Condition C: Evidence + Self-verification
**Answer C:** {result['answer_c']}

EVAL_C_CORRECTNESS: 
EVAL_C_HALLUCINATION: 
EVAL_C_ABSTENTION: 
EVAL_C_CITATION: 

{'='*80}

"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"✅ Evaluation template created: {output_file}")