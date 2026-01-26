#!/bin/bash
#SBATCH --partition=notchpeak
#SBATCH --account=leung
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=200G
#SBATCH --array=0-315
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=ali.akeefe@utah.edu
#SBATCH --job-name=prinseq_dedup
#SBATCH -o logs/prinseq_dedup-%A.log
#SBATCH --open-mode=append

module load perl


# Ensure output directory exists
mkdir -p untrimmed_reads

# Get sample prefix
prefix=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" sample_list.txt)

echo "[*] Processing $prefix"

# Decompress .gz files temporarily
zcat ${prefix}_R1_001.fastq.gz > ${prefix}_R1_001.fastq
zcat ${prefix}_R2_001.fastq.gz > ${prefix}_R2_001.fastq

# Run prinseq-lite to remove duplicate reads
perl prinseq-lite-0.20.4/prinseq-lite.pl \
    -derep 14 \
    -fastq ${prefix}_R1_001.fastq \
    -fastq2 ${prefix}_R2_001.fastq \
    -out_good untrimmed_reads/${prefix}_good \
    -out_bad untrimmed_reads/${prefix}_bad

echo "[✓] Done with $prefix"

