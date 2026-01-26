#!/bin/bash
#SBATCH --partition=notchpeak
#SBATCH --account=leung
#SBATCH --time=48:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64000
#SBATCH --job-name=bowtie2_parallel
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=ali.akeefe@.utah.edu
#SBATCH -o logs/parallel_bowtie2-%j.log

module load bowtie2
module load parallel

cd ./ali_raw_reads/untrimmed_reads/trimmed_reads

outdir="./processed_reads"
mkdir -p "$outdir"
export outdir
export BOWTIE_INDEX=/scratch/general/vast/u1527341/Mcode/code/Homo_sapiens/NCBI/GRCh38/Sequence/Bowtie2Index/genome

# Function to run alignment (to be called by GNU Parallel)
run_bowtie2() {
  SAMPLE="$1"
  fq1="${SAMPLE}_good_1_val_1.fq"
  fq2="${SAMPLE}_good_2_val_2.fq"
  sam_out="${outdir}/${SAMPLE}_aligned.sam"

  if [[ -f "$sam_out" ]]; then
    echo "[✓] Skipping $SAMPLE — already aligned."
    return 0
  fi

  echo "[$SAMPLE] Running Bowtie2..."
  bowtie2 -p 4 \
    -x "$BOWTIE_INDEX" \
    -1 "$fq1" -2 "$fq2" -S "$sam_out"
  echo "[$SAMPLE] Done."
}

export -f run_bowtie2

# Run up to 4 samples at a time, each using 4 threads (total 16 threads)
parallel -j 4 run_bowtie2 :::: sample_list.txt

