"""
Collection of column lists to construct other columnns.

Preserved columm order should look like this
tmqc_90x_cols = (
    [
        # report tab3 'Production Metrics'
        "sample_id",
        "collection",
        "pf_hq_aligned_q20_bases",
        "mean_insert_size",
        "average_coverage",
        "wgs_het_snp_q",
        "wgs_het_snp_sensitivity",
        "per_ten_coverage_bases",
        "per_twenty_coverage_bases",
    ]
    + NM_90X_COLS
    + [
        "q20_bases",
        "contamination_pct",
        # internal qc only
        "unique_aligned_gb",
        "aligned_bases_pct",
        "chimeric_rate",
        # jw_note
        "merge_name",
        "merge_finished_date",
        "results_path",
        "results",
    ]
)
"""

# Input columns

SE_ONLY_COLS = [
    # construct lane_barcode
    "flowcell_id",
    "lane_num",
    "index_id",
    "work_order_id",  # extract abbrev
    "collaborator_sample_id",
    "sample_internal_id",  # rename to sample_id
    "unique_aligned",  # calculate unique_aligned_gb
    # dates
    "flowcell_create_date" "run_start_date",
    "run_finished_date",
    "analysis_start_date",
    "bwa_analysis_finished_date",
    "analysis_finished_date",  # checking for completion
]


MERGE_ONLY_COLS = [
    "unique_aligned_bases",  # internal qc only
    "merge_name",
    "merge_finished_date",
]


# TODO: better name for constants
INTERSECT_COLS = [
    "results_path",
    "average_coverage",
    "aligned_bases_pct",  # internal qc only
    "chimeric_rate",  # internal qc only
    "per_ten_coverage_bases",
    "per_twenty_coverage_bases",
    "q20_bases",
    "contamination_rate",
]


NM_COLS = [
    "mean_insert_size",  # corrected column name & value in Exemplar LIMS
    "pf_hq_aligned_q20_bases",
    "wgs_het_snp_q",
    "wgs_het_snp_sensitivity",
]


NM_90X_COLS = [
    "per_sixty_coverage_bases",
    "per_seventy_coverage_bases"
]


# Output columns

WKT3_COLS = [
    # weekly report tab3 'Production Metrics'
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


INTERNAL_QC_COLS = [
    # internal qc only
    "unique_aligned_gb",
    "aligned_bases_pct",
    "chimeric_rate",
]


MERGE_NOTE_COLS = [
    # jw_note only
    "merge_name",
    "merge_finished_date",
    "results_path",
    "results",
]


SE_NOTE_COLS = [
    # jw_note only
    "lane_barcode",
    "analysis_finished_date",
    "results_path",
    "results",
]


# Construct Columns

rpt_se_cols = SE_ONLY_COLS + INTERSECT_COLS + NM_COLS
tmqc_se_cols = WKT3_COLS + INTERNAL_QC_COLS + SE_NOTE_COLS

tmqc_90x_cols = WKT3_COLS[:]  # make a new copy
tmqc_90x_cols[-3:-3] = NM_90X_COLS
tmqc_90x_cols += INTERNAL_QC_COLS + MERGE_NOTE_COLS
