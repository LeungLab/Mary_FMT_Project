import pandas as pd
import os
import glob
import argparse
import sys

def consolidate_resistome_data(input_dir, output_file, abundance_col_name):
    """
    Consolidates data from multiple gene_mapping_data.txt files into a single
    CSV matrix, where rows are ARGs and columns are samples.

    Args:
        input_dir (str): Directory containing the gene_mapping_data.txt files.
        output_file (str): The name of the final combined CSV file.
        abundance_col_name (str): The exact column header for the normalized
                                  gene abundance metric (e.g., 'RPKM').
    """
    print(f"Starting consolidation of data from directory: {input_dir}")
    
    # 1. Define the file pattern to search for
    file_pattern = os.path.join(input_dir, '*gene_mapping_data.txt')
    data_files = glob.glob(file_pattern)

    if not data_files:
        print(f"Error: No files matching '*gene_mapping_data.txt' found in {input_dir}")
        sys.exit(1)

    print(f"Found {len(data_files)} gene mapping files to process.")

    all_data = []
    gene_column = 'ARG_ID' # Standardized name for the gene identifier column

    for filepath in data_files:
        try:
            # 2. Extract sample name from the filename
            # Example filename: 25617X10_S56_unmapped_result.gene_mapping_data.txt
            # Sample name extraction should result in: 25617X10_S56
            filename = os.path.basename(filepath)
            sample_name = filename.split('_unmapped_result')[0]
            
            # 3. Read the data file. Assuming it's tab-separated (TSV)
            df = pd.read_csv(filepath, sep='\t')
            
            # 4. Check if the critical columns exist
            required_cols = [gene_column, abundance_col_name]
            
            # Attempt to find the gene/ARG identifier column (often the first one)
            if df.columns[0] not in required_cols:
                # Rename the first column, which usually contains the gene/ARG name
                df.rename(columns={df.columns[0]: gene_column}, inplace=True)
            
            if gene_column not in df.columns or abundance_col_name not in df.columns:
                 print(f"Warning: Skipping {filename}. Columns '{gene_column}' and '{abundance_col_name}' were not found.")
                 print(f"Available columns in this file: {list(df.columns)}")
                 continue
            
            # Select only the Gene ID and the abundance column
            df_subset = df[[gene_column, abundance_col_name]].copy()
            
            # Rename the abundance column to the sample name for merging
            df_subset.rename(columns={abundance_col_name: sample_name}, inplace=True)
            
            # Append the processed dataframe to the list
            all_data.append(df_subset)
            print(f"Successfully processed sample: {sample_name}")
            
        except Exception as e:
            print(f"An error occurred while processing {filepath}: {e}")

    if not all_data:
        print("Fatal Error: No files were successfully processed. Exiting.")
        return

    # 5. Merge all individual dataframes
    # Start with the first dataframe and successively merge the rest
    combined_df = all_data[0]
    for i in range(1, len(all_data)):
        # Merge on the 'ARG_ID' column (the gene name)
        combined_df = pd.merge(combined_df, all_data[i], on=gene_column, how='outer')

    # 6. Fill NaN (Not a Number) values with 0, as an ARG not present in a sample
    # should have an abundance of zero.
    combined_df = combined_df.fillna(0)
    
    # Set the ARG_ID as the index for a clean matrix look
    combined_df.set_index(gene_column, inplace=True)
    
    # 7. Save the final matrix to the specified output file
    combined_df.to_csv(output_file)
    
    print("\n--- Consolidation Complete ---")
    print(f"Final ARG count (rows): {len(combined_df)}")
    print(f"Total samples (columns): {len(combined_df.columns)}")
    print(f"The final resistome matrix has been saved to: {output_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Consolidate multiple '*gene_mapping_data.txt' files into a single CSV matrix.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('input_dir', 
                        help='Path to the directory containing all the gene_mapping_data.txt files.')
    
    parser.add_argument('--output', 
                        default='resistome_abundance_matrix.csv',
                        help='Name of the output CSV file (default: resistome_abundance_matrix.csv)')
    
    parser.add_argument('--col', 
                        required=True,
                        help="""The exact header of the column containing the normalized ARG abundance.
(Example: If your file has 'ARG_ID', 'Reads', 'RPKM', you would use 'RPKM').
This is CRITICAL to specify correctly.""")
    
    args = parser.parse_args()
    
    # Check for pandas installation and warn the user
    try:
        import pandas as pd
    except ImportError:
        print("Error: The 'pandas' library is required to run this script.")
        print("Please install it using: pip install pandas")
        sys.exit(1)

    consolidate_resistome_data(args.input_dir, args.output, args.col)
