import pandas as pd
import matplotlib.pyplot as plt
import os
# import matplotlib
# matplotlib.use("TkAgg")

def create_ResultTable_from_df_by_removing_H2O_SampleNames_and_Undetermined_CT_and_create_CtSD_errors_by_filter_CtSD_more_than_0p6(df_CT_Result_table):
  df_CT_Result_table = df_CT_Result_table[df_CT_Result_table['Sample Name'] != 'H2O']
  df_CT_Result_table = df_CT_Result_table[df_CT_Result_table['Sample Name'] != 'h2o']
  df_CT_Result_table = df_CT_Result_table[df_CT_Result_table['CT'] != 'Undetermined']
  df_CtSD_errors = df_CT_Result_table[df_CT_Result_table['Ct SD'] > 0.6][['Well Position','Sample Name','Target Name','CT','Ct SD']]
  df_CtSD_errors.loc[:,'Ct SD'] = df_CtSD_errors['Ct SD'].round(3)
  return df_CT_Result_table, df_CtSD_errors

def remove_outlyer_CTs_from_df_CT_Result_table(df_CT_Result_table,df_CtSD_errors):
  for ct_sd in df_CtSD_errors['Ct SD'].unique():
    current_sery = df_CtSD_errors[df_CtSD_errors['Ct SD'] == ct_sd]['CT']
    outlier = find_outlyer(current_sery.values)
    index2drop = df_CtSD_errors[df_CtSD_errors['CT'] == outlier].index
    df_CT_Result_table.drop(index2drop, inplace=True)
  return df_CT_Result_table

def find_outlyer(list_numbers):
  mean_list = sum(list_numbers)/len(list_numbers)
  big_distanse = 0
  outlier = list_numbers[0]
  for i in list_numbers:
    if abs(i-mean_list) > big_distanse:
      big_distanse = abs(i-mean_list)
      outlier = i
  return outlier

def create_pivotTable_from_df_clean_CT_Result_table(df_CT_Result_table):
  df_pivot = df_CT_Result_table.pivot_table(
    index='Sample Name',
    columns='Target Name',
    values='CT',
     aggfunc='mean')
  return df_pivot
def read_excel(path,sheetName='Results',skipRows=38):
  # create df
  df = pd.read_excel(path, sheet_name=sheetName, skiprows=skipRows)
  df = df.dropna(axis=1, how='all')
  # dict_subSamples: dict of samples which must split into different df by substrings of sample names
  df_CT_Result_table, df_CtSD_errors = create_ResultTable_from_df_by_removing_H2O_SampleNames_and_Undetermined_CT_and_create_CtSD_errors_by_filter_CtSD_more_than_0p6(
    df)
  df_CT_Result_table = remove_outlyer_CTs_from_df_CT_Result_table(df_CT_Result_table, df_CtSD_errors)
  df_pivot = create_pivotTable_from_df_clean_CT_Result_table(df_CT_Result_table)
  return df_CT_Result_table, df_pivot
"""**Check Ct SD more than 0.5**"""
# df_CT_Result_table, df_pivot = read_excel(r"C:\Users\mojij\Downloads\editedSamplenameQpcr2025-10-10.xlsx",sheetName='Results',skipRows=0)
# print(df_CT_Result_table)
# print(df_pivot)









def get_sampleNames_from_df_pivot_which_contain_str(dataFrame,list_str):
  res = []
  for target in list_str:
    res.extend(dataFrame.index[dataFrame.index.str.contains(target,case=False, na=False)])
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
def findRowsOrColumnsIndexByPortionName(df,patterns:list,orientation="columns"):
  if orientation == 'columns':
    mask = df.columns.str.contains('|'.join(patterns), case=False, na=False)
    return [col for col in df.columns[mask].values.tolist()]
  else:
    mask = df.index.str.contains('|'.join(patterns), case=False, na=False)
    return [col for col in df.index[mask].values.tolist()]
def create_fold_change_values_and_FoldChange_columnsName(targetDf,ref_gene_cols:list,sample_controls:list):
  SetFoldChange_columnsName = set()
  for col in targetDf.columns:
    targetDf[f'delta_{col}'] = targetDf[col] - targetDf[ref_gene_cols].mean(axis=1)
    targetDf[f'deltaDelta_{col}'] = targetDf[f'delta_{col}'] - targetDf.loc[sample_controls,f'delta_{col}'].mean()
    targetDf[f'foldChange_{col}'] = 2**(-targetDf[f'deltaDelta_{col}'])
    FoldChange_columnName = f'foldChange_{col}'
    SetFoldChange_columnsName.add(FoldChange_columnName)
  return SetFoldChange_columnsName



