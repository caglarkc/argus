# Argus × SWE-bench:English

---

## English, English

* English:Linux / macOS(Windows English WSL2)
* Docker ≥ 20.10
* English Docker Hub(English SWE-bench English)
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
- `sb-cli`:SWE-bench English
- `docker`:Docker Python SDK
- `tqdm`:English
- `datasets`:HuggingFace datasets

---

## English, English(English)

```
Argus/
├─ Dockerfile.argus-agent      # English Argus Agent English
├─ pyproject.toml
├─ uv.lock
├─.python-version             # English Python English(3.12.x)
├─ argus/                      # Argus English
├─ argus_config.example.yaml   # English
└─ evaluation/
   └─ run_evaluation.py        # English(SWE-bench)
```

English:

```
evaluation/
├─ argus_workspace/argus_agent_cache/
│  ├─ Argus/                # English /opt/Argus(English.venv)
│  ├─ uv_bin/uv             # English /root/.local/bin/uv
│  └─ uv_share/uv/...       # English /root/.local/share/uv(English CPython)
└─ results/
   └─ SWE-bench_.../        # English, patch, predictions.json English
```

---

## English, English(English)

English:

```bash
docker build -f Dockerfile.argus-agent -t argus/agent:0.1.
```

English(EnglishArgusEnglish):

```bash
docker build --no-cache -f Dockerfile.argus-agent -t argus/agent:0.1.
```

English:

* `/opt/Argus/.venv`(venv；English python English uv English shim)
* `/root/.local/bin/uv`
* `/root/.local/share/uv`(**English CPython 3.12 + English**)

> English **English apt English python**.uv English `.python-version` English manylinux English CPython 3.12.

---

## English, English

### 1)English(English)

```bash
cd Argus

# English 2 English
python evaluation/run_evaluation.py \
  --config ~/.argus/argus_config.yaml \
  --limit 2 \
  --mode e2e
```

### 2)English

```bash
python evaluation/run_evaluation.py \
  --config ~/.argus/argus_config.yaml \
  --instance-ids django__django-11001 astropy__astropy-12907
```

### 3)English 50 English(English)

```bash
python evaluation/run_evaluation.py \
  --config ~/.argus/argus_config.yaml \
  --limit 50 \
  --max-workers 4 \
  --mode e2e
```

---

## English, English

| English | English | English |
|------|--------|------|
| `--dataset` | `SWE-bench_Lite` | English:`SWE-bench` / `SWE-bench_Lite` / `SWE-bench_Verified` |
| `--config` | `~/.argus/argus_config.yaml` | Argus English |
| `--agent` | `argus` | Agent English:`argus` / `codex` / `claude` |
| `--instance-ids` | - | English ID(English) |
| `--pattern` | - | English ID |
| `--limit` | - | English |
| `--max-workers` | `1` | English |
| `--mode` | `expr` | English(English) |
| `--run-id` | `argus-agent` | English |
| `--force` | `False` | English(English) |

### English

| English | English |
|------|------|
| `expr` | English patch |
| `collect` | English patch English `predictions.json` |
| `e2e` | English patch + English |

### English (English patch English run.log),English:

```bash
# English(English 30 English)
python evaluation/run_evaluation.py --limit 100

# English,English 30 English,English 70 English
python evaluation/run_evaluation.py --limit 100

# English(English)
python evaluation/run_evaluation.py --limit 100 --force
```

---

## English, English `predictions.json` English,English SWE-bench English:

```bash
# English SWE-bench Lite(test English)
sb-cli submit swe-bench_lite test \
    --predictions_path evaluation/results/SWE-bench_SWE-bench_Lite_argus-agent/predictions.json \
    --run_id my_run_name
```

**English**:

| English --dataset | sb-cli English |
|------------------|-------------|
| `SWE-bench_Lite` | `swe-bench_lite test` |
| `SWE-bench_Verified` | `swe-bench_verified test` |
| `SWE-bench` | `swe-bench-m test` |

---

## English, English(English)

1. **English**:English uv English `.python-version` English **CPython 3.12(manylinux English)**,English `.venv` English.
2. **English**:English `/opt/Argus`, `/root/.local/bin/uv`, `/root/.local/share/uv` English `argus_agent_cache/`.
3. **English**:English SWE English；English **`/opt/Argus/.venv/bin/argus...`** English(English `source activate`).
4. `.venv/bin/python` English uv English **shim**,English `~/.local/share/uv/python/.../bin/python`,English Python/`libpython3.12.so`.

---

## English, English(English)

English SWE English Argus,English:

```bash
docker run --rm -it \
  -v "$(pwd)/argus_workspace/argus_agent_cache/Argus":/opt/Argus:ro \
  -v "$(pwd)/argus_workspace/argus_agent_cache/uv_bin":/root/.local/bin:ro \
  -v "$(pwd)/argus_workspace/argus_agent_cache/uv_share":/root/.local/share:ro \
  -v "$(pwd)/results/demo":/results:rw \
  --workdir /testbed \
  swebench/sweb.eval.x86_64.<instance_id>:latest \
  bash

# English:
/opt/Argus/.venv/bin/argus --config /results/argus_config.yaml --agent argus --permission-mode yolo
```

---

## English, English

```bash
# English(English)
rm -rf argus_workspace/argus_agent_cache

# English
rm -rf results
```
