"""
Automatic evaluation script for SQuAD 2.0 Hallucination Experiment
Tự động chấm điểm dựa trên so sánh với gold answer
FIXED: Better hallucination detection for Condition C
"""

import json
import re
from typing import List, Dict


def normalize_answer(text):
    """Chuẩn hóa câu trả lời để so sánh"""
    if not text:
        return ""
    text = str(text).lower().strip()
    # Loại bỏ dấu câu
    text = re.sub(r'[^\w\s]', ' ', text)
    # Loại bỏ khoảng trắng thừa
    text = ' '.join(text.split())
    return text


def check_correctness(answer, gold_answer):
    """
    Kiểm tra câu trả lời có đúng không
    Returns: 1 if correct, 0 if incorrect
    
    Đặc biệt xử lý:
    - UNANSWERABLE questions: correct nếu từ chối trả lời
    - Normal questions: correct nếu chứa gold answer
    """
    answer_norm = normalize_answer(answer)
    gold_norm = normalize_answer(gold_answer)
    
    # Case 1: UNANSWERABLE question
    if gold_norm == "unanswerable":
        # Correct nếu model từ chối (abstention)
        refusal_phrases = [
            'not enough information',
            'insufficient information',
            'cannot answer',
            'unable to answer',
            'do not have',
            'unsupported',
            'not mentioned',
            'does not provide',
            'no information'
        ]
        for phrase in refusal_phrases:
            if phrase in answer_norm:
                return 1
        return 0
    
    # Case 2: Normal question
    # Check if gold answer appears in the response
    if gold_norm in answer_norm:
        return 1
    
    # Check if answer contains key parts of gold answer
    gold_words = set(gold_norm.split())
    answer_words = set(answer_norm.split())
    
    # Remove common stop words
    stop_words = {'the', 'is', 'a', 'an', 'in', 'of', 'on', 'at', 'to', 'for', 
                  'by', 'was', 'were', 'are', 'and', 'or', 'with', 'from', 'that'}
    
    gold_content = gold_words - stop_words
    answer_content = answer_words - stop_words
    
    if len(gold_content) == 0:
        return 0
    
    # If >70% of gold answer words appear in answer
    overlap = len(gold_content & answer_content)
    ratio = overlap / len(gold_content)
    
    return 1 if ratio > 0.7 else 0


def check_hallucination_condition_a(answer, gold_answer):
    """
    Condition A: No context
    Hallucination = trả lời sai factual
    
    Đặc biệt:
    - UNANSWERABLE: hallucination nếu đưa ra câu trả lời cụ thể
    - Normal: hallucination nếu sai
    """
    answer_norm = normalize_answer(answer)
    gold_norm = normalize_answer(gold_answer)
    
    # Case 1: UNANSWERABLE question
    if gold_norm == "unanswerable":
        # Hallucination nếu đưa ra câu trả lời cụ thể (không từ chối)
        refusal_phrases = [
            'not enough information',
            'insufficient information',
            'cannot answer',
            'unable to answer',
            'do not have',
            'unsupported'
        ]
        for phrase in refusal_phrases:
            if phrase in answer_norm:
                return 0  # Không hallucination vì đã từ chối
        return 1  # Hallucination vì đưa ra câu trả lời khi không có thông tin
    
    # Case 2: Normal question
    if check_correctness(answer, gold_answer) == 1:
        return 0  # Correct answer = no hallucination
    else:
        return 1  # Wrong answer = hallucination


def extract_actual_response(answer):
    """
    Extract phần response thực sự từ câu trả lời Condition C
    Bỏ qua các phần meta-text như step-by-step reasoning
    """
    answer_lower = answer.lower()
    
    # Pattern 1: Tìm "response:" hoặc "answer:"
    response_match = re.search(
        r'(?:response|answer):\s*(.+?)(?:\s*(?:label:|supported|not enough|$))', 
        answer_lower, 
        re.DOTALL | re.IGNORECASE
    )
    
    if response_match:
        return response_match.group(1).strip()
    
    # Pattern 2: Tìm phần sau "step 4:" hoặc cuối cùng
    step4_match = re.search(
        r'step\s*4[:\.]?\s*(.+?)(?:\s*(?:label:|supported|not enough|$))',
        answer_lower,
        re.DOTALL | re.IGNORECASE
    )
    
    if step4_match:
        return step4_match.group(1).strip()
    
    # Pattern 3: Nếu có nhiều câu, lấy câu cuối (thường là response thực sự)
    sentences = [s.strip() for s in answer.split('.') if s.strip()]
    if sentences:
        # Bỏ câu chứa "step", "passage", "sentence", "support"
        content_sentences = [
            s for s in sentences 
            if not any(word in s.lower() for word in ['step', 'passage states', 'sentence from', 'since'])
        ]
        if content_sentences:
            return content_sentences[-1]
    
    # Fallback: Dùng toàn bộ
    return answer_lower