def changeLabelName2controlStr(sampleControlNames,xlabels):
  for counter, sample in enumerate(sampleControlNames):
    if sample in xlabels:
      ind = xlabels.index(sample)
      if counter != 0:
        xlabels[ind] = f'Control_{counter}'
      else:
        xlabels[ind] = f'Control'
  return xlabels
def barplot_foldChange(target_key,target_df,listFoldChangeNames,listFilterOutFoldChanges=['foldChange_POL2A'],SaveDIR='./',sampleControlNames=None):
  # White background
  plt.style.use("default")
  # Select xlabels and values
  xlabels = list(target_df.index.values)
  # later work
  if sampleControlNames:
    xlabels = changeLabelName2controlStr(sampleControlNames, xlabels)


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
    # check if output exist
    output_path = SaveDIR + f'{foldChange_col} in {target_key}.png'
    newPath = check_if_outputFile_not_exist_otherwise_return_path(output_path,index=0)
    plt.savefig(newPath, dpi=300, bbox_inches="tight")
    # plt.show()
    print('Done')
def check_if_outputFile_not_exist_otherwise_return_path(path,index=0):
  isfileExist = os.path.isfile(path)
  if isfileExist:
    suffix = os.path.splitext(path)[1]
    beforeSuffix = os.path.splitext(path)[0]
    return check_if_outputFile_not_exist_otherwise_return_path(f"{beforeSuffix}_{index+1}{suffix}",index+1)
  else:
    return path
def savefoldChangePlots_by_df_pivot(df_pivot,dict_subSamples:dict[list],listReferenceGeneName:list,listControlSamples:list[list],listFilterOutFoldChanges=['foldChange_POL2A'],SaveDIR='./',ReplaceSampleControlName2ControlStr=False):
  dicts_of_dfSamplegroups = {}
  for DfName,listSearch in dict_subSamples.items():
    dicts_of_dfSamplegroups[DfName] = get_sampleNames_from_df_pivot_which_contain_str(df_pivot,listSearch)
  dicts_of_dfSamplegroups = create_DataFramesDict_by_sampleNames_from_pivot_Df(df_pivot,dicts_of_dfSamplegroups)
  # Edit each df in dicts_of_dfSamplegroups by related RefrenceGeneName & ControlSamples

  for ind,keyDf_DF in enumerate(dicts_of_dfSamplegroups.items()):
    ref_gene_cols = findRowsOrColumnsIndexByPortionName(keyDf_DF[1], listReferenceGeneName[ind])
    sample_controls = findRowsOrColumnsIndexByPortionName(keyDf_DF[1], listControlSamples[ind], orientation='rows')
    SetFoldChangeNames = create_fold_change_values_and_FoldChange_columnsName(keyDf_DF[1],ref_gene_cols,sample_controls)
    if ReplaceSampleControlName2ControlStr:
      barplot_foldChange(keyDf_DF[0], keyDf_DF[1], SetFoldChangeNames, listFilterOutFoldChanges, SaveDIR=SaveDIR,
                         sampleControlNames=sample_controls)
    else:
      barplot_foldChange(keyDf_DF[0],keyDf_DF[1], SetFoldChangeNames, listFilterOutFoldChanges, SaveDIR=SaveDIR)


def plot_target_foldChangeDFs(path,dict_subSamples:dict[list],listReferenceGeneName:list,listControlSamples:list[list],listFilterOutFoldChanges=['foldChange_POL2A'],SaveDIR='./',ReplaceSampleControlName2ControlStr=False):
  # create df
  df = pd.read_excel(path,sheet_name='Results',skiprows=38)
  df = df.dropna(axis=1,how='all')
  # dict_subSamples: dict of samples which must split into different df by substrings of sample names
  df_CT_Result_table, df_CtSD_errors = create_ResultTable_from_df_by_removing_H2O_SampleNames_and_Undetermined_CT_and_create_CtSD_errors_by_filter_CtSD_more_than_0p6(df)
  df_CT_Result_table = remove_outlyer_CTs_from_df_CT_Result_table(df_CT_Result_table,df_CtSD_errors)
  df_pivot = create_pivotTable_from_df_clean_CT_Result_table(df_CT_Result_table)
  savefoldChangePlots_by_df_pivot(df_pivot, dict_subSamples, listReferenceGeneName, listControlSamples, listFilterOutFoldChanges= listFilterOutFoldChanges, SaveDIR= SaveDIR, ReplaceSampleControlName2ControlStr= ReplaceSampleControlName2ControlStr)

# path = "./QPCR FH.xls"
# path2 = "./Anaysis-second batch sep2 2025.xls"
# dict_subSamples = {'df_Starved':['Starve','Different']}
# listRefrenceGeneName = [['pol2a']]
# listControlSamples = [['Starved']]
# plot_target_foldChangeDFs(path,dict_subSamples,listRefrenceGeneName,listControlSamples,ReplaceSampleControlName2ControlStr=True)

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