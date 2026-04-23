import sys
import json
import argparse
from pathlib import Path
from typing import Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from evaluation.bfcl.dataset import BFCLDataset
from evaluation.bfcl.evaluator import BFCLEvaluator
from evaluation.bfcl.adapter import create_bfcl_adapter


def create_llm_client(config_path: Optional[str] = None):
    from argus.config.manager import ConfigManager
    from argus.llm.llm_client import LLMClient

    cfg_mgr = ConfigManager(config_path) if config_path else ConfigManager()

    class Args:
        def __init__(self):
            self.model = None
            self.api_key = None
            self.base_url = None
            self.permission_mode = "yolo"

    args = Args()
    config = cfg_mgr.resolve_effective_config(args)
    llm_client = LLMClient(config.active_model)
    model = config.active_model.model

    return llm_client, model


def run_bfcl_evaluation(category: str = "simple_python",
    max_samples: int = 5,
    bfcl_data_dir: str | Path | None = None,
    config_path: Optional[str] = None,
    output_dir: str | Path | None = None):
    print("\n" + "="*60)
    print(f"🚀 Argus BFCLmessage")
    print("="*60)

    print(f"\n🤖 messageLLMmessage...")
    try:
        llm_client, model = create_llm_client(config_path)
        if not model:
            print("❌ message")
            return None
        print(f"   LLMmessage: {model}")
    except Exception as e:
        print(f"❌ messageLLMmessage: {e}")
        return None

    print("\n🔧 messageBFCLmessage...")
    bfcl_agent = create_bfcl_adapter(llm_client, model)
    print(f"   message: {bfcl_agent.name}")

    print(f"\n📚 messageBFCLmessage (message)...")
    print(f"   message: {category}")
    print(f"   message: {max_samples if max_samples > 0 else 'message'}")

    dataset = BFCLDataset(bfcl_data_dir=bfcl_data_dir, category=category, auto_download=True)

    if len(dataset) == 0:
        print(f"❌ message,message '{category}' message")
        return None

    print("\n📊 messageBFCLmessage...")
    evaluator = BFCLEvaluator(dataset=dataset, category=category, evaluation_mode="ast")

    print("\n🔄 message...")
    results = evaluator.evaluate(agent=bfcl_agent, max_samples=max_samples if max_samples > 0 else None)

    print("\n" + "="*60)
    print("📊 message")
    print("="*60)
    print(f"message: {results['overall_accuracy']:.2%}")
    print(f"message: {results['correct_samples']}/{results['total_samples']}")

    if results.get('category_metrics'):
        print(f"\nmessage:")
        for cat, metrics in results['category_metrics'].items():
            print(f"  {cat}: {metrics['accuracy']:.2%} ({metrics['correct']}/{metrics['total']})")

    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = project_root / "evaluation" / "bfcl" / "results"

    output_path.mkdir(parents=True, exist_ok=True)
    result_file = output_path / f"BFCL_v4_{category}_result.json"
    evaluator.export_to_bfcl_format(results, result_file)

    detail_file = output_path / f"bfcl_{category}_detailed.json"
    with open(detail_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📄 message: {detail_file}")
    return results


def main():
    parser = argparse.ArgumentParser(description="messageBFCLmessage", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--category", type=str, default="simple_python", choices=BFCLDataset.SUPPORTED_CATEGORIES, help="message")
    parser.add_argument("--samples", type=int, default=5, help="message (0message)")
    parser.add_argument("--data-dir", type=str, default=None, help="BFCLmessage")
    parser.add_argument("--config", type=str, default=None, help="Argusmessage")
    parser.add_argument("--output-dir", type=str, default=None, help="message")
    args = parser.parse_args()

    results = run_bfcl_evaluation(category=args.category,
        max_samples=args.samples,
        bfcl_data_dir=args.data_dir,
        config_path=args.config,
        output_dir=args.output_dir)

    if results:
        print("\n✅ message!")
    else:
        print("\n❌ message!")
        sys.exit(1)


if __name__ == "__main__":
    main()


