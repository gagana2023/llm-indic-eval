import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. SET FILENAMES
file_qwen = 'Qwen_Qwen3-0.6B-FC .xlsx'
file_llama = 'meta-llama_Llama-3.2-1B-Instruct-FC.xlsx'

def get_analysis_df(file_path, model_name):
    # Load the excel file
    df = pd.read_excel(file_path)
    
    # Strip any accidental spaces from column names or language names
    df.columns = df.columns.str.strip()
    df['Language'] = df['Language'].str.strip()
    
    # Identify the English baseline row
    # We look for "English (en-IN)"
    english_mask = df['Language'].str.contains('English', case=False, na=False)
    if not english_mask.any():
        print(f"Warning: English baseline not found in {file_path}")
        return None
    
    english_baseline = df[english_mask].iloc[0]
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    results = []
    for _, row in df.iterrows():
        lang = row['Language']
        if "English" in lang:
            continue
            
        offsets = []
        pct_drops = []
        
        for col in numeric_cols:
            base_val = english_baseline[col]
            lang_val = row[col]
            
            # Offset = Base - Lang
            offset = base_val - lang_val
            offsets.append(offset)
            
            # % Drop = (Offset / Base) * 100
            if base_val != 0:
                pct_drops.append((offset / base_val) * 100)
            else:
                pct_drops.append(0)
        
        results.append({
            'Language': lang,
            f'{model_name} Avg Offset': sum(offsets) / len(offsets),
            f'{model_name} Avg % Drop': sum(pct_drops) / len(pct_drops)
        })
        
    return pd.DataFrame(results)

# 2. RUN ANALYSIS
print("Processing Qwen...")
qwen_results = get_analysis_df(file_qwen, 'Qwen')
print("Processing Llama...")
llama_results = get_analysis_df(file_llama, 'Llama')

# 3. MERGE AND EXPORT
comparison = pd.merge(qwen_results, llama_results, on='Language')
comparison.to_csv('analysis_1_offsets.csv', index=False)
print("\nAnalysis complete! Results saved to 'analysis_1_offsets.csv'")

# 4. PLOT
plt.figure(figsize=(12, 10))
# Sort by Qwen drop for visual clarity
comparison = comparison.sort_values('Qwen Avg % Drop', ascending=False)

plot_data = comparison.melt(id_vars='Language', 
                            value_vars=['Qwen Avg % Drop', 'Llama Avg % Drop'],
                            var_name='Model', value_name='% Performance Drop')

sns.barplot(data=plot_data, y='Language', x='% Performance Drop', hue='Model')
plt.title('Analysis 1: Performance Drop from English (Baseline)')
plt.xlabel('% Drop (Higher bar = Worse performance relative to English)')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('analysis_1_plot.png')
print("Chart saved as 'analysis_1_plot.png'")

# Display the top 5 "Worst performing" languages for Qwen
print("\nTop 5 Languages with biggest performance drop (Qwen):")
print(comparison[['Language', 'Qwen Avg % Drop', 'Llama Avg % Drop']].head(5))