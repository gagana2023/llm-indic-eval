import json
import os
import re
from collections import defaultdict

# --- CONFIGURATION ---
RESULT_FILE = "Translate Batch Input Predictions Jan 2 2026.jsonl"
OUTPUT_DIR = "multilingual_bfcl_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LANGUAGES = {
    "Hindi": "hi-IN", "Kannada": "kn-IN", "Bengali": "bn-IN", "Malayalam": "ml-IN",
    "Tamil": "ta-IN", "Marathi": "mr-IN", "Telugu": "te-IN", "Punjabi": "pa-IN",
    "Gujarati": "gu-IN", "Odia": "od-IN", "Assamese": "as-IN", "Maithili": "mai-IN",
    "Bodo": "brx-IN", "Manipuri": "mni-IN", "Dogri": "doi-IN", "Nepali": "ne-IN",
    "Kashmiri": "ks-IN", "Sanskrit": "sa-IN", "Konkani": "kok-IN", "Santali": "sat-IN",
    "Sindhi": "sd-IN", "Urdu": "ur-IN"
}

translations_map = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

def clean_and_parse_json(raw_text):
    """Attempt multiple ways to extract the translation from messy LLM output."""
    # 1. Clean markdown and whitespace
    clean_text = re.sub(r'^```json\s*', '', raw_text.strip())
    clean_text = re.sub(r'\s*```$', '', clean_text)
    
    # 2. Try standard parsing with strict=False (handles raw newlines/tabs)
    try:
        data = json.loads(clean_text, strict=False)
        return data.get("translation", "")
    except Exception:
        pass

    # 3. Fallback: Regex to find whatever is inside the "translation" key
    # This looks for: "translation": " <captured_text> "
    regex_pattern = r'"translation":\s*"(.*?)"\s*\}'
    match = re.search(regex_pattern, clean_text, re.DOTALL)
    if match:
        return match.group(1).replace('\\"', '"').replace('\\n', '\n')

    return None

print(f"Reading results from {RESULT_FILE}...")

success_count = 0
fail_count = 0

with open(RESULT_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        
        try:
            res = json.loads(line)
            key_parts = res['key'].split('|')
            fname, line_idx, q_idx, msg_idx, lang_code = key_parts
            
            raw_response_text = res['response']['candidates'][0]['content']['parts'][0]['text']
            
            translated_text = clean_and_parse_json(raw_response_text)
            
            if translated_text:
                translations_map[fname][lang_code][int(line_idx)][int(q_idx)][int(msg_idx)] = translated_text
                success_count += 1
            else:
                print(f"❌ Extraction Failed: {res['key']}")
                fail_count += 1
                
        except Exception as e:
            print(f"⚠️ Error processing line: {e}")
            fail_count += 1

# --- STEP 2: RECONSTRUCT ORIGINAL FILES ---
print(f"\nExtracted {success_count} translations. Errors: {fail_count}.")
print("Reconstructing files...")

for fname in translations_map.keys():
    if not os.path.exists(fname):
        continue

    for lang_code in LANGUAGES.values():
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)
        
        output_path = os.path.join(lang_dir, fname)
        
        with open(fname, 'r', encoding='utf-8') as f_in, \
             open(output_path, 'w', encoding='utf-8') as f_out:
            
            for line_idx, line in enumerate(f_in):
                if not line.strip(): continue
                entry = json.loads(line)
                
                if line_idx in translations_map[fname][lang_code]:
                    line_translations = translations_map[fname][lang_code][line_idx]
                    for q_idx, msg_map in line_translations.items():
                        for msg_idx, translated_val in msg_map.items():
                            try:
                                entry["question"][q_idx][msg_idx]["content"] = translated_val
                            except (IndexError, KeyError):
                                pass 

                f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"\n✅ Done! Check the '{OUTPUT_DIR}' folder.")