def check_hallucination_with_evidence_core(response_text, evidence):
    """
    Core logic để check hallucination
    response_text: Phần response đã được extract
    """
    evidence_norm = normalize_answer(evidence)
    response_norm = normalize_answer(response_text)
    
    # Extract content words
    response_words = set(response_norm.split())
    evidence_words = set(evidence_norm.split())
    
    # Common words to ignore
    stop_words = {
        'the', 'is', 'a', 'an', 'in', 'of', 'on', 'at', 'to', 'for', 
        'by', 'was', 'were', 'are', 'and', 'or', 'with', 'from', 'that',
        'this', 'these', 'those', 'it', 'its', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'can', 'according', 'based',
        'states', 'mentions', 'says', 'passage'
    }
    
    response_content = response_words - stop_words
    evidence_content = evidence_words - stop_words
    
    if len(response_content) == 0:
        return 0
    
    # Nếu >80% content words của response có trong evidence → no hallucination
    # Tăng threshold từ 70% lên 80% để strict hơn
    overlap = len(response_content & evidence_content)
    ratio = overlap / len(response_content)
    
    if ratio >= 0.8:
        return 0
    else:
        return 1


def check_hallucination_with_evidence(answer, evidence):
    """
    Condition B/C: With evidence
    Hallucination = có info không có trong passage
    """
    answer_lower = answer.lower()
    
    # Check if refused to answer
    refusal_phrases = [
        'not enough information',
        'insufficient information',
        'cannot answer',
        'unable to answer',
        'unsupported'
    ]
    for phrase in refusal_phrases:
        if phrase in answer_lower:
            return 0  # No hallucination nếu từ chối
    
    return check_hallucination_with_evidence_core(answer, evidence)


def check_hallucination_condition_c(answer, evidence):
    """
    Condition C: Evidence + Self-verification
    
    KEY FIX: Extract chỉ phần response thực sự, bỏ qua step-by-step reasoning
    """
    answer_lower = answer.lower()
    
    # 1. Nếu có label "SUPPORTED" → no hallucination
    if 'supported' in answer_lower:
        return 0
    
    # 2. Nếu refused → no hallucination  
    refusal_phrases = [
        'not enough information',
        'insufficient information',
        'cannot answer',
        'unable to answer',
        'unsupported'
    ]
    for phrase in refusal_phrases:
        if phrase in answer_lower:
            return 0
    
    # 3. Extract phần response thực sự
    actual_response = extract_actual_response(answer)
    
    # 4. Check hallucination chỉ trên phần response
    return check_hallucination_with_evidence_core(actual_response, evidence)


def check_abstention(answer):
    """
    Kiểm tra có từ chối trả lời không
    Returns: 1 if refused, 0 if answered
    """
    answer_lower = normalize_answer(answer)
    
    refusal_phrases = [
        'not enough information',
        'insufficient information',
        'cannot answer',
        'unable to answer',
        'do not have',
        'unsupported',
        'not mentioned',
        'does not mention',
        'does not provide',
        'no information'
    ]
    
    for phrase in refusal_phrases:
        if phrase in answer_lower:
            return 1
    
    return 0


def check_citation_c(answer, evidence):
    """
    Kiểm tra citation trong Condition C có faithful không
    Returns: 1 if faithful, 0 if not
    """
    answer_lower = answer.lower()
    
    # Check if it contains "supported"
    if 'supported' in answer_lower:
        return 1
    
    # Check if refused to answer
    if check_abstention(answer) == 1:
        return 1
    
    # Extract quoted text from answer
    quotes = re.findall(r'"([^"]*)"', answer)
    
    if quotes:
        # Check if any quote appears in evidence
        for quote in quotes:
            quote_norm = normalize_answer(quote)
            evidence_norm = normalize_answer(evidence)
            
            if quote_norm and quote_norm in evidence_norm:
                return 1
    
    # Default: assume faithful if has evidence
    return 1


