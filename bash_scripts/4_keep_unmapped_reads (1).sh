#!/bin/bash
#SBATCH --partition=notchpeak
#SBATCH --account=leung
#SBATCH --time=48:00:00
#SBATCH -n 16
#SBATCH --mem=64000
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=ali.akeefe@utah.edu
#SBATCH --job-name=samtools_kraken_prep
#SBATCH -o logs/samtools_kraken-%j.log
#SBATCH --open-mode=append

module load samtools
module load parallel

cd ./ali_raw_reads/untrimmed_reads/trimmed_reads

# Directories
input_dir="./processed_reads"
bam_dir="./bam"
fastq_dir="./fastq_for_kraken"

mkdir -p "$bam_dir" "$fastq_dir"

# Function to process each sample
process_sample() {
  SAMPLE="$1"
  sam_file="${input_dir}/${SAMPLE}_aligned.sam"
  bam_file="${bam_dir}/${SAMPLE}.bam"
  unmapped_bam="${bam_dir}/${SAMPLE}_unmapped.bam"
  fastq_out="${fastq_dir}/${SAMPLE}_unmapped.fastq"

  if [[ ! -f "$sam_file" ]]; then
    echo "[!] Missing SAM for $SAMPLE"
    return 1
  fi

  echo "[$SAMPLE] Converting SAM to BAM..."
  samtools view -bS "$sam_file" > "$bam_file"

  echo "[$SAMPLE] Extracting unmapped reads..."
  samtools view -b -f 4 "$bam_file" > "$unmapped_bam"

  echo "[$SAMPLE] Converting unmapped BAM to FASTQ..."
  samtools fastq "$unmapped_bam" > "$fastq_out"

  echo "[$SAMPLE] Done."
}

export input_dir bam_dir fastq_dir
export -f process_sample

# Run in parallel (adjust -j to match available cores)
parallel -j 4 process_sample :::: sample_list.txt

