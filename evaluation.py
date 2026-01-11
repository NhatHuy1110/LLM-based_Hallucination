"""
Parse and process manual evaluations
"""

import re
from typing import List, Dict


def parse_evaluation_file(eval_file: str) -> List[Dict]:
    """
    Parse evaluation file and extract scores
    
    Args:
        eval_file: Path to evaluation file
        
    Returns:
        List of evaluation dictionaries
    """
    with open(eval_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    evaluations = []
    
    # Find all question IDs
    questions = re.findall(r'## Question (\d+)', content)
    
    for q_id in questions:
        # Extract section for this question
        pattern = rf'## Question {q_id}.*?(?=## Question|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            continue
        
        section = match.group(0)
        eval_dict = {'id': int(q_id)}
        
        # Parse scores for each condition
        for condition in ['A', 'B', 'C']:
            # Correctness
            correctness = re.search(rf'EVAL_{condition}_CORRECTNESS:\s*(\d)', section)
            if correctness:
                eval_dict[f'{condition.lower()}_correctness'] = int(correctness.group(1))
            
            # Hallucination
            hallucination = re.search(rf'EVAL_{condition}_HALLUCINATION:\s*(\d)', section)
            if hallucination:
                eval_dict[f'{condition.lower()}_hallucination'] = int(hallucination.group(1))
            
            # Abstention
            abstention = re.search(rf'EVAL_{condition}_ABSTENTION:\s*(\d)', section)
            if abstention:
                eval_dict[f'{condition.lower()}_abstention'] = int(abstention.group(1))
        
        # Citation for condition C
        citation = re.search(r'EVAL_C_CITATION:\s*(\d)', section)
        if citation:
            eval_dict['c_citation'] = int(citation.group(1))
        
        evaluations.append(eval_dict)
    
    return evaluations


def validate_evaluations(evaluations: List[Dict]) -> bool:
    """
    Check if all evaluations are complete
    
    Args:
        evaluations: List of evaluation dictionaries
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        'a_correctness', 'a_hallucination', 'a_abstention',
        'b_correctness', 'b_hallucination', 'b_abstention',
        'c_correctness', 'c_hallucination', 'c_abstention', 'c_citation'
    ]
    
    for eval_dict in evaluations:
        for field in required_fields:
            if field not in eval_dict:
                print(f"Warning: Question {eval_dict['id']} missing field: {field}")
                return False
    
    return True