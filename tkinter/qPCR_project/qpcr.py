import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use("TkAgg")

def read_excel(path,sheetName='Results',skipRows=38):
  # create df
  df = pd.read_excel(path, sheet_name='Results', skiprows=38)
  df = df.dropna(axis=1, how='all')
  # dict_subSamples: dict of samples which must split into different df by substrings of sample names
  df_CT_Result_table, df_CtSD_errors = create_ResultTable_from_df_by_removing_H2O_SampleNames_and_Undetermined_CT_and_create_CtSD_errors_by_filter_CtSD_more_than_0p6(
    df)
  df_CT_Result_table = remove_outlyer_CTs_from_df_CT_Result_table(df_CT_Result_table, df_CtSD_errors)
  df_pivot = create_pivotTable_from_df_clean_CT_Result_table(df_CT_Result_table)
  return df_CT_Result_table, df_pivot
"""**Check Ct SD more than 0.5**"""


def create_ResultTable_from_df_by_removing_H2O_SampleNames_and_Undetermined_CT_and_create_CtSD_errors_by_filter_CtSD_more_than_0p6(df_CT_Result_table):
  df_CT_Result_table = df_CT_Result_table[df_CT_Result_table['Sample Name'] != 'H2O']
  df_CT_Result_table = df_CT_Result_table[df_CT_Result_table['CT'] != 'Undetermined']
  df_CtSD_errors = df_CT_Result_table[df_CT_Result_table['Ct SD'] > 0.6][['Well Position','Sample Name','Target Name','CT','Ct SD']]
  df_CtSD_errors.loc[:,'Ct SD'] = df_CtSD_errors['Ct SD'].round(3)
  return df_CT_Result_table, df_CtSD_errors

def find_outlyer(list_numbers):
  mean_list = sum(list_numbers)/len(list_numbers)
  big_distanse = 0
  outlier = list_numbers[0]
  for i in list_numbers:
    if abs(i-mean_list) > big_distanse:
      big_distanse = abs(i-mean_list)
      outlier = i
  return outlier

def remove_outlyer_CTs_from_df_CT_Result_table(df_CT_Result_table,df_CtSD_errors):
  for ct_sd in df_CtSD_errors['Ct SD'].unique():
    current_sery = df_CtSD_errors[df_CtSD_errors['Ct SD'] == ct_sd]['CT']
    outlier = find_outlyer(current_sery.values)
    index2drop = df_CtSD_errors[df_CtSD_errors['CT'] == outlier].index
    df_CT_Result_table.drop(index2drop, inplace=True)
  return df_CT_Result_table


def create_pivotTable_from_df_clean_CT_Result_table(df_CT_Result_table):
  df_pivot = df_CT_Result_table.pivot_table(
    index='Sample Name',
    columns='Target Name',
    values='CT',
     aggfunc='mean')
  return df_pivot


def get_sampleNames_from_df_pivot_which_contain_str(dataFrame,list_str):
  res = []
  for target in list_str:
    res.extend(dataFrame.index[dataFrame.index.str.contains(target)])
  return res

def create_DataFramesDict_by_sampleNames_from_pivot_Df(df_pivot,dict_samples):
  dicts_of_dfSamplegroups = {}
  for k,values in dict_samples.items():
    dicts_of_dfSamplegroups[k] = df_pivot.loc[values]
    dicts_of_dfSamplegroups[k].dropna(axis=1,inplace=True)
  return dicts_of_dfSamplegroups


# ΔCt = Ct(target) − Ct(reference).

# ΔΔCt = ΔCt(sample) − ΔCt(control).

# Fold change = 2^(−ΔΔCt).

def create_fold_change_values_and_FoldChange_columnsName(targetDf,ref_gene_cols:list,sample_controls:list):
  listFoldChange_columnsName = set()
  for col in targetDf.columns:
    # print(targetDf[ref_gene_cols].mean(axis=1))
    targetDf[f'delta_{col}'] = targetDf[col] - targetDf[ref_gene_cols].mean(axis=1)
    targetDf[f'deltaDelta_{col}'] = targetDf[f'delta_{col}'] - targetDf.loc[sample_controls,f'delta_{col}'].mean()
    targetDf[f'foldChange_{col}'] = 2**(-targetDf[f'deltaDelta_{col}'])
    FoldChange_columnName = f'foldChange_{col}'
    listFoldChange_columnsName.add(FoldChange_columnName)
  return listFoldChange_columnsName




