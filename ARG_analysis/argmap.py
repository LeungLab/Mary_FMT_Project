import pandas as pd
import glob
import os
import argparse

def generate_arg_class_map(input_dir, output_file):
    """
    Scans all gene_mapping_data.txt files in a directory, extracts the
    ARO Term and Drug Class columns, and creates a unique, consolidated
    mapping file.
    """
    
    # Define the required column names exactly as they appear in the files
    # Note: Using a dictionary to map the potentially wide name to a clean name
    REQUIRED_COLUMNS = {
        'ARO Term': 'ARO_Term',
        'Drug Class': 'Drug_Class'
    }

    all_maps = []
    
    # 1. Iterate through all matching files
    search_path = os.path.join(input_dir, '*gene_mapping_data.txt')
    file_list = glob.glob(search_path)
    
    if not file_list:
        print(f"Error: No '*gene_mapping_data.txt' files found in '{input_dir}'")
        return

    print(f"Found {len(file_list)} files. Consolidating ARG mappings...")
    
    # 2. Process each file
    for filepath in file_list:
        try:
            # Read the file assuming it is tab-separated
            # We only read the first few columns to speed up loading and reduce memory usage
            df = pd.read_csv(filepath, sep='\t', usecols=REQUIRED_COLUMNS.keys())
            
            # Rename columns to cleaner names for the output file
            df = df.rename(columns=REQUIRED_COLUMNS)
            
            # Select only the two required columns
            map_data = df[['ARO_Term', 'Drug_Class']].copy()
            
            all_maps.append(map_data)
            
        except Exception as e:
            print(f"Could not process file {filepath}. Error: {e}")
            
    # 3. Concatenate and clean the data
    if all_maps:
        # Combine all extracted dataframes
        combined_df = pd.concat(all_maps, ignore_index=True)
        
        # Drop duplicates to create the unique, definitive map
        final_map = combined_df.drop_duplicates().reset_index(drop=True)
        
        # 4. Save the final map
        final_map.to_csv(output_file, index=False)
        print("-" * 50)
        print(f"Success! Created mapping file: '{output_file}'")
        print(f"Total unique ARO Terms mapped: {len(final_map)}")
        print(f"This file is now ready for use in the R analysis script.")
    else:
        print("No data could be processed. Exiting.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generates a unique ARG Class map by consolidating data from all gene_mapping_data.txt files."
    )
    parser.add_argument(
        'input_dir', 
        type=str, 
        help="Path to the directory containing the original '*gene_mapping_data.txt' files. Use '.' for the current directory."
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='arg_class_map.csv', 
        help="Name of the output CSV file to save the unique map (default: arg_class_map.csv)."
    )
    args = parser.parse_args()
    
    generate_arg_class_map(args.input_dir, args.output)
