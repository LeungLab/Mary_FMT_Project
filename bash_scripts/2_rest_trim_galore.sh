#!/bin/bash
#SBATCH --account=leung
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=ali.akeefe@utah.edu
#SBATCH --job-name=trim_galore
#SBATCH -o logs/trim_galore-%j.log
#SBATCH --open-mode=append

module purge
module load trim_galore

cd ali_raw_reads

cd untrimmed_reads


# Loop over each sample prefix in the list
while IFS= read -r prefix; do
  # Check if output files already exist
  if [[ -f "trimmed_reads/${prefix}_good_1_val_1.fq" && -f "trimmed_reads/${prefix}_good_2_val_2.fq" ]]; then
    echo "[✓] Skipping $prefix — already trimmed."
    continue
  fi

  echo "[*] Trimming $prefix"

  # Run Trim Galore using 4 cores
  trim_galore --cores 4 --paired \
    "${prefix}_good_1.fastq" "${prefix}_good_2.fastq" \
    --fastqc

  # Organize report outputs
  mkdir -p report
  mv "${prefix}"*fastqc* report
  mv "${prefix}"*txt report
  mv "${prefix}"*html report

  mkdir -p trimmed_reads
  mv "${prefix}"*val_1.fq* trimmed_reads
  mv "${prefix}"*val_2.fq* trimmed_reads

  echo "[✓] Done with $prefix"
done < sample_list.txt