def barplot_foldChange(dicts_of_dfSamplegroups,listFoldChangeNames,listFilterOutFoldChanges=['foldChange_POL2A'],SaveDIR='./'):
  # White background
  plt.style.use("default")

  for target_key in dicts_of_dfSamplegroups.keys():
    target_df = dicts_of_dfSamplegroups[target_key]
    # Select xlabels and values
    xlabels = target_df.index.values

    for foldChange_col in listFoldChangeNames:
      if foldChange_col in listFilterOutFoldChanges:
        continue
      values = target_df[foldChange_col].values

      fig, ax = plt.subplots(figsize=(15, 10))

      # Use a colormap (viridis)
      cmap = plt.get_cmap("viridis")
      colors = [cmap(i / len(values)) for i in range(len(values))]

      # Barplot
      bars = ax.bar(xlabels, values, width=0.4, color=colors)

      # Add labels on bars
      for i, v in enumerate(values):
        ax.text(i, v + 0.05 * max(values), f"{v:.2f}",
                ha='center', va='bottom', fontsize=12, fontweight='bold')

      # Title and labels
      ax.set_title(f"{foldChange_col} in {target_key}", fontsize=20, fontweight='bold', pad=20)
      ax.set_ylabel("Fold Change", fontsize=20, labelpad=15, fontweight='bold')
      ax.set_xlabel("Samples", fontsize=20, labelpad=15, fontweight='bold')

      # Rotate x-axis labels for readability
      ax.set_xticks(range(len(xlabels)))
      ax.set_xticklabels(xlabels, rotation=45, ha="right", fontsize=15, fontweight='bold')

      # Grid (horizontal only, like seaborn whitegrid)
      ax.grid(True, which="major", axis="y", linestyle="--", linewidth=0.7, alpha=0.7)

      # Clean up spines
      for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

      plt.tight_layout()
      plt.savefig(SaveDIR + f'{foldChange_col} in {target_key}.png', dpi=300, bbox_inches="tight")
      # plt.show()
# def barplot_foldChange(dicts_of_dfSamplegroups,listFoldChangeNames,listFilterOutFoldChanges=['foldChange_POL2A'],SaveDIR='./'):
#   import matplotlib.pyplot as plt
#   import seaborn as sns
#   # Use a clean style
#   plt.style.use("seaborn-v0_8-whitegrid")
#   for target_key in dicts_of_dfSamplegroups.keys():
#     target_df = dicts_of_dfSamplegroups[target_key]
#     # Select xlabels and values
#     xlabels = target_df.index.values
#     for foldChange_col in listFoldChangeNames:
#       if foldChange_col in listFilterOutFoldChanges:
#         continue
#       values = target_df[foldChange_col].values
#
#       fig, ax = plt.subplots(figsize=(15, 10))
#       # Barplot with better colors
#       sns.barplot(x=xlabels, y=values, ax=ax, palette="viridis", width=0.4,)
#
#       # Add labels on bars
#       for i, v in enumerate(values):
#           ax.text(i, v + 0.05 * max(values), f"{v:.2f}",
#                   ha='center', va='bottom', fontsize=12, fontweight='bold')
#
#       # Title and labels
#       ax.set_title(f"{foldChange_col} in {target_key}", fontsize=20, fontweight='bold', pad=20)
#       ax.set_ylabel("Fold Change", fontsize=20, labelpad=15,fontweight='bold')
#       ax.set_xlabel("Samples", fontsize=20, labelpad=15,fontweight='bold')
#
#       # Rotate x-axis labels for readability
#       ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=15,fontweight='bold')
#
#       # Clean up spines
#       sns.despine()
#
#       plt.tight_layout()
#       plt.savefig(SaveDIR + f'{foldChange_col} in {target_key}.png')
#       # plt.show()

