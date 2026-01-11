"""
Main entry point for the hallucination experiment with SQuAD 2.0
"""

import sys
import os
from config import DATASET, EVAL_TEMPLATE_FILE, RESULTS_FILE, INTERMEDIATE_FILE, MODEL
from experiment import run_experiment, create_evaluation_template
from analysis import run_analysis


def main():
    print("="*60)
    print("LLM HALLUCINATION EXPERIMENT")
    print("SQuAD 2.0 Dataset")
    print("="*60)
    print()
    print(f"Using: {MODEL} via Groq (FREE & FAST)")
    print()
    print("This experiment tests 3 conditions:")
    print("  A: No Context (baseline)")
    print("  B: Evidence-grounded")
    print("  C: Evidence-grounded + Self-verification")
    print()
    print("="*60)
    
    # Kiểm tra dataset đã load chưa
    if not DATASET:
        print("\n❌ ERROR: Dataset not loaded!")
        print("Please run: python prepare_squad_dataset.py first")
        print("="*60)
        sys.exit(1)
    
    print("\nSelect mode:")
    print("1. Run experiment (collect LLM responses)")
    print("2. Analyze results (after manual evaluation)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_experiment_mode()
    elif choice == "2":
        run_analysis_mode()
    elif choice == "3":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice. Please run again.")
        sys.exit(1)


def run_experiment_mode():
    """Mode 1: Run the experiment"""
    print("\n" + "="*60)
    print("MODE 1: RUN EXPERIMENT")
    print("="*60)
    
    print("\n🔑 HOW TO GET FREE GROQ API KEY:")
    print("-" * 60)
    print("1. Go to: https://console.groq.com/keys")
    print("2. Sign up/Login (free account)")
    print("3. Click 'Create API Key'")
    print("4. Name: 'llama-squad-experiment'")
    print("5. Copy the key (starts with 'gsk_...')")
    print()
    print("⚡ Groq is FREE and SUPER FAST!")
    print("📊 Free tier: 14,400 requests/day")
    print("-" * 60)
    print()
    
    # Get API key
    api_key = input("Enter your Groq API key: ").strip()
    
    if not api_key:
        print("\n❌ Error: API key is required!")
        sys.exit(1)
    
    if not api_key.startswith("gsk_"):
        print("\n⚠️  Warning: Groq API key should start with 'gsk_'")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            sys.exit(0)
    
    # Confirm
    print(f"\n{'='*60}")
    print("EXPERIMENT DETAILS:")
    print(f"{'='*60}")
    print(f"Model: {MODEL}")
    print(f"Dataset: SQuAD 2.0 (100 questions)")
    
    answerable = sum(1 for q in DATASET if q['gold_answer'] != 'UNANSWERABLE')
    unanswerable = len(DATASET) - answerable
    
    print(f"  ✅ Answerable: {answerable}")
    print(f"  ❌ Unanswerable: {unanswerable}")
    print(f"Conditions: 3 (A, B, C)")
    print(f"Total API calls: {len(DATASET) * 3} calls")
    print(f"Estimated time: ~{len(DATASET) * 3 * 2 // 60} minutes")
    print(f"Cost: FREE ✓")
    print(f"{'='*60}")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Run experiment
    print("\n🚀 Starting experiment...\n")
    try:
        results = run_experiment(api_key)
        
        if not results:
            print("\n❌ Experiment failed - no results generated")
            sys.exit(1)
        
        # Create evaluation template
        create_evaluation_template(results, EVAL_TEMPLATE_FILE)
        
        print("\n" + "="*60)
        print("✅ EXPERIMENT COMPLETED!")
        print("="*60)
        print("\n📋 NEXT STEPS:")
        print("-" * 60)
        print(f"1. Open file: '{EVAL_TEMPLATE_FILE}'")
        print("2. For each question, fill in scores (0 or 1)")
        print("   - For UNANSWERABLE questions:")
        print("     * Correctness=1 if model refused")
        print("     * Hallucination=1 if model answered")
        print("     * Abstention=1 if model refused")
        print("   - For ANSWERABLE questions:")
        print("     * Correctness=1 if answer matches gold")
        print("     * Hallucination=1 if invented info")
        print("     * Abstention=1 if refused unnecessarily")
        print("3. Save the file")
        print("4. Run: python main.py → Choose Mode 2")
        print("-" * 60)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Experiment interrupted by user")
        print(f"Partial results saved in: {INTERMEDIATE_FILE}")
    except Exception as e:
        print(f"\n\n❌ Error during experiment: {e}")
        print(f"Check {INTERMEDIATE_FILE} for partial results")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_analysis_mode():
    """Mode 2: Analyze results"""
    print("\n" + "="*60)
    print("MODE 2: ANALYZE RESULTS")
    print("="*60)
    
    # Check if files exist
    if not os.path.exists(RESULTS_FILE):
        print(f"\n❌ Error: Results file not found: {RESULTS_FILE}")
        print("Please run Mode 1 first!")
        sys.exit(1)
    
    # Ask for evaluation file
    print(f"\nDefault evaluation file: {EVAL_TEMPLATE_FILE}")
    custom = input(f"Use different file? (press Enter for default, or type filename): ").strip()
    eval_file = custom if custom else EVAL_TEMPLATE_FILE
    
    if not os.path.exists(eval_file):
        print(f"\n❌ Error: Evaluation file not found: {eval_file}")
        sys.exit(1)
    
    # Run analysis
    print("\n📊 Running analysis...\n")
    try:
        run_analysis(RESULTS_FILE, eval_file)
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE!")
        print("="*60)
        print("\n📈 OUTPUT FILES:")
        print("-" * 60)
        print("1. results_table_squad.csv - Metrics comparison")
        print("2. results_comparison_squad.png - Visualizations")
        print("3. analysis_report_squad.md - Full report")
        print("-" * 60)
        print("\n💡 Open these files to see your results!")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()