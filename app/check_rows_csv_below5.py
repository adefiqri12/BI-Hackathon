import os
import pandas as pd

def count_csv_rows_in_directory(directory_path):
    # Check if the directory path exists
    if not os.path.isdir(directory_path):
        print(f"The directory '{directory_path}' does not exist.")
        return

    # Traverse through all directories and subdirectories
    for root, dirs, files in os.walk(directory_path):
        # Filter out only the .csv files
        csv_files = [file for file in files if file.endswith('.csv')]

        # If there are no .csv files in the directory, continue to the next directory
        if len(csv_files) == 0:
            print(f"No .csv files found in the directory '{root}'.")
            continue

        # Iterate over each .csv file
        for file in csv_files:
            file_path = os.path.join(root, file)
            try:
                # Try reading the .csv file using pandas with utf-8 encoding
                df = pd.read_csv(file_path, encoding='utf-8')
            except Exception as e:
                print(f"Error reading file '{file}' with utf-8 encoding: {e}")
                try:
                    # Try reading the .csv file using pandas with latin-1 encoding
                    df = pd.read_csv(file_path, encoding='latin-1')
                    # Convert the dataframe to utf-8 encoding and write it to a new file
                    utf8_file_path = os.path.join(root, f"{os.path.splitext(file)[0]}.csv")
                    df.to_csv(utf8_file_path, index=False, encoding='utf-8')
                    print(f"Converted file '{file}' to utf-8 encoding and saved as '{os.path.basename(utf8_file_path)}'.")
                except Exception as e:
                    print(f"Error reading file '{file}' with latin-1 encoding: {e}")
                    print(f"Unable to read file '{file}'.")
                    continue

            num_rows = len(df)
            missing_values = df.isnull().sum().sum()
            non_na_rows = df.dropna()
            num_rows_after_dropping_na = len(non_na_rows)
                
            # Print the results if the number of rows after dropping NaN values is less than 4
            if num_rows_after_dropping_na < 4:
                print(f"File '{os.path.splitext(file)[0]}' contains {num_rows_after_dropping_na} rows of data after dropping rows with {missing_values} missing values.")

# Example usage:
directory_path = r'BI-Hackathon'
count_csv_rows_in_directory(directory_path)