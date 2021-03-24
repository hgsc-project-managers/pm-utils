"""
Add modules that are shared in other scripts.
"""

# First come standard libraries, in alphabetical order
import csv
from collections import defaultdict
import logging
import re

# After a blank line, import third-party libraries
import pandas as pd

# After another blank line, import local libraries
from .utils import normalize_name
from .rpt_columns import rpt_merge_cols
from .mappings import STUDY_MAPPING

logger = logging.getLogger("utils in pm_utils")


def load_merge_report(recent_merge_report):
    rtm = pd.read_excel(recent_merge_report, sheet_name="merge_report")
    # normalize column names
    d1 = {c: normalize_name(c) for c in rtm.columns}
    rtm.rename(columns=d1, inplace=True)
    # use loc to avoid SettingWithCopyWarning message
    rtm_sub = rtm.loc[:, rpt_merge_cols]
    # parse project abbrev & sample_id from merge_name
    decode  = rtm_sub["merge_name"].apply(decode_merge_name)
    rtm_sub[["collection", "sample_id"]] = pd.DataFrame(
    decode.tolist(), index=rtm_sub.index
    )
    cid = rtm_sub["collection"]
    # add default value using defaultdict
    d2 = defaultdict(lambda: None)
    d2.update(STUDY_MAPPING)
    # add a column 'collection'
    rtm_sub["collection"] = cid.map(d2)
    # convert contamination_rate to contamination_pct
    rtm_sub["contamination_pct"] = rtm_sub["contamination_rate"] * 100
    # pandas broadcasting operation
    rtm_sub["unique_aligned_gb"] = (
        rtm_sub["unique_aligned_bases"]
    ) / 1_000_000_000
    return rtm_sub


TIMESTAMP_PAT = r"\d{4}-\d\d-\d\dT\d{4,6}"
PROJECT_PAT = r"TM[A-Z]{4}"
SAMPLE_PAT = r"NWD\d{6}"
SEQUENCE_PAT = r"\d{6}_\d"
FLOWCELL_PAT = r"[A-Z0-9]{9}"
LIB_PAT = fr"(IL[A-Z]{{3}})_({PROJECT_PAT})_({SAMPLE_PAT})_{SEQUENCE_PAT}"

MERGE_PAT_STANDARD = re.compile(
    f"(?:{TIMESTAMP_PAT})_{LIB_PAT}-FLOWCELL(?:(?:-{FLOWCELL_PAT})+)$"
)
MERGE_PAT_SPECIAL = re.compile(f"({SAMPLE_PAT})-LIB((?:-{LIB_PAT})+)")
MERGE_PAT_NEW = re.compile(
    fr"({PROJECT_PAT})\.({SAMPLE_PAT})-\d_\dAMP-FLOWCELL(?:(?:-{FLOWCELL_PAT})+)$"
)


def standard_merge_rule(merge_name: str) -> tuple:
    m = MERGE_PAT_STANDARD.match(merge_name)
    if not m:
        return None, None
    _, project, sample = m.groups()
    return project, sample


def special_merge_rule(merge_name: str) -> tuple:
    m = MERGE_PAT_SPECIAL.match(merge_name)
    if not m:
        return None, None
    sample, libs_string = m.groups()[:2]
    lib_strings = libs_string.split("-")[1:]
    decoded = [re.match(LIB_PAT, l).groups() for l in lib_strings]
    library_types = set(d[0] for d in decoded)
    projects = set(d[1] for d in decoded)
    samples = set([sample] + [d[2] for d in decoded])
    errors = False
    if len(library_types) > 1:
        logger.error(f"inconsistent library types {library_types} in {merge_name}")
        errors = True
    if len(projects) > 1:
        logger.error(f"inconsistent projects {projects} in {merge_name}")
        errors = True
    if len(samples) > 1:
        logger.error(f"inconsistent samples {samples} in {merge_name}")
        errors = True
    if errors:
        return None, None
    return projects.pop(), samples.pop()


def new_merge_rule(merge_name: str) -> tuple:
    m = MERGE_PAT_NEW.match(merge_name)
    if not m:
        return None, None
    project, sample = m.groups()

    return project, sample


RULES = [standard_merge_rule, special_merge_rule, new_merge_rule]


def decode_merge_name(merge_name: str) -> tuple:
    for rule in RULES:
        project, sample = rule(merge_name)
        if project:
            return project, sample
    logger.error(f"Cannot decode merge name '{merge_name}'")
    return None, None
