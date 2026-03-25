import pandas as pd
import glob
import os

def identify_expert_monoliths(output_file="expert_monoliths.csv"):
    # 1. Gather all CSV files in the current directory
    all_files = glob.glob("*.csv")
    
    if not all_files:
        print("No CSV files found in the current directory.")
        return

    dfs = []
    required_cols = ['Project', 'Version', 'File', 'Class', 'Smelly']

    for filename in all_files:
        if filename == output_file:
            continue
        try:
            df = pd.read_csv(filename)
            
            # Normalize column names to handle potential case sensitivity
            cols_map = {c.lower(): c for c in df.columns}
            if all(r.lower() in cols_map for r in required_cols):
                df = df.rename(columns={cols_map[r.lower()]: r for r in required_cols})
                dfs.append(df[required_cols])
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    if not dfs:
        print("No valid data found in CSV files.")
        return

    # 2. Combine and aggregate
    full_df = pd.concat(dfs, axis=0, ignore_index=True)

    # Group by the unique class identifiers and sum the 'Smelly' labels
    # If the sum is 0, then NO method in that class has feature envy
    class_group = full_df.groupby(['Project', 'Version', 'File', 'Class'])['Smelly'].sum().reset_index()

    # 3. Filter for 'Expert' classes
    expert_monoliths = class_group[class_group['Smelly'] == 0]

    # 4. Finalize and Save
    result = expert_monoliths.drop(columns=['Smelly'])
    result.to_csv(output_file, index=False)
    print(f"Success! Identified {len(result)} expert classes. Results saved to {output_file}.")

if __name__ == "__main__":
    identify_expert_monoliths()
