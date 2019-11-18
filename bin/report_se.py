#!/usr/bin/env python

"""
Inputs Exemplar Illumina Breakdown report
and generates an Excel workbook with two sheets.

tab3: weekly report tab3 'Production Metrics'
tmqc: QC data metrics with results PASS or FAIL
"""

# First come standard libraries, in alphabetical order
import argparse
from collections import defaultdict
import re

# After a blank line, import third-party libraries
import pandas as pd

# After another blank line, import local libraries
from utils import normalize_name
from rpt_columns import rpt_se_cols, WKT3_COLS, tmqc_se_cols


# TODO add abbrev for newly assigned study Walk-PHaSST SCD & PCGC
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "recent_merge_report",
        help="*.xlsx, usually generated from Exemplar LIMS",
    )
    parser.add_argument("output_file", help="should end with .xlsx")
    args = parser.parse_args()
    return args


def run(recent_exemplar_ib_report, output_file):
    rtm_sub = load_exemplar_ib_report(recent_exemplar_ib_report)
    results = qc_results(rtm_sub)
    # TODO track weeks
    # will contain output for at least the last 4 weeks along with metrics
    wkt3 = results[WKT3_COLS]
    tmqc = results[tmqc_se_cols]
    output_results(output_file, wkt3, tmqc)


def load_exemplar_ib_report(recent_exemplar_ib_report):
    rtm = pd.read_excel(recent_exemplar_ib_report, sheet_name="ib_report")
    # fillna for missing values
    rtm.fillna(method="ffill")
    # normalize column names
    d1 = {c: normalize_name(c) for c in rtm.columns}
    rtm.rename(columns=d1, inplace=True)
    # use loc to avoid SettingWithCopyWarning warning message
    rtm_sub = rtm.loc[:, rpt_se_cols]
    # rename sample_id
    d2 = {"sample_internal_id": "sample_id"}
    rtm_sub.rename(columns=d2, inplace=True)
    # extract abbrev
    cid = rtm_sub["work_order_id"].str.split("_", n=-1, expand=True)[0]
    # add a column collection
    d3 = defaultdict(lambda: None)
    d3.update(COLLECTION_LIST)
    rtm_sub["collection"] = cid.map(d3)
    # create lane_barcode
    rtm_sub["lane_barcode"] = (
        rtm_sub["flowcell_id"]
        + "-"
        + rtm_sub["lane_num"].astype(str)
        + "-"
        + rtm_sub["index_id"]
    )
    # convert contamination_rate to contamination_pct
    rtm_sub["contamination_pct"] = rtm_sub["contamination_rate"] * 100
    # pandas broadcasting operation
    rtm_sub["unique_aligned_gb"] = (rtm_sub["unique_aligned"]) / 1_000_000_000
    return rtm_sub


def qc_results(rtm_sub):
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


def output_results(output_file, wkt3, tmqc):
    with pd.ExcelWriter(output_file) as writer:
        wkt3.to_excel(writer, sheet_name="tab3", index=False)
        tmqc.to_excel(writer, sheet_name="tm_qc", index=False)


if __name__ == "__main__":
    main()
