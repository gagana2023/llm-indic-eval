import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. LOAD DATA
file_qwen = 'Qwen_Qwen3-0.6B-FC .xlsx'
file_llama = 'meta-llama_Llama-3.2-1B-Instruct-FC.xlsx'

df_qwen = pd.read_excel(file_qwen)
df_llama = pd.read_excel(file_llama)

# Define Linguistic Families
family_mapping = {
    'Hindi (hi-IN)': 'Indo-Aryan', 'Bengali (bn-IN)': 'Indo-Aryan',
    'Marathi (mr-IN)': 'Indo-Aryan', 'Gujarati (gu-IN)': 'Indo-Aryan',
    'Punjabi (pa-IN)': 'Indo-Aryan', 'Urdu (ur-IN)': 'Indo-Aryan',
    'Odia (od-IN)': 'Indo-Aryan', 'Assamese (as-IN)': 'Indo-Aryan',
    'Maithili (mai-IN)': 'Indo-Aryan', 'Konkani (kok-IN)': 'Indo-Aryan',
    'Dogri (doi-IN)': 'Indo-Aryan', 'Sanskrit (sa-IN)': 'Indo-Aryan',
    'Nepali (ne-IN)': 'Indo-Aryan', 'Sindhi (sd-IN)': 'Indo-Aryan',
    'Kashmiri (ks-IN)': 'Indo-Aryan',
    'Tamil (ta-IN)': 'Dravidian', 'Telugu (te-IN)': 'Dravidian',
    'Kannada (kn-IN)': 'Dravidian', 'Malayalam (ml-IN)': 'Dravidian',
    'Santali (sat-IN)': 'Austroasiatic', 'Bodo (brx-IN)': 'Sino-Tibetan',
    'Manipuri (mni-IN)': 'Sino-Tibetan'
}

def get_family_data(df, model_name):
    df.columns = df.columns.str.strip()
    df['Language'] = df['Language'].str.strip()
    english_baseline = df[df['Language'].str.contains('English', case=False)].iloc[0]
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    results = []
    for _, row in df.iterrows():
        lang = row['Language']
        if "English" in lang: continue
        
        pct_drops = []
        for col in numeric_cols:
            base = english_baseline[col]
            if base != 0:
                pct_drops.append(((base - row[col]) / base) * 100)
        
        results.append({
            'Language': lang,
            'Family': family_mapping.get(lang, 'Other'),
            'Avg % Drop': sum(pct_drops) / len(pct_drops) if pct_drops else 0,
            'Model': model_name
        })
    return pd.DataFrame(results)

# 2. PROCESS
data_qwen = get_family_data(df_qwen, 'Qwen')
data_llama = get_family_data(df_llama, 'Llama')
combined = pd.concat([data_qwen, data_llama])

# 3. PREPARE HEATMAP DATA
# We want to see Mean % Drop per Family for each Model
heatmap_data = combined.groupby(['Family', 'Model'])['Avg % Drop'].mean().unstack()

# 4. PLOT
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_data, annot=True, cmap='YlOrRd', fmt=".1f")
plt.title('Analysis 3: Linguistic Family vs. Model Performance Drop\n(Heatmap showing % Drop from English)')
plt.savefig('family_heatmap.png')

print("\nMean % Drop by Linguistic Family:")
print(heatmap_data)