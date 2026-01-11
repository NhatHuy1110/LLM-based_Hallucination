"""
Tải và chuẩn bị SQuAD 2.0 dataset
Chạy file này TRƯỚC KHI chạy experiment
"""

import json
import random
import requests
import os


def download_squad():
    """Tải SQuAD 2.0 dev set"""
    print("="*60)
    print("DOWNLOADING SQUAD 2.0 DATASET")
    print("="*60)
    
    filename = 'squad_dev_v2.json'
    
    # Kiểm tra đã tồn tại chưa
    if os.path.exists(filename):
        print(f"✅ File {filename} already exists. Skipping download.")
        return True
    
    print(f"\n📥 Downloading SQuAD 2.0 dev set...")
    print("This may take a few minutes...")
    
    url = "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json"
    
    try:
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded successfully: {filename}")
        print(f"📊 File size: {len(response.content) / 1024 / 1024:.2f} MB")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


def load_squad_data(file_path='squad_dev_v2.json'):
    """Load SQuAD 2.0 JSON data"""
    print(f"\n📂 Loading {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_articles = len(data['data'])
    print(f"✅ Loaded {total_articles} articles")
    
    return data


def extract_all_questions(squad_data):
    """
    Trích xuất TẤT CẢ câu hỏi từ SQuAD 2.0
    """
    questions = []
    
    print("\n🔍 Extracting questions...")
    
    for article in squad_data['data']:
        for paragraph in article['paragraphs']:
            context = paragraph['context']
            
            for qa in paragraph['qas']:
                question_text = qa['question']
                q_id = qa['id']
                is_impossible = qa.get('is_impossible', False)
                
                # Lấy answer
                if is_impossible:
                    gold_answer = "UNANSWERABLE"
                else:
                    if qa['answers']:
                        gold_answer = qa['answers'][0]['text']
                    else:
                        continue
                
                questions.append({
                    'squad_id': q_id,
                    'question': question_text,
                    'evidence': context,
                    'gold_answer': gold_answer,
                    'is_impossible': is_impossible
                })
    
    return questions


def sample_balanced_questions(questions, n_answerable=60, n_unanswerable=40):
    """
    Sample câu hỏi cân bằng
    """
    answerable = [q for q in questions if not q['is_impossible']]
    unanswerable = [q for q in questions if q['is_impossible']]
    
    print(f"\n📊 Available questions in SQuAD 2.0:")
    print(f"  - Answerable: {len(answerable)}")
    print(f"  - Unanswerable: {len(unanswerable)}")
    
    # Sample ngẫu nhiên
    random.seed(42)  # Để reproducible
    
    selected_answerable = random.sample(
        answerable, 
        min(n_answerable, len(answerable))
    )
    
    selected_unanswerable = random.sample(
        unanswerable, 
        min(n_unanswerable, len(unanswerable))
    )
    
    # Gộp lại và shuffle
    dataset = selected_answerable + selected_unanswerable
    random.shuffle(dataset)
    
    # Gán lại ID từ 1-100
    for i, item in enumerate(dataset, 1):
        item['id'] = i
    
    print(f"\n✅ Sampled dataset:")
    print(f"  - Answerable: {len(selected_answerable)}")
    print(f"  - Unanswerable: {len(selected_unanswerable)}")
    print(f"  - Total: {len(dataset)}")
    
    return dataset


def truncate_evidence(text, max_chars=800):
    """
    Rút gọn evidence để không quá dài
    """
    if len(text) <= max_chars:
        return text
    
    # Cắt ở câu gần nhất
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    
    if last_period > max_chars * 0.7:  # Nếu có dấu chấm ở 70% trở lên
        return truncated[:last_period + 1]
    else:
        return truncated + "..."


def prepare_dataset_for_config(dataset):
    """
    Chuẩn bị dataset cho config.py
    """
    formatted = []
    
    for item in dataset:
        formatted.append({
            'id': item['id'],
            'question': item['question'],
            'gold_answer': item['gold_answer'],
            'evidence': truncate_evidence(item['evidence'], max_chars=800)
        })
    
    return formatted


def save_to_json(dataset, filename='squad_100_dataset.json'):
    """
    Lưu dataset ra file JSON
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Dataset saved to: {filename}")


def show_examples(dataset, n=5):
    """
    Hiển thị ví dụ câu hỏi
    """
    print("\n" + "="*60)
    print("EXAMPLE QUESTIONS")
    print("="*60)
    
    for i, q in enumerate(dataset[:n], 1):
        print(f"\n{i}. Question: {q['question']}")
        print(f"   Answer: {q['gold_answer']}")
        print(f"   Type: {'❌ UNANSWERABLE' if q.get('is_impossible') else '✅ ANSWERABLE'}")
        print(f"   Evidence: {q['evidence'][:150]}...")


def main():
    print("\n" + "="*60)
    print("SQUAD 2.0 DATASET PREPARATION")
    print("="*60)
    
    # Bước 1: Tải dataset
    if not download_squad():
        print("\n❌ Cannot proceed without dataset!")
        return
    
    # Bước 2: Load data
    squad_data = load_squad_data()
    
    # Bước 3: Trích xuất tất cả câu hỏi
    all_questions = extract_all_questions(squad_data)
    print(f"✅ Total questions extracted: {len(all_questions)}")
    
    # Bước 4: Sample 100 câu (60 answerable + 40 unanswerable)
    dataset = sample_balanced_questions(
        all_questions,
        n_answerable=60,
        n_unanswerable=40
    )
    
    # Bước 5: Chuẩn bị format cho config
    formatted_dataset = prepare_dataset_for_config(dataset)
    
    # Bước 6: Lưu ra file JSON
    save_to_json(formatted_dataset, 'squad_100_dataset.json')
    
    # Bước 7: Hiển thị ví dụ
    show_examples(formatted_dataset, n=5)
    
    # Thống kê
    print("\n" + "="*60)
    print("DATASET STATISTICS")
    print("="*60)
    
    answerable_count = sum(1 for q in formatted_dataset if q['gold_answer'] != 'UNANSWERABLE')
    unanswerable_count = len(formatted_dataset) - answerable_count
    
    print(f"Total questions: {len(formatted_dataset)}")
    print(f"  ✅ Answerable: {answerable_count} ({answerable_count/len(formatted_dataset)*100:.1f}%)")
    print(f"  ❌ Unanswerable: {unanswerable_count} ({unanswerable_count/len(formatted_dataset)*100:.1f}%)")
    
    # Hướng dẫn tiếp theo
    print("\n" + "="*60)
    print("✅ PREPARATION COMPLETE!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("1. File 'squad_100_dataset.json' has been created")
    print("2. This file will be automatically loaded by config.py")
    print("3. Run: python main.py")
    print("4. Choose option 1 to run experiment")
    print("="*60)


if __name__ == "__main__":
    main()