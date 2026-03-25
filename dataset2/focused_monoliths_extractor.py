import pandas as pd
import os
import glob

def extract_expert_god_classes(input_list="expert_monoliths.csv", 
                               csv_dir="../dataset/csvs/", 
                               output_folder="expert_java_files"):
    # 1. Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")

    # 2. Read the list of envy-free candidate classes
    if not os.path.exists(input_list):
        print(f"Error: {input_list} not found.")
        return
    
    expert_list = pd.read_csv(input_list)
    extracted_count = 0

    # 3. Process each candidate
    for _, row in expert_list.iterrows():
        project = str(row['Project']).lower()
        target_class = row['Class']
        
        # Build path to the project CSV (e.g., ../dataset/csvs/accumulo.csv)
        project_csv_path = os.path.join(csv_dir, f"{project}.csv")
        
        if not os.path.exists(project_csv_path):
            # Try to find it if naming isn't perfectly lowercase
            matches = glob.glob(os.path.join(csv_dir, f"{project}*.csv"))
            if matches:
                project_csv_path = matches[0]
            else:
                continue

        try:
            # Read project CSV
            proj_df = pd.read_csv(project_csv_path)
            
            # Normalize column names for reliability
            proj_df.columns = [c.strip() for c in proj_df.columns]
            
            # Filter for:
            # - The specific class
            # - God Class label (Smelly == 1)
            # - Row must have Code
            match = proj_df[
                (proj_df['Class'] == target_class) & 
                (proj_df['Smelly'] == 1)
            ]

            if not match.empty:
                # Get the code from the first matching row 
                # (Assuming the God Class label row contains the class-level code)
                class_code = match.iloc[0]['Code']
                
                if pd.isna(class_code) or str(class_code).strip() == "":
                    continue

                # Create a safe filename: Project_Class.java
                safe_class_name = "".join(x for x in str(target_class) if x.isalnum() or x in "._-")
                filename = f"{project}_{safe_class_name}.java"
                filepath = os.path.join(output_folder, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(class_code)
                
                extracted_count += 1
                print(f"Extracted: {filename}")

        except Exception as e:
            print(f"Error processing {project_csv_path} for class {target_class}: {e}")

    print(f"\nFinished! Extracted {extracted_count} Expert God Classes to '{output_folder}'.")

if __name__ == "__main__":
    extract_expert_god_classes()
