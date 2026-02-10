import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. LOAD DATA
file_qwen = 'Qwen_Qwen3-0.6B-FC .xlsx'
file_llama = 'meta-llama_Llama-3.2-1B-Instruct-FC.xlsx'

df_qwen = pd.read_excel(file_qwen)
df_llama = pd.read_excel(file_llama)

def get_task_offsets(df, model_name):
    df.columns = df.columns.str.strip()
    english_baseline = df[df['Language'].str.contains('English', case=False)].iloc[0]
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    task_results = []
    for col in numeric_cols:
        eng_val = english_baseline[col]
        # Mean of all other languages for this specific task
        other_langs_mean = df[~df['Language'].str.contains('English', case=False)][col].mean()
        
        offset = eng_val - other_langs_mean
        pct_drop = (offset / eng_val * 100) if eng_val != 0 else 0
        
        task_results.append({
            'Task': col,
            'Avg % Drop': pct_drop,
            'Model': model_name
        })
    return pd.DataFrame(task_results)

# 2. PROCESS
task_qwen = get_task_offsets(df_qwen, 'Qwen')
task_llama = get_task_offsets(df_llama, 'Llama')
combined_tasks = pd.concat([task_qwen, task_llama])

# 3. PLOT TOP 10 HARDEST TASKS
plt.figure(figsize=(12, 8))
# Group by Task and get the mean drop to find the "Hardest" ones overall
hardest_tasks = combined_tasks.groupby('Task')['Avg % Drop'].mean().sort_values(ascending=False).index[:12]
top_tasks_df = combined_tasks[combined_tasks['Task'].isin(hardest_tasks)]

sns.barplot(data=top_tasks_df, y='Task', x='Avg % Drop', hue='Model')
plt.title('Analysis 4: Which Tasks are "Lost in Translation"?\n(Top 12 Tasks with Highest Performance Drop)')
plt.xlabel('% Drop from English Capability')
plt.tight_layout()
plt.savefig('task_difficulty_analysis.png')

print("\nTop 5 Hardest Tasks (Overall):")
print(combined_tasks.groupby('Task')['Avg % Drop'].mean().sort_values(ascending=False).head(5))