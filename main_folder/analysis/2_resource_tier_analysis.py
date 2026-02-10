import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. LOAD DATA
file_qwen = 'Qwen_Qwen3-0.6B-FC .xlsx'
file_llama = 'meta-llama_Llama-3.2-1B-Instruct-FC.xlsx'

df_qwen = pd.read_excel(file_qwen)
df_llama = pd.read_excel(file_llama)

# Define Tiers
tier_mapping = {
    'Hindi (hi-IN)': 'Tier 1 (High)', 'Bengali (bn-IN)': 'Tier 1 (High)',
    'Tamil (ta-IN)': 'Tier 2 (Mid)', 'Telugu (te-IN)': 'Tier 2 (Mid)', 
    'Marathi (mr-IN)': 'Tier 2 (Mid)', 'Kannada (kn-IN)': 'Tier 2 (Mid)', 
    'Malayalam (ml-IN)': 'Tier 2 (Mid)', 'Gujarati (gu-IN)': 'Tier 2 (Mid)',
    'Punjabi (pa-IN)': 'Tier 2 (Mid)', 'Urdu (ur-IN)': 'Tier 2 (Mid)',
    'Odia (od-IN)': 'Tier 3 (Low)', 'Assamese (as-IN)': 'Tier 3 (Low)', 
    'Maithili (mai-IN)': 'Tier 3 (Low)', 'Santali (sat-IN)': 'Tier 3 (Low)', 
    'Kashmiri (ks-IN)': 'Tier 3 (Low)', 'Sindhi (sd-IN)': 'Tier 3 (Low)',
    'Sanskrit (sa-IN)': 'Tier 3 (Low)', 'Nepali (ne-IN)': 'Tier 3 (Low)', 
    'Konkani (kok-IN)': 'Tier 3 (Low)', 'Dogri (doi-IN)': 'Tier 3 (Low)', 
    'Manipuri (mni-IN)': 'Tier 3 (Low)', 'Bodo (brx-IN)': 'Tier 3 (Low)'
}

def get_tier_data(df, model_name):
    df.columns = df.columns.str.strip()
    df['Language'] = df['Language'].str.strip()
    english_baseline = df[df['Language'].str.contains('English', case=False)].iloc[0]
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    tier_results = []
    for _, row in df.iterrows():
        lang = row['Language']
        if "English" in lang: continue
        
        pct_drops = []
        for col in numeric_cols:
            base = english_baseline[col]
            if base != 0:
                pct_drops.append(((base - row[col]) / base) * 100)
        
        tier_results.append({
            'Language': lang,
            'Tier': tier_mapping.get(lang, 'Other'),
            'Avg % Drop': sum(pct_drops) / len(pct_drops) if pct_drops else 0,
            'Model': model_name
        })
    return pd.DataFrame(tier_results)

# 2. PROCESS
qwen_tier = get_tier_data(df_qwen, 'Qwen')
llama_tier = get_tier_data(df_llama, 'Llama')
combined = pd.concat([qwen_tier, llama_tier])

# 3. PLOT
plt.figure(figsize=(10, 6))
sns.boxplot(data=combined, x='Tier', y='Avg % Drop', hue='Model', order=['Tier 1 (High)', 'Tier 2 (Mid)', 'Tier 3 (Low)'])
plt.title('Analysis 2: Performance Decay by Resource Tier')
plt.ylabel('% Drop from English')
plt.grid(axis='y', alpha=0.3)
plt.savefig('tier_analysis_plot.png')

# Print Summary for Interpretation
print("\nMean Performance Drop per Tier:")
print(combined.groupby(['Tier', 'Model'])['Avg % Drop'].mean().unstack())