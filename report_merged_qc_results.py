#!/usr/bin/env python

"""Combines output weekly merge report (from QC group) with new metrics report
(from R&D group) and generates an Excel workbook with two sheets."""

import argparse
import re

import pandas as pd


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
    rtm = pd.read_excel(recent_merge_report, sheet_name='table ref')


    rtm_column_names = []

    for col_name in rtm.columns:
        rtm_column_names.append(col_name)


    # normalize column names

    rtm_new_column_names = []

    for col_name in rtm.columns:
        col_name = normalize_name(col_name)
        rtm_new_column_names.append(col_name)


    d1 = {c: normalize_name(c) for c in rtm.columns}


    rtm.rename(columns=d1, inplace=True)


    tm_cols = [
        'merge_name',
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


    rtm_sub = rtm.loc[:,tm_cols]


    sid = rtm_sub['merge_name'].str.split('_', n=5, expand=True)[3]


    rtm_sub['sample_id'] = sid.copy()


    # convert contamination_rate to contamination_pct

    rtm_sub['contamination_pct'] = (rtm_sub['contamination_rate'] * 100)


    # aligned_bases (CN)
    # duplicate_bases (DC)

    # pandas broadcasting operateion
    # val1_minus_val10 = df["Val1"] - df["Val10"]
    # df['Val_Diff'] = df['Val10'] - df['Val1']

    # unique_aligned_bases = aligned_bases - duplicate_bases # Exemplar RT 13348
    # unique_aligned_gb = unique_aligned_bases / 1_000_000_000
    rtm_sub['unique_aligned_gb'] = (rtm_sub['aligned_bases'] - rtm_sub['duplicate_bases']) / 1_000_000_000


    # TODO
    # results (PASS or FAIL)


    # ## new metrics (KW)

    nm = pd.read_excel(new_metrics_file, sheet_name='Sheet1')


    d2 = {c: normalize_name(c) for c in nm.columns}


    nm.rename(columns=d2, inplace=True)


    # ### merge dataframes (merge_sub, nm)

    # m = pd.merge(at_sub, appl_sub, how = 'outer', left_on=['Prefix'], right_on=['Midpool suffix'])

    m = pd.merge(rtm_sub, nm, how='outer', left_on='sample_id', right_on='sample_id')


    # fill column 'collection' with a value

    m['collection'] = 'Harvard SCD'

    # new: metrics from Kim Wlker's group

    # Week
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

    tm_cols = [
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
        'merge_cram_path'
        # results # TODO
    ]


    tmqc = m[tm_cols]


    rpt_cols = [
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


    rpt = m[rpt_cols]


    # If you wish to write to more than one sheet in the workbook, 
    # it is necessary to specify an ExcelWriter object

    # df2 = df1.copy()
    # with pd.ExcelWriter('output.xlsx') as writer:  # doctest: +SKIP
    #     df1.to_excel(writer, sheet_name='Sheet_name_1')
    #     df2.to_excel(writer, sheet_name='Sheet_name_2')


    with pd.ExcelWriter(output_file) as writer:
        rpt.to_excel(writer, sheet_name='tab3')
        tmqc.to_excel(writer, sheet_name='tm_qc')


def normalize_name(field_name):
    """lowercase with underscores, etc"""
    fixes = (
        (r'/', '_per_'),
        (r'%', '_pct_'),
        (r'\W', '_'),
        (r'^_+', ''),
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
