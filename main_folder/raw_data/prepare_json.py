import json
import os

# Updated BFCL File List
files_to_process = [
    "BFCL_v4_irrelevance.json", "BFCL_v4_live_irrelevance.json", "BFCL_v4_live_multiple.json",
    "BFCL_v4_live_parallel.json", "BFCL_v4_live_parallel_multiple.json", "BFCL_v4_live_relevance.json",
    "BFCL_v4_live_simple.json", "BFCL_v4_memory.json", "BFCL_v4_multiple.json",
    "BFCL_v4_multi_turn_base.json", "BFCL_v4_multi_turn_long_context.json", "BFCL_v4_multi_turn_miss_func.json",
    "BFCL_v4_multi_turn_miss_param.json", "BFCL_v4_parallel.json", "BFCL_v4_parallel_multiple.json",
    "BFCL_v4_simple_java.json", "BFCL_v4_simple_javascript.json", "BFCL_v4_simple_python.json",
    "BFCL_v4_web_search.json"
]

# Complete Language Map
LANGUAGES = {
    "Hindi": "hi-IN", "Kannada": "kn-IN", "Bengali": "bn-IN", "Malayalam": "ml-IN",
    "Tamil": "ta-IN", "Marathi": "mr-IN", "Telugu": "te-IN", "Punjabi": "pa-IN",
    "Gujarati": "gu-IN", "Odia": "od-IN", "Assamese": "as-IN", "Maithili": "mai-IN",
    "Bodo": "brx-IN", "Manipuri": "mni-IN", "Dogri": "doi-IN", "Nepali": "ne-IN",
    "Kashmiri": "ks-IN", "Sanskrit": "sa-IN", "Konkani": "kok-IN", "Santali": "sat-IN",
    "Sindhi": "sd-IN", "Urdu": "ur-IN"
}

OUTPUT_FILE = "gemini_batch_input.jsonl"
batch_requests = []

print("Starting data preparation...")

for file_name in files_to_process:
    if not os.path.exists(file_name):
        continue

    with open(file_name, 'r', encoding='utf-8') as f:
        for line_idx, line in enumerate(f):
            if not line.strip(): continue
            entry = json.loads(line)
            
            # Navigate BFCL nested structure
            questions = entry.get("question", [])
            for q_idx, turn_list in enumerate(questions):
                for msg_idx, message in enumerate(turn_list):
                    if message.get("role") == "user":
                        original_text = message.get("content", "")
                        if not original_text: continue

                        # Generate one request per language
                        for lang_name, lang_code in LANGUAGES.items():
                            # Key: filename|line_idx|q_idx|msg_idx|lang_code
                            request_key = f"{file_name}|{line_idx}|{q_idx}|{msg_idx}|{lang_code}"

                            batch_requests.append({
                                "key": request_key,
                                "request": {
                                    "contents": [{
                                        "role": "user",
                                        "parts": [{
                                            "text": (
                                                f"Translate the following user prompt into {lang_name} ({lang_code}). "
                                                "Guidelines:\n"
                                                "1. Preserve technical terms, function names, and parameters in English.\n"
                                                "2. Return the translation inside a JSON object with the key 'translation'.\n"
                                                f"Prompt: {original_text}"
                                            )
                                        }]
                                    }],
                                    "generation_config": {
                                        "temperature": 0.0,
                                        "response_mime_type": "application/json" # Forces JSON output
                                    }
                                }
                            })

with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
    for req in batch_requests:
        f.write(json.dumps(req, ensure_ascii=False) + "\n")

print(f"Total requests generated: {len(batch_requests)}")
print(f"File saved as: {OUTPUT_FILE}")