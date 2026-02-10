

# LLM Indic-Eval: Multilingual Function Calling Benchmark

This repository contains the experimental framework and analysis for evaluating the function-calling capabilities of Large Language Models (LLMs) across 22 Indian languages. The project utilizes the **Berkeley Function Calling Leaderboard (BFCL)** as a base and extends it to the Indic multilingual context via the **Gemini Batch API**.

## Repository Structure

The project is organized into the following directory structure:

* **`main_folder/raw_data`**: Contains `prepare_json.py`, which is used for formatting BFCL English prompts into JSONL files compatible with the Gemini Batch API for translation.
* **`main_folder/translated_data`**: Contains `extract.py`, which processes the raw outputs from Gemini Batch predictions to reconstruct structured prompt files for the evaluation suite.
* **`main_folder/analysis`**: A suite of Python scripts for post-evaluation data processing:
* `1_offset_analysis.py`: Calculates the performance delta between English and Indic language results.
* `2_resource_tier_analysis.py`: Correlates accuracy with language resource availability (High/Mid/Low tiers).
* `3_linguistic_family_analysis.py`: Evaluates cross-lingual transfer across Indo-Aryan and Dravidian families.
* `4_category_analysis.py`: Breaks down performance by task complexity (Simple, Parallel, Multi-turn).


* **`evaluation_script.sh`**: The core shell script that orchestrates the execution of the BFCL benchmark using the **SGLang** backend.

## Workflow Execution

### 1. Data Preparation and Translation

To translate the benchmark prompts, first prepare the input payloads:

```bash
python main_folder/raw_data/prepare_json.py

```

After processing through the Gemini Batch API, extract the results:

```bash
python main_folder/translated_data/extract.py

```

### 2. Running Evaluations

The evaluation is automated via the main shell script. This script handles prompt injection, model generation via SGLang, and accuracy computation:

```bash
bash evaluation_script.sh

```

### 3. Result Analysis

Once the evaluation logs are generated, the analysis scripts can be run to visualize the results:

```bash
python main_folder/analysis/1_offset_analysis.py
# Followed by 2_resource_tier_analysis.py, 3_linguistic_family_analysis.py, etc.

```