def savefoldChangePlots_by_df_pivot(df_pivot,dict_subSamples:dict[list],listReferenceGeneName:list,listControlSamples:list[list],listFilterOutFoldChanges=['foldChange_POL2A'],SaveDIR='./'):
  dicts_of_dfSamplegroups = {}
  for DfName,listsearch in dict_subSamples.items():
    dicts_of_dfSamplegroups[DfName] = get_sampleNames_from_df_pivot_which_contain_str(df_pivot,listsearch)
  dicts_of_dfSamplegroups = create_DataFramesDict_by_sampleNames_from_pivot_Df(df_pivot,dicts_of_dfSamplegroups)
  # Edit each df in dicts_of_dfSamplegroups by related RefrenceGeneName & ControlSamples
  for ind,target_key in enumerate(dicts_of_dfSamplegroups.keys()):
    listFoldChangeNames = create_fold_change_values_and_FoldChange_columnsName(dicts_of_dfSamplegroups[target_key],listReferenceGeneName[ind],listControlSamples[ind])
  # create dict of df names : Fold Change column names
  barplot_foldChange(dicts_of_dfSamplegroups,listFoldChangeNames,listFilterOutFoldChanges,SaveDIR=SaveDIR)
  return dicts_of_dfSamplegroups,listFoldChangeNames


def plot_target_foldChangeDFs(path,dict_subSamples:dict[list],listReferenceGeneName:list,listControlSamples:list[list],listFilterOutFoldChanges=['foldChange_POL2A'],SaveDIR='./'):
  # create df
  df = pd.read_excel(path,sheet_name='Results',skiprows=38)
  df = df.dropna(axis=1,how='all')
  # dict_subSamples: dict of samples which must split into different df by substrings of sample names
  df_CT_Result_table, df_CtSD_errors = create_ResultTable_from_df_by_removing_H2O_SampleNames_and_Undetermined_CT_and_create_CtSD_errors_by_filter_CtSD_more_than_0p6(df)
  df_CT_Result_table = remove_outlyer_CTs_from_df_CT_Result_table(df_CT_Result_table,df_CtSD_errors)
  df_pivot = create_pivotTable_from_df_clean_CT_Result_table(df_CT_Result_table)
  dicts_of_dfSamplegroups = {}
  for DfName,listsearch in dict_subSamples.items():
    dicts_of_dfSamplegroups[DfName] = get_sampleNames_from_df_pivot_which_contain_str(df_pivot,listsearch)
  dicts_of_dfSamplegroups = create_DataFramesDict_by_sampleNames_from_pivot_Df(df_pivot,dicts_of_dfSamplegroups)
  # Edit each df in dicts_of_dfSamplegroups by related RefrenceGeneName & ControlSamples
  for ind,target_key in enumerate(dicts_of_dfSamplegroups.keys()):
    listFoldChangeNames = create_fold_change_values_and_FoldChange_columnsName(dicts_of_dfSamplegroups[target_key],listReferenceGeneName[ind],listControlSamples[ind])
  print(listFoldChangeNames)
  print(dicts_of_dfSamplegroups)
  # create dict of df names : Fold Change column names
  barplot_foldChange(dicts_of_dfSamplegroups,listFoldChangeNames,listFilterOutFoldChanges,SaveDIR=SaveDIR)
  return dicts_of_dfSamplegroups,listFoldChangeNames

# path = "/content/QPCR FH.xls"
# path2 = "/content/Anaysis-second batch sep2 2025.xls"
# dict_subSamples = {'df_SIRNA':['CTR','siRNA' ],'df_Starved':['Starved','PC12-EB','VLP1','Differentiated']}
# listRefrenceGeneName = [['POL2A'],['POL2A']]
# listControlSamples = [['PC12-CTR-SIRNA'], ['PC12-Starved']]
# dicts_of_dfSamplegroups2, dict_listFoldChangeNames2 = plot_target_foldChangeDFs(path,dict_subSamples,listRefrenceGeneName,listControlSamples)

"""# Melt curve"""

# meltCurve_df = pd.read_excel('/content/Anaysis-second batch sep2 2025.xls',sheet_name='Melt Curve Raw Data',skiprows=38)
# meltCurve_df.head(2)
#
# def get_sampleNames_by_Well_Position(Well_Position):
#   return df[df['Well Position'] == Well_Position]['Sample Name'].values[0]
# get_sampleNames_by_Well_Position('B2')
#
# meltCurve_df['Sample Name'] = meltCurve_df.apply(lambda row: get_sampleNames_by_Well_Position(row['Well Position']),axis=1)
# meltCurve_df.head()
#
# plt.plot(meltCurve_df['Temperature'],meltCurve_df['Derivative'])
# plt.show()
#
# df.head()