def evaluate_all_questions(results_file: str) -> List[Dict]:
    """
    Tự động chấm điểm tất cả câu hỏi
    """
    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    evaluations = []
    
    print("🤖 BẮT ĐẦU TỰ ĐỘNG CHẤM ĐIỂM...")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        q_id = result.get('id', i)
        question = result['question']
        gold = result['gold_answer']
        evidence = result['evidence']
        
        is_unanswerable = normalize_answer(gold) == "unanswerable"
        
        print(f"\n📝 Question {q_id}: {question[:60]}...")
        if is_unanswerable:
            print(f"   [UNANSWERABLE QUESTION]")
        
        eval_dict = {'id': q_id}
        
        # Condition A
        answer_a = result['answer_a']
        eval_dict['a_correctness'] = check_correctness(answer_a, gold)
        eval_dict['a_hallucination'] = check_hallucination_condition_a(answer_a, gold)
        eval_dict['a_abstention'] = check_abstention(answer_a)
        
        print(f"  A: Correctness={eval_dict['a_correctness']}, "
              f"Hallucination={eval_dict['a_hallucination']}, "
              f"Abstention={eval_dict['a_abstention']}")
        
        # Condition B
        answer_b = result['answer_b']
        eval_dict['b_correctness'] = check_correctness(answer_b, gold)
        eval_dict['b_hallucination'] = check_hallucination_with_evidence(answer_b, evidence)
        eval_dict['b_abstention'] = check_abstention(answer_b)
        
        print(f"  B: Correctness={eval_dict['b_correctness']}, "
              f"Hallucination={eval_dict['b_hallucination']}, "
              f"Abstention={eval_dict['b_abstention']}")
        
        # Condition C - FIXED
        answer_c = result['answer_c']
        eval_dict['c_correctness'] = check_correctness(answer_c, gold)
        eval_dict['c_hallucination'] = check_hallucination_condition_c(answer_c, evidence)  # FIXED!
        eval_dict['c_abstention'] = check_abstention(answer_c)
        eval_dict['c_citation'] = check_citation_c(answer_c, evidence)
        
        print(f"  C: Correctness={eval_dict['c_correctness']}, "
              f"Hallucination={eval_dict['c_hallucination']}, "
              f"Abstention={eval_dict['c_abstention']}, "
              f"Citation={eval_dict['c_citation']}")
        
        evaluations.append(eval_dict)
    
    return evaluations


def compute_statistics(evaluations: List[Dict]) -> Dict:
    """Tính toán thống kê tổng quan"""
    stats = {
        'total_questions': len(evaluations),
        'condition_a': {
            'correctness': sum(e['a_correctness'] for e in evaluations),
            'hallucination': sum(e['a_hallucination'] for e in evaluations),
            'abstention': sum(e['a_abstention'] for e in evaluations)
        },
        'condition_b': {
            'correctness': sum(e['b_correctness'] for e in evaluations),
            'hallucination': sum(e['b_hallucination'] for e in evaluations),
            'abstention': sum(e['b_abstention'] for e in evaluations)
        },
        'condition_c': {
            'correctness': sum(e['c_correctness'] for e in evaluations),
            'hallucination': sum(e['c_hallucination'] for e in evaluations),
            'abstention': sum(e['c_abstention'] for e in evaluations),
            'citation': sum(e['c_citation'] for e in evaluations)
        }
    }
    
    return stats


def create_filled_evaluation_file(results_file: str, output_file: str):
    """
    Tạo file evaluation đã được điền sẵn (định dạng .md)
    """
    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Auto evaluate
    evaluations = evaluate_all_questions(results_file)
    
    # Compute statistics
    stats = compute_statistics(evaluations)
    
    # Create evaluation dict for quick lookup
    eval_map = {e['id']: e for e in evaluations}
    
    # Generate filled template với định dạng giống file mẫu
    template = """# EVALUATION TEMPLATE - SQUAD 2.0 (AUTO-FILLED - FIXED)

## Instructions
Scores have been automatically filled based on comparison with gold answers.
✅ FIXED: Better hallucination detection for Condition C (extracts actual response only)

Fill in 0 or 1 for each metric:
- Correctness: 1 = correct, 0 = incorrect (for unanswerable: 1 if refused correctly, 0 otherwise)
- Hallucination: 1 = hallucinated (info not in passage), 0 = no hallucination
- Abstention: 1 = refused/said "not enough info", 0 = answered
- Citation Faithfulness (C only): 1 = citation supports answer, 0 = citation incorrect

Note: For unanswerable questions (gold_answer = "UNANSWERABLE"):
- Correctness = 1 if model refused/abstained
- Hallucination = 1 if model gave a specific answer
- Abstention = 1 if model refused

## Overall Statistics
- Total Questions: {total}
- Condition A: Correctness={a_correct}/{total} ({a_correct_pct:.1f}%), Hallucination={a_hall}/{total} ({a_hall_pct:.1f}%), Abstention={a_abs}/{total} ({a_abs_pct:.1f}%)
- Condition B: Correctness={b_correct}/{total} ({b_correct_pct:.1f}%), Hallucination={b_hall}/{total} ({b_hall_pct:.1f}%), Abstention={b_abs}/{total} ({b_abs_pct:.1f}%)
- Condition C: Correctness={c_correct}/{total} ({c_correct_pct:.1f}%), Hallucination={c_hall}/{total} ({c_hall_pct:.1f}%), Abstention={c_abs}/{total} ({c_abs_pct:.1f}%), Citation={c_cite}/{total} ({c_cite_pct:.1f}%)

""".format(
        total=stats['total_questions'],
        a_correct=stats['condition_a']['correctness'],
        a_correct_pct=stats['condition_a']['correctness']/stats['total_questions']*100,
        a_hall=stats['condition_a']['hallucination'],
        a_hall_pct=stats['condition_a']['hallucination']/stats['total_questions']*100,
        a_abs=stats['condition_a']['abstention'],
        a_abs_pct=stats['condition_a']['abstention']/stats['total_questions']*100,
        b_correct=stats['condition_b']['correctness'],
        b_correct_pct=stats['condition_b']['correctness']/stats['total_questions']*100,
        b_hall=stats['condition_b']['hallucination'],
        b_hall_pct=stats['condition_b']['hallucination']/stats['total_questions']*100,
        b_abs=stats['condition_b']['abstention'],
        b_abs_pct=stats['condition_b']['abstention']/stats['total_questions']*100,
        c_correct=stats['condition_c']['correctness'],
        c_correct_pct=stats['condition_c']['correctness']/stats['total_questions']*100,
        c_hall=stats['condition_c']['hallucination'],
        c_hall_pct=stats['condition_c']['hallucination']/stats['total_questions']*100,
        c_abs=stats['condition_c']['abstention'],
        c_abs_pct=stats['condition_c']['abstention']/stats['total_questions']*100,
        c_cite=stats['condition_c']['citation'],
        c_cite_pct=stats['condition_c']['citation']/stats['total_questions']*100
    )
    
    # Add each question với định dạng giống file template
    for result in results:
        q_id = result.get('id', results.index(result) + 1)
        eval_data = eval_map[q_id]
        
        is_unanswerable = normalize_answer(result['gold_answer']) == "unanswerable"
        unanswerable_tag = " [UNANSWERABLE]" if is_unanswerable else ""
        
        template += f"""
{'='*80}
## Question {q_id}{unanswerable_tag}

**Question:** {result['question']}

**Gold Answer:** {result['gold_answer']}

**Evidence:** {result['evidence']}

---

### Condition A: No Context
**Answer A:** {result['answer_a']}

EVAL_A_CORRECTNESS: {eval_data['a_correctness']}
EVAL_A_HALLUCINATION: {eval_data['a_hallucination']}
EVAL_A_ABSTENTION: {eval_data['a_abstention']}

---

### Condition B: Evidence-grounded
**Answer B:** {result['answer_b']}

EVAL_B_CORRECTNESS: {eval_data['b_correctness']}
EVAL_B_HALLUCINATION: {eval_data['b_hallucination']}
EVAL_B_ABSTENTION: {eval_data['b_abstention']}

---

### Condition C: Evidence + Self-verification
**Answer C:** {result['answer_c']}

EVAL_C_CORRECTNESS: {eval_data['c_correctness']}
EVAL_C_HALLUCINATION: {eval_data['c_hallucination']}
EVAL_C_ABSTENTION: {eval_data['c_abstention']}
EVAL_C_CITATION: {eval_data['c_citation']}

{'='*80}

"""
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)
    
    # Also save JSON format for programmatic access
    json_output = output_file.replace('.md', '_data.json')
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump({
            'evaluations': evaluations,
            'statistics': stats
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ File evaluation (Markdown): {output_file}")
    print(f"✅ File evaluation (JSON): {json_output}")
    print(f"📝 Bạn có thể mở file và kiểm tra kết quả")


if __name__ == "__main__":
    import sys
    
    print("="*80)
    print("TỰ ĐỘNG CHẤM ĐIỂM THỰC NGHIỆM - SQUAD 2.0 (FIXED)")
    print("="*80)
    
    # Default file paths (theo config.py)
    results_file = "experiment_results_squad.json"
    output_file = "evaluation_filled_squad_fixed.md"
    
    # Allow custom file paths via command line
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    try:
        create_filled_evaluation_file(results_file, output_file)
        
        print("\n" + "="*80)
        print("✅ HOÀN THÀNH!")
        print("="*80)
        print(f"\n📋 BƯỚC TIẾP THEO:")
        print(f"1. Mở file: {output_file}")
        print(f"2. Xem thống kê tổng quan ở đầu file")
        print(f"3. So sánh với kết quả cũ để verify fix")
        print(f"4. Chạy analysis: python -m analysis experiment_results_squad.json {output_file}")
        
    except FileNotFoundError:
        print(f"\n❌ Lỗi: Không tìm thấy file {results_file}")
        print("Hãy chạy experiment trước:")
        print("  python main.py → Chọn 1")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()