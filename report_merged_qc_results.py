
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


import re

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


# In[3]:


rtm = pd.read_excel('2019-02-22_RecentTOPMedMerges.xlsx', sheet_name='table ref')


# In[4]:


rtm_column_names = []

for col_name in rtm.columns:
    rtm_column_names.append(col_name)


# In[5]:


# normalize column names

rtm_new_column_names = []

for col_name in rtm.columns:
    col_name = normalize_name(col_name)
    rtm_new_column_names.append(col_name)


# In[6]:


d1 = {c: normalize_name(c) for c in rtm.columns}


# In[7]:


rtm.rename(columns=d1, inplace=True)


# In[8]:


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


# In[9]:


rtm_sub = rtm.loc[:,tm_cols]


# In[10]:


sid = rtm_sub['merge_name'].str.split('_', n=5, expand=True)[3]


# In[11]:


rtm_sub['sample_id'] = sid.copy()


# In[12]:


# convert contamination_rate to contamination_pct

rtm_sub['contamination_pct'] = (rtm_sub['contamination_rate'] * 100)


# In[13]:


# aligned_bases (CN)
# duplicate_bases (DC)

# pandas broadcasting operateion
# val1_minus_val10 = df["Val1"] - df["Val10"]
# df['Val_Diff'] = df['Val10'] - df['Val1']

# unique_aligned_bases = aligned_bases - duplicate_bases # Exemplar RT 13348
# unique_aligned_gb = unique_aligned_bases / 1_000_000_000
rtm_sub['unique_aligned_gb'] = (rtm_sub['aligned_bases'] - rtm_sub['duplicate_bases']) / 1_000_000_000


# In[14]:


# TODO
# results (PASS or FAIL)


# ## new metrics (KW)

# In[15]:


nm = pd.read_excel('Topmed_harvard_batch_1_KW.xlsx', sheet_name='Sheet1')


# In[16]:


d2 = {c: normalize_name(c) for c in nm.columns}


# In[17]:


nm.rename(columns=d2, inplace=True)


# ### merge dataframes (merge_sub, nm)

# In[18]:


# m = pd.merge(at_sub, appl_sub, how = 'outer', left_on=['Prefix'], right_on=['Midpool suffix'])

m = pd.merge(rtm_sub, nm, how='outer', left_on='sample_id', right_on='sample_id')


# In[19]:


# fill column 'collection' with a value

m['collection'] = 'Harvard SCD'

# new: metrics from Kim Wlker's group

Week
External ID # extract from merge_name
Collection # cohort?
PF HQ Aligned Q20 Bases # new
Mean Insert Size (Library AVG) # new
Mean Coverage (Raw) # Average Coverage?
WGS HET SNP Q # new
WGS HET SNP SENSITIVITY # new
Per 10 Coverage Bases
Per 20 Coverage Bases
Q20 Bases
Contamination % # convert Contamination Rate to Contamination %
Notes
# In[20]:


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


# In[21]:


tmqc = m[tm_cols]


# In[22]:


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


# In[23]:


rpt = m[rpt_cols]


# In[24]:


# If you wish to write to more than one sheet in the workbook, 
# it is necessary to specify an ExcelWriter object

# df2 = df1.copy()
# with pd.ExcelWriter('output.xlsx') as writer:  # doctest: +SKIP
#     df1.to_excel(writer, sheet_name='Sheet_name_1')
#     df2.to_excel(writer, sheet_name='Sheet_name_2')


# In[25]:


with pd.ExcelWriter('weekly3.xlsx') as writer:
    rpt.to_excel(writer, sheet_name='tab3')
    tmqc.to_excel(writer, sheet_name='tm_qc')

