#!/usr/bin/env python

"""Combines output weekly merge report (from QC group) with new metrics report
(from R&D group) and generates an Excel workbook with two sheets."""

import argparse
import re

import pandas as pd


SUB_COLS = [
    'merge_name',
    'merge_finished_date',
    'aligned_bases', # qc only
    'duplicate_bases', # qc only
    'aligned_bases_pct', # qc only
    'average_coverage',
    'chimeric_rate', # qc only
    'per_ten_coverage_bases',
    'per_twenty_coverage_bases',
    'q20_bases',
    'contamination_rate'
]

TM_COLS = [
    # weekly_report
    'sample_id',
    'collection',
    'pf_hq_aligned_q20_bases',
    'mean_insert_size_library_avg',
    'average_coverage',
    'wgs_het_snp_q',
    'wgs_het_snp_sensitivity',
    'per_ten_coverage_bases',
    'per_twenty_coverage_bases',
    'q20_bases',
    'contamination_pct',
    # qc only
    'unique_aligned_gb',
    'aligned_bases_pct',
    'chimeric_rate',
    'merge_name',
    'merge_finished_date',
    'merge_cram_path',
    'results'
]

RPT_COLS = [
    'sample_id',
    'collection',
    'pf_hq_aligned_q20_bases',
    'mean_insert_size_library_avg',
    'average_coverage',
    'wgs_het_snp_q',
    'wgs_het_snp_sensitivity',
    'per_ten_coverage_bases',
    'per_twenty_coverage_bases',
    'q20_bases',
    'contamination_pct'
]

COLLECTION_DICT = {
        'Legacy': 'TOPMed Control',
        'TMHASC': 'Harvard SCD'
}

# columns in weekly report tab3 'Production Metrics'
# External ID # extract from merge_name
# Collection # cohort?
# PF HQ Aligned Q20 Bases # new
# Mean Insert Size (Library AVG) # new
# Mean Coverage (Raw) # Average Coverage?
# WGS HET SNP Q # new
# WGS HET SNP SENSITIVITY # new
# Per 10 Coverage Bases
# Per 20 Coverage Bases
# Q20 Bases
# Contamination % # convert Contamination Rate to Contamination %
# Notes


def main():
    args = parse_args()
    run(args.recent_merge_report, args.new_metrics_file, args.output_file)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recent_merge_report',
                        help='*.xlsx, usually generated by QC group')
    parser.add_argument('new_metrics_file',
                        help='*.xlsx, usually generated by R&D group')
    parser.add_argument('output_file',
                        help='should end with .xlsx')
    args = parser.parse_args()
    return args


def run(recent_merge_report, new_metrics_file, output_file):
    rtm_sub = load_merge_report(recent_merge_report)
    nm = load_metrics(new_metrics_file)
    m = pd.merge(rtm_sub, nm, how='outer',
                 left_on='sample_id', right_on='sample_id')
    # TODO track weeks
    # will contain output for at least the last 4 weeks along with metrics
    tmqc = m[TM_COLS]
    rpt = m[RPT_COLS]
    output_results(output_file, rpt, tmqc)


def load_merge_report(recent_merge_report):
    rtm = pd.read_excel(recent_merge_report, sheet_name='table ref')

    # normalize column names
    d1 = {c: normalize_name(c) for c in rtm.columns}
    rtm.rename(columns=d1, inplace=True)

    # use loc to avoid warning message
    rtm_sub = rtm.loc[:, SUB_COLS]

    # extract abbrev from merge_name
    cid = rtm_sub['merge_name'].str.split('_', n=5, expand=True)[2]

    # TODO add default value using defaultdict
    # add a column 'collection'
    rtm_sub['collection'] = cid.map(COLLECTION_DICT)

    # extract sample_id from merge_name
    sid = rtm_sub['merge_name'].str.split('_', n=5, expand=True)[3]

    rtm_sub['sample_id'] = sid
    # rtm_sub['sample_id'] = sid.copy()

    # convert contamination_rate to contamination_pct
    rtm_sub['contamination_pct'] = (rtm_sub['contamination_rate'] * 100)

    # aligned_bases (CN)
    # duplicate_bases (DC)

    # pandas broadcasting operation
    rtm_sub['unique_aligned_gb'] = (
        rtm_sub['aligned_bases'] - rtm_sub['duplicate_bases']
    ) / 1_000_000_000

    # add qc results 'PASS' or 'FAIL'
    b1 = (rtm_sub['unique_aligned_gb'] > 90.0) | (
        rtm_sub['unique_aligned_gb'] == 90.0
    )
    b2 = (rtm_sub['aligned_bases_pct'] > 90.0) | (
        rtm_sub['aligned_bases_pct'] == 90.0
    )
    b3 = (rtm_sub['average_coverage'] > 30.0) | (
        rtm_sub['average_coverage'] == 30.0
    )
    b4 = (rtm_sub['per_ten_coverage_bases'] > 95.0) | (
        rtm_sub['per_ten_coverage_bases'] == 95.0
    )
    b5 = (rtm_sub['per_twenty_coverage_bases'] > 90.0) | (
        rtm_sub['per_twenty_coverage_bases'] == 90.0
    )
    b6 = (rtm_sub['q20_bases'] > 87_000_000_000) | (
        rtm_sub['q20_bases'] == 87_000_000_000
    )
    b7 = (rtm_sub['contamination_pct'] < 3.0)
    b8 = (rtm_sub['chimeric_rate'] < 5.0)
    rtm_sub['bool_val'] = b1 & b2 & b3 & b4 & b5 & b6 & b7 & b8
    bool_dict = {True: 'PASS', False: 'FAIL'}
    rtm_sub['results'] = rtm_sub['bool_val'].map(bool_dict)

    return rtm_sub


def load_metrics(new_metrics_file):
    # new metrics from R&D group
    # will be pushed to LIMS in the future
    nm = pd.read_excel(new_metrics_file, sheet_name='Sheet1')
    d2 = {c: normalize_name(c) for c in nm.columns}
    nm.rename(columns=d2, inplace=True)
    return nm


def output_results(output_file, rpt, tmqc):
    with pd.ExcelWriter(output_file) as writer:
        rpt.to_excel(writer, sheet_name='tab3')
        tmqc.to_excel(writer, sheet_name='tm_qc')


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
