#!/usr/bin/env python

"""
Inputs a single input file 'Exemplar Merge Report'
and generates an XLSX workbook with two sheets.

tab3: weekly report tab3 'Production Metrics'
tm_qc: QC data metrics with results PASS or FAIL

New TOPMed metrics be added to Exemplar LIMS merge report:
- PF_HQ_Aligned_Q20_Bases
- MEAN_INSERT_SIZE  # corrected value for Mean Insert Size (Library AVG)
- WGS_HET_SNP_Q
- WGS_HET_SNP_SENSITIVITY
"""

import argparse
import re

from collections import defaultdict

import pandas as pd


SUB_COLS = [
    "merge_name",
    "merge_finished_date",
    "results_path",
    "unique_aligned_bases",  # qc only
    "aligned_bases_pct",  # qc only
    "average_coverage",
    "chimeric_rate",  # qc only
    "per_ten_coverage_bases",
    "per_twenty_coverage_bases",
    "q20_bases",
    "contamination_rate",
    # new metrics
    "wgs_het_snp_q",
    "mean_insert_size",
    "wgs_het_snp_sensitivity",
    "pf_hq_aligned_q20_bases",
]

TM_COLS = [
    # weekly_report
    "sample_id",
    "collection",
    "pf_hq_aligned_q20_bases",
    "mean_insert_size",
    "average_coverage",
    "wgs_het_snp_q",
    "wgs_het_snp_sensitivity",
    "per_ten_coverage_bases",
    "per_twenty_coverage_bases",
    "q20_bases",
    "contamination_pct",
    # qc only
    "unique_aligned_gb",
    "aligned_bases_pct",
    "chimeric_rate",
    "merge_name",
    "merge_finished_date",
    "results_path",
    "results",
]

RPT_COLS = [
    "sample_id",
    "collection",
    "pf_hq_aligned_q20_bases",
    "mean_insert_size",
    "average_coverage",
    "wgs_het_snp_q",
    "wgs_het_snp_sensitivity",
    "per_ten_coverage_bases",
    "per_twenty_coverage_bases",
    "q20_bases",
    "contamination_pct",
]

# map abbrev (from merge_name in input report) to the Study/Cohort name
COLLECTION_LIST = [
    ("Legacy", "TOPMed Control"),
    ("TMCONT", "TOPMed Control"),
    ("TMHASC", "Harvard SCD"),
    ("TMCGVC", "Causal Genetic Variants of Cardiomyopathy"),
    ("TMGCUC", "Genetic Causes of Unexplained Cardiomyopathies"),
    ("TMREDS", "Sickle Cell Disease REDS III"),
]


def main():
    args = parse_args()
    run(args.recent_merge_report, args.output_file)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "recent_merge_report",
        help="*.xlsx, usually downloaded from Exemplar LIMS",
    )
    parser.add_argument("output_file", help="should end with .xlsx")
    args = parser.parse_args()
    return args


def run(recent_merge_report, output_file):
    rtm_sub = load_merge_report(recent_merge_report)
    # TODO track weeks
    # will contain output for at least the last 4 weeks along with metrics
    rpt = rtm_sub[RPT_COLS]
    tmqc = rtm_sub[TM_COLS]
    output_results(output_file, rpt, tmqc)


def load_merge_report(recent_merge_report):
    rtm = pd.read_excel(recent_merge_report, sheet_name="table ref")

    # normalize column names
    d1 = {c: normalize_name(c) for c in rtm.columns}
    rtm.rename(columns=d1, inplace=True)

    # use loc to avoid warning message
    rtm_sub = rtm.loc[:, SUB_COLS]

    # extract abbrev from merge_name
    cid = rtm_sub["merge_name"].str.split("_", n=5, expand=True)[2]
    # add default value using defaultdict
    d2 = defaultdict(lambda: None)
    d2.update(COLLECTION_LIST)
    # add a column 'collection'
    rtm_sub["collection"] = cid.map(d2)

    # extract sample_id from merge_name
    sid = rtm_sub["merge_name"].str.split("_", n=5, expand=True)[3]
    rtm_sub["sample_id"] = sid

    # convert contamination_rate to contamination_pct
    rtm_sub["contamination_pct"] = rtm_sub["contamination_rate"] * 100

    # pandas broadcasting operation
    rtm_sub["unique_aligned_gb"] = (
        rtm_sub["unique_aligned_bases"]
    ) / 1_000_000_000

    # add qc results 'PASS' or 'FAIL'
    # Negative checks, should all be False
    n1 = rtm_sub["unique_aligned_gb"] < 90.0
    n2 = rtm_sub["aligned_bases_pct"] < 90.0
    n3 = rtm_sub["average_coverage"] < 30.0
    n4 = rtm_sub["per_ten_coverage_bases"] < 95.0
    n5 = rtm_sub["per_twenty_coverage_bases"] < 90.0
    n6 = rtm_sub["q20_bases"] < 87_000_000_000
    # Positive checks, should all be True
    p1 = rtm_sub["contamination_pct"] < 3.0
    p2 = rtm_sub["chimeric_rate"] < 5.0
    # Combined
    all_checks_good = p1 & p2 & ~(n1 | n2 | n3 | n4 | n5 | n6)
    rtm_sub["results"] = all_checks_good.map({True: "PASS", False: "FAIL"})

    return rtm_sub


def output_results(output_file, rpt, tmqc):
    with pd.ExcelWriter(output_file) as writer:
        rpt.to_excel(writer, sheet_name="tab3", index=False)
        tmqc.to_excel(writer, sheet_name="tm_qc", index=False)


def normalize_name(field_name):
    """lowercase with underscores, etc"""
    fixes = (
        (r"/", "_per_"),
        (r"%", "_pct_"),
        (r"\W", "_"),
        (r"^_+", ""),  # remove '_' if field_name begins with '_'
        (r"_+$", ""),
        (r"__+", "_"),
    )
    result = field_name.strip().lower() or None
    # result = field_name.strip().upper() or None
    if result:
        if result.endswith("?"):
            if not re.match(r"is[_\W]", result):
                result = "is_" + result
        for pattern, replacement in fixes:
            result = re.sub(pattern, replacement, result)
    return result


if __name__ == "__main__":
    main()
