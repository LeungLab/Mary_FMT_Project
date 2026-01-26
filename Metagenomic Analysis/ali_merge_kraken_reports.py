#!/usr/bin/env python3

"""
Merge Kraken2 reports into a raw count table at a desired taxonomic level.
Usage:
    python ali_merge_kraken_reports.py --pattern "*.report" --level G --contaminants Escherichia_coli,1234
"""

import os
import glob
import pandas as pd
import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Merge Kraken2 reports into raw count table.")

    parser.add_argument(
        '--pattern', required=True,
        help='Wildcard pattern to match Kraken2 report files (e.g., "*.report")'
    )
    parser.add_argument(
        '--level', required=True,
        help='Taxonomic level to extract (e.g., U, R, D, P, C, O, F, G, S)'
    )
    parser.add_argument(
        '--contaminants', default='',
        help='Comma-separated list of contaminant names or taxids to exclude'
    )
    parser.add_argument(
        '--output', default='merged_kraken_counts.tsv',
        help='Output file name (default: merged_kraken_counts.tsv)'
    )

    args = parser.parse_args()

    # Expand wildcard pattern to file paths
    k2_reports = sorted(glob.glob(args.pattern))
    if not k2_reports:
        sys.exit(f"No files matched the pattern: {args.pattern}")

    # Generate sample IDs from file names
    reports_ids = [os.path.basename(f).replace('_kraken.report', '') for f in k2_reports]

    # Parse contaminants
    contaminants = args.contaminants.split(',') if args.contaminants else []
    contaminants = [c.replace('_', ' ') for c in contaminants]

    return k2_reports, reports_ids, args.level, contaminants, args.output


def parse_k2_report(sample_name, path, desired_level, contaminants=[]):
    k2_data = {}
    root_n = 0
    unclassified_n = 0

    with open(path, 'r') as f:
        for line in f:
            line = line.lstrip()
            if not line:
                continue

            fields = line.strip().split('\t')
            if len(fields) == 8:
                _, n_fragments_clade, _, _, _, rank, taxid, name = fields
            elif len(fields) == 6:
                _, n_fragments_clade, _, rank, taxid, name = fields
            else:
                continue  # Skip malformed lines

            name = name.strip()
            taxid = taxid.strip()
            rank = rank.strip()
            try:
                n_fragments_clade = int(n_fragments_clade)
            except ValueError:
                continue

            if rank == 'R':
                root_n = n_fragments_clade
            elif rank == 'U':
                unclassified_n = n_fragments_clade
            elif rank != desired_level:
                continue
            elif taxid in contaminants or name in contaminants:
                continue
            elif n_fragments_clade == 0:
                continue
            else:
                k2_data[name] = n_fragments_clade

    return pd.Series(k2_data, name=sample_name), root_n, unclassified_n


def main():
    k2_reports, reports_ids, tax_lvl, contaminants, output_path = parse_args()

    reports_data = []
    roots, unclassifieds = {}, {}

    for sid, path in zip(reports_ids, k2_reports):
        sample_series, root_count, unclassified_count = parse_k2_report(sid, path, tax_lvl, contaminants)
        reports_data.append(sample_series)
        roots[sid] = root_count
        unclassifieds[sid] = unclassified_count

    merged_df = pd.concat(reports_data, axis=1)
    merged_df.fillna(0, inplace=True)
    merged_df.index.name = 'taxon'
    merged_df = merged_df.reset_index()

    merged_df.to_csv(output_path, sep='\t', index=False)
    print(f"✅ Merged Kraken2 report saved to: {output_path}")


if __name__ == '__main__':
    main()
