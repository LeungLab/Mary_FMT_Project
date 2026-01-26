#!/bin/bash

#SBATCH --partition=notchpeak
#SBATCH --account=leung
#SBATCH --time=8:00:00
#SBATCH -n 32
#SBATCH --mem=200000
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=ali.akeefe@utah.edu
#SBATCH --job-name=krakenrun
#SBATCH -o logs/krakenrun-%j.log
#SBATCH --open-mode=append

# Load Kraken2
module load kraken2

# Move into directory with FASTQ files
cd ali_raw_reads/untrimmed_reads/trimmed_reads/fastq_for_kraken

# Create results directory if it doesn't exist
mkdir -p kraken2results_marco

# Run Kraken2 on all *_kraken.fastq files
for fq in *_unmapped.fastq; do
    sample=$(basename "$fq" _unmapped.fastq)
    echo "Running Kraken2 on $fq"
    kraken2 \
        --db /scratch/general/vast/u1527341/Mcode/code/kraken2_db_for_gabriella \
        --threads 8 \
        --report kraken2results_marco/${sample}.report \
        --output kraken2results_marco/${sample}_output.txt \
        "$fq"
    echo "Finished processing $sample"
done

echo "All Kraken2 classifications completed."

