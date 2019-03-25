#!/usr/bin/env python

"""Inputs Production Metrics (tab3) of BCM HGSC TOPMed Weekly Report
and generates an Excel workbook with project average metrics by Collection"""

import argparse
import re

import pandas as pd

# display.precision sets the output display precision in terms of decimal places
pd.set_option('precision', 4)


def main():
    args = parse_args()
    run(args.weekly_report, args.output_file)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('weekly_report',
                        help='*.xlsx, usually sheet_name is Production Metrics'
                        ' in tab3')
    parser.add_argument('output_file',
                        help='*.xlsx, outputs Project Averages in tab4 for'
                        ' Weekly Report')
    args = parser.parse_args()
    return args


def run(weekly_report, output_file):
    # Production Metrics
    pm = pd.read_excel(weekly_report, sheet_name='Production Metrics')

    col_dict = {c: normalize_name(c) for c in pm.columns}
    pm.rename(columns=col_dict, inplace=True)
    # groupby
    pm_gr = pm.groupby(['collection']).mean()
    # reorder columns
    avg_cols = ['mean_insert_size_library_avg', 'mean_coverage_raw',
                'per_10_coverage_bases', 'per_20_coverage_bases',
                'q20_bases', 'contamination_pct']
    pm_gr_av = pm_gr[avg_cols]
    # write to excel with float_format
    pm_gr_av.to_excel(output_file, sheet_name='tab4', float_format='%.4f')


def normalize_name(field_name):
    """lowercase with underscores, etc"""
    fixes = (
        (r'/', '_per_'),
        (r'%', '_pct_'),
        (r'\W', '_'),
        (r'^_+', ''), # remove '_' if field_name begins with '_'
        (r'_+$', ''),
        (r'__+', '_'),
    )
    result = field_name.strip().lower() or None
    # result = field_name.strip().upper() or None
    if result:
        if result.endswith('?'):
            if not re.match(r'is[_\W]', result):
                result = 'is_' + result
        for pattern, replacement in fixes:
            result = re.sub(pattern, replacement, result)
    return result


if __name__ == '__main__':
    main()
