#!/bin/bash

# 1. Configuration
LANGUAGES=("as-IN" "bn-IN" "brx-IN" "doi-IN" "gu-IN" "hi-IN" "kn-IN" "kok-IN" "ks-IN" "mai-IN" "ml-IN" "mni-IN" "mr-IN" "ne-IN" "od-IN" "pa-IN" "sa-IN" "sat-IN" "sd-IN" "ta-IN" "te-IN" "ur-IN")
MODELS=("Qwen/Qwen3-0.6B-FC" "meta-llama/Llama-3.2-1B-Instruct-FC")

# Your 17 specific categories
CATEGORIES=("simple_python" "simple_java" "simple_javascript" "parallel" "multiple" "parallel_multiple" "irrelevance" "live_simple" "live_multiple" "live_parallel" "live_parallel_multiple" "live_irrelevance" "live_relevance" "multi_turn_base" "multi_turn_miss_func" "multi_turn_miss_param" "multi_turn_long_context")

BASE_DIR=$(pwd)
DATA_SOURCE_DIR="$BASE_DIR/multilingual_bfcl_data"
REPO_DIR="$BASE_DIR/gorilla/berkeley-function-call-leaderboard"
FINAL_RESULTS="$BASE_DIR/benchmark_results"

mkdir -p "$FINAL_RESULTS"

# 2. Backup English Data
echo "Backing up English data..."
mkdir -p "$REPO_DIR/bfcl_eval/data_backup"
cp "$REPO_DIR/bfcl_eval/data"/*.json "$REPO_DIR/bfcl_eval/data_backup/"

# Function to handle generation and evaluation
execute_benchmark() {
    local CURRENT_LANG=$1
    local CURRENT_MODEL=$2
    
    echo "Running $CURRENT_MODEL for $CURRENT_LANG..."
    cd "$REPO_DIR"
    
    # Generate results for each category
    for CAT in "${CATEGORIES[@]}"; do
        echo "  -> Generating: $CAT"
        bfcl generate --model "$CURRENT_MODEL" --test-category "$CAT" --backend sglang --gpu-memory-utilization 0.5
    done
    
    # Run evaluation
    echo "  -> Scoring results..."
    bfcl evaluate --model "$CURRENT_MODEL"
    
    # Archive results
    SAFE_MODEL=$(echo "$CURRENT_MODEL" | tr '/' '_')
    DEST="$FINAL_RESULTS/$CURRENT_LANG/$SAFE_MODEL"
    mkdir -p "$DEST"
    cp -r ./result/* "$DEST/" 2>/dev/null
    cp -r ./score/* "$DEST/" 2>/dev/null
    
    # Clean up repo folders for next run
    rm -rf ./result/* ./score/*
    cd "$BASE_DIR"
}

# 3. Run English Baseline
echo "================================================"
echo "RUNNING ENGLISH BASELINE"
echo "================================================"
for MODEL in "${MODELS[@]}"; do
    execute_benchmark "English" "$MODEL"
done

# 4. Loop Through Indian Languages
for LANG in "${LANGUAGES[@]}"; do
    echo "================================================"
    echo "PROCESSING LANGUAGE: $LANG"
    echo "================================================"
    
    # Swap files: Clear and copy translated data
    rm "$REPO_DIR/bfcl_eval/data"/*.json
    cp "$DATA_SOURCE_DIR/$LANG"/*.json "$REPO_DIR/bfcl_eval/data/"

    for MODEL in "${MODELS[@]}"; do
        execute_benchmark "$LANG" "$MODEL"
    done
done

# 5. Restore English Data
cp "$REPO_DIR/bfcl_eval/data_backup"/*.json "$REPO_DIR/bfcl_eval/data/"
echo "All 22 languages and baseline completed!"
