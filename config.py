"""
Configuration and Dataset - SQuAD 2.0
"""

import json
import os

# Load dataset từ file JSON (được tạo bởi prepare_squad_dataset.py)
def load_dataset():
    """Load dataset từ file JSON"""
    dataset_file = 'squad_100_dataset.json'
    
    if not os.path.exists(dataset_file):
        print(f"\n❌ ERROR: {dataset_file} not found!")
        print("Please run: python prepare_squad_dataset.py first")
        print("="*60)
        return []
    
    with open(dataset_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

# Load dataset khi import config
DATASET = load_dataset()

# API Settings - Llama via Groq (FREE & FAST)
MODEL = "llama-3.3-70b-versatile"  # Llama 3.3 70B - FREE
# Alternative models:
# "llama-3.1-70b-versatile" - Llama 3.1 70B
# "llama3-70b-8192" - Llama 3 70B
# "llama3-8b-8192" - Llama 3 8B (faster, less accurate)

RATE_LIMIT_DELAY = 1  # seconds between requests

# File paths
RESULTS_FILE = "experiment_results_squad.json"
INTERMEDIATE_FILE = "intermediate_results_squad.json"
EVAL_TEMPLATE_FILE = "evaluation_template_squad.md"
EVAL_RESULTS_FILE = "evaluation_results_squad.md"
ANALYSIS_REPORT_FILE = "analysis_report_squad.md"
RESULTS_TABLE_FILE = "results_table_squad.csv"
RESULTS_CHART_FILE = "results_comparison_squad.png"