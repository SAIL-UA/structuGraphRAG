import pandas as pd
import glob
from io import StringIO
import csv  # Importing csv for quoting
import sys

def parse_csv_data(csv_content):
    # Read the CSV into a DataFrame
    df = pd.read_csv(StringIO(csv_content))
    
    # Check if the first row contains "Value", "Label", "Frequency", and "%"
    if df.columns.tolist() == ["Value", "Label", "Frequency", "%"]:
        print("Skipping CSV with headers:", df.columns.tolist())
        return []
    
    # Find the variable name and short description from the first row
    variable_name = None
    short_description = None
    for col in df.columns:
        if col != "Unnamed: 0" and ':' in col:
            try:
                variable_name, short_description = col.split(": ")
                short_description = short_description.split("\"")[0]
                break
            except ValueError as e:
                print(f"Error splitting column '{col}': {e}")
    
    if variable_name is None or short_description is None:
        raise ValueError("Variable name and short description not found in the first row.")
    
    print("variable name: ", variable_name)
    print("short description: ", short_description)

    # Initialize lists to store answer codes and descriptions
    answer_codes = []
    answer_descriptions = []

    # Iterate over the rows to extract answer codes and descriptions
    for index, row in df.iterrows():
        if pd.isna(row.iloc[0]) and row.iloc[1] == "Total":
            break
        if index > 0 and pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
            answer_codes.append(row.iloc[0])
            answer_descriptions.append(row.iloc[1])

    # Prepare the result
    results = []
    for code, description in zip(answer_codes, answer_descriptions):
        results.append({
            "Variable_name": variable_name,
            "Short_description": short_description,
            "Answer_code": code,
            "Answer_meaning": description
        })
    return results

# Path to the folder containing CSV files
folder_path = 'csvs'
csv_files = glob.glob(f'{folder_path}/*.csv')

try:
    # Process each CSV file and save the parsed results
    for index, file_path in enumerate(csv_files, start=1):
        with open(file_path, 'r') as file:
            csv_content = file.read()
            parsed_results = parse_csv_data(csv_content)

            # Skip saving if the parsed results are empty
            if not parsed_results:
                continue

        # Convert parsed results to a DataFrame
        parsed_df = pd.DataFrame(parsed_results)
        
        # Save the DataFrame to a new CSV file
        parsed_df.to_csv(f'nsumhss_parsed_table_{index}.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Optional: Print the last DataFrame for verification
    print(parsed_df)

except ValueError as e:
    print(e)
    sys.exit(1)
