#!/usr/bin/env python3

"""Inputs Production Metrics (tab3) of BCM HGSC TOPMed Weekly Report
and generates an Excel workbook with project average metrics by Collection"""

# First come standard libraries, in alphabetical order
import argparse
import re

# After a blank line, impport third-party libraries
import pandas as pd

# After another blank line, import third-party libraries
from .utils import normalize_name
from .version import __version__


# display.precision sets the output display precision in terms of decimal places
pd.set_option("precision", 4)


def main():
    args = parse_args()
    run(args.weekly_report, args.output_file)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "weekly_report",
        help="*.xlsx, usually sheet_name is Production Metrics" " in tab3",
    )
    parser.add_argument(
        "output_file",
        help="*.xlsx, outputs Project Averages in tab4 for" " Weekly Report",
    )
    parser.add_argument("--version", action="version",
                        version="%(prog)s {}".format(__version__))
    args = parser.parse_args()
    return args


def run(weekly_report, output_file):
    # Production Metrics
    pm = pd.read_excel(weekly_report, sheet_name="Production Metrics")

    col_dict = {c: normalize_name(c) for c in pm.columns}
    pm.rename(columns=col_dict, inplace=True)
    # groupby
    pm_gr = pm.groupby(["collection"]).mean()
    # reorder columns
    avg_cols = [
        "mean_insert_size_library_avg",
        "mean_coverage_raw",
        "per_10_coverage_bases",
        "per_20_coverage_bases",
        "q20_bases",
        "contamination_pct",
    ]
    pm_gr_av = pm_gr[avg_cols]
    # write to excel with float_format
    pm_gr_av.to_excel(output_file, sheet_name="tab4", float_format="%.4f")


if __name__ == "__main__":
    main()
