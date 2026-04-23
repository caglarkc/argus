# Argus × BFCL:English

---

## English, English

* English:Linux / macOS / Windows
* Python ≥ 3.11
* Git(English)
* English **Argus English** `argus_config.yaml`

  English `--config` English,English `~/.argus/argus_config.yaml`

---

## English, English:

```bash
# English uv(English)
uv sync --extra evaluation

# English pip
pip install -e ".[evaluation]"
```

English:
- `datasets`:HuggingFace datasets(English)
- `tqdm`:English

---

## English, English

```
Argus/
├─ argus/                      # Argus English
├─ argus_config.example.yaml   # English
└─ evaluation/
   └─ bfcl/
      ├─ run_bfcl_evaluation.py  # English
      ├─ dataset.py              # English
      ├─ evaluator.py            # English
      ├─ adapter.py              # LLM English
      ├─ gorilla/                # English BFCL English(English)
      └─ results/                # English
```

---

## English, English

### 1)English(English)

```bash
cd Argus

# English 5 English
python evaluation/bfcl/run_bfcl_evaluation.py \
  --category simple_python \
  --samples 5 \
  --config ~/.argus/argus_config.yaml
```

### 2)English

```bash
python evaluation/bfcl/run_bfcl_evaluation.py \
  --category simple_python \
  --samples 0 \
  --config ~/.argus/argus_config.yaml
```

### 3)English

```bash
# English(English)
for category in simple_python multiple parallel; do
  python evaluation/bfcl/run_bfcl_evaluation.py \
    --category $category \
    --samples 10 \
    --config ~/.argus/argus_config.yaml
done
```

---

## English, English

| English | English | English |
|------|--------|------|
| `--category` | `simple_python` | English(English) |
| `--samples` | `5` | English(`0` English) |
| `--data-dir` | - | BFCL English(English) |
| `--config` | `~/.argus/argus_config.yaml` | Argus English |
| `--output-dir` | `evaluation/bfcl/results` | English |

### English

| English | English |
|------|------|
| `simple_python` | English Python English |
| `multiple` | English |
| `parallel` | English |
| `parallel_multiple` | English |
| `java` | Java English |
| `javascript` | JavaScript English |
| `live_simple` | English API English |
| `live_multiple` | English API English |
| `live_parallel` | English API English |
| `live_parallel_multiple` | English API English |
| `live_relevance` | English API English |
| `live_irrelevance` | English API English |
| `irrelevance` | English |
| `multi_turn_base` | English |
| `multi_turn_miss_func` | English |
| `multi_turn_miss_param` | English |
| `multi_turn_long_context` | English |

---

## English, English:

### 1. English JSON

English:`bfcl_{category}_detailed.json`

English,English:

```json
{
  "total_samples": 10,
  "correct_samples": 8,
  "overall_accuracy": 0.8,
  "category_metrics": {
    "simple_python": {
      "total": 10,
      "correct": 8,
      "accuracy": 0.8
    }
  },
  "results": [
    {
      "sample_id": "sample_1",
      "category": "simple_python",
      "correct": true,
      "model_output": "math.factorial(5)",
      "expected": ["math.factorial(5)"],
      "latency_ms": 1234.56
    }
  ]
}
```

### 2. BFCL English:`BFCL_v4_{category}_result.json`

English BFCL English,English:

```json
[
  {
    "id": "sample_1",
    "result": "math.factorial(5)",
    "correct": true
  }
]
```

---

## English, English:

| English | English | English |
|------|------|----------|
| `ast` | English Python AST English | English,English |
| `exact` | English | English |

English AST English,English:
- English(English, JSON, English)
- English
- English,English:

```python
from evaluation.bfcl.evaluator import BFCLEvaluator

evaluator = BFCLEvaluator(dataset=dataset,
    category="simple_python",
    evaluation_mode="ast"  # English "exact")
```

---

## English, English(English)

1. **English**:English GitHub English BFCL English(English sparse checkout,English)
2. **LLM English**:English Argus English LLMClient English BFCL English
3. **English**:English AST English
4. **English**:English, English,English BFCL English

---

## English, English,English:

```python
from evaluation.bfcl.run_bfcl_evaluation import run_bfcl_evaluation

# English
results = run_bfcl_evaluation(category="simple_python",
    max_samples=10,
    config_path="~/.argus/argus_config.yaml",
    output_dir="./results")

# English
print(f"English: {results['overall_accuracy']:.2%}")
print(f"English: {results['correct_samples']}/{results['total_samples']}")
```

### English API

```python
from evaluation.bfcl.dataset import BFCLDataset
from evaluation.bfcl.evaluator import BFCLEvaluator
from evaluation.bfcl.adapter import create_bfcl_adapter
from argus.llm.llm_client import LLMClient
from argus.config.manager import ConfigManager

# English LLM English
config = ConfigManager().resolve_effective_config(None)
llm_client = LLMClient(config.active_model)

# English
adapter = create_bfcl_adapter(llm_client, config.active_model.model)

# English
dataset = BFCLDataset(category="simple_python", auto_download=True)

# English
evaluator = BFCLEvaluator(dataset=dataset, category="simple_python")

# English
results = evaluator.evaluate(agent=adapter, max_samples=10)
```

---

## English, English

### Q: English？

A: English git,English GitHub.English:

```bash
cd evaluation/bfcl
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/ShishirPatil/gorilla.git gorilla

cd gorilla
git sparse-checkout set berkeley-function-call-leaderboard/bfcl_eval/data
```

### Q: English？

A: 
1. English(`--config` English)
2. English(AST vs English)
3. English JSON English `model_output` English `expected` English
4. English

### Q: English？

A: English:

```bash
for category in simple_python multiple parallel java javascript; do
  python evaluation/bfcl/run_bfcl_evaluation.py \
    --category $category \
    --samples 0 \
    --config ~/.argus/argus_config.yaml
done
```

---

## English, English

```bash
# English(English)
rm -rf evaluation/bfcl/gorilla

# English
rm -rf evaluation/bfcl/results
```

---

## English

- [Berkeley Function Call Leaderboard](https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard)
- [Argus English](../README.md)
