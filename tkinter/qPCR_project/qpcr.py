import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


import matplotlib
matplotlib.use("TkAgg")
def editCT2CtMeaninDfAndRemoveRelatedRowsInDfErrorWhenErrorGroupLenIsLessThan3(df_CtSD_errors, df_CT_Result_table):
    groupedby_sample_target = df_CtSD_errors.groupby(['Sample Name', 'Target Name'], as_index=False)
    listindex2drop = []
    for group in groupedby_sample_target:
        if group[1].shape[0] < 3:
            df_CT_Result_table.loc[group[1].index, 'CT'] = df_CT_Result_table.loc[group[1].index, 'Ct Mean']
            listindex2drop.extend(group[1].index.tolist())
    df_CtSD_errors = df_CtSD_errors.drop(listindex2drop, axis=0)
    return df_CT_Result_table, df_CtSD_errors


def create_ResultTable_from_df_by_removing_H2O_SampleNames_and_Undetermined_CT_and_create_CtSD_errors_by_filter_CtSD_more_than_0p6(
        df_CT_Result_table):
    df_CT_Result_table = df_CT_Result_table[
        ~df_CT_Result_table['Sample Name'].str.contains('h2o', case=False, na=False)]
    df_CT_Result_table = df_CT_Result_table[df_CT_Result_table['CT'] != 'Undetermined']
    df_CtSD_errors = df_CT_Result_table[df_CT_Result_table['Ct SD'] > 0.6]
    df_CT_Result_table, df_CtSD_errors = editCT2CtMeaninDfAndRemoveRelatedRowsInDfErrorWhenErrorGroupLenIsLessThan3(
        df_CtSD_errors, df_CT_Result_table)
    df_CtSD_errors.loc[:, 'Ct SD'] = df_CtSD_errors['Ct SD'].round(3)
    return df_CT_Result_table, df_CtSD_errors


def remove_outlyer_CTs_from_df_CT_Result_table(df_CT_Result_table, df_CtSD_errors):
    for ct_sd in df_CtSD_errors['Ct SD'].unique():
        currentError = df_CtSD_errors[df_CtSD_errors['Ct SD'] == ct_sd]['CT']
        outlier = find_outlyer(currentError.values)
        index2drop = df_CtSD_errors[df_CtSD_errors['CT'] == outlier].index
        df_CT_Result_table.drop(index2drop, inplace=True)
    return df_CT_Result_table


def find_outlyer(list_numbers):
    mean_list = sum(list_numbers) / len(list_numbers)
    big_distanse = 0
    outlier = list_numbers[0]
    for i in list_numbers:
        if abs(i - mean_list) > big_distanse:
            big_distanse = abs(i - mean_list)
            outlier = i
    return outlier


def create_pivotTable_from_df_clean_CT_Result_table(df_CT_Result_table):
    df_pivot = df_CT_Result_table.pivot_table(
        index='Sample Name',
        columns='Target Name',
        values='CT',
        aggfunc='mean')
    return df_pivot


def readExcelAndCreatePivotCT(path, sheetName='Results', skipRows=38):
    # create df
    df = pd.read_excel(path, sheet_name=sheetName, skiprows=skipRows)
    df = df.dropna(axis=1, how='all')
    df = df[['Well Position', 'Sample Name', 'Target Name', 'CT', 'Ct Mean', 'Ct SD']]
    # dict_subSamples: dict of samples which must split into different df by substrings of sample names
    df_CT_Result_table, df_CtSD_errors = create_ResultTable_from_df_by_removing_H2O_SampleNames_and_Undetermined_CT_and_create_CtSD_errors_by_filter_CtSD_more_than_0p6(
        df)
    df_CT_Result_table = remove_outlyer_CTs_from_df_CT_Result_table(df_CT_Result_table, df_CtSD_errors)
    df_pivot = create_pivotTable_from_df_clean_CT_Result_table(df_CT_Result_table)
    return df_CT_Result_table, df_pivot


"""**Check Ct SD more than 0.6**"""



def get_sampleNames_from_df_pivot_which_contain_str(dataFrame, list_str):
    res = []
    for target in list_str:
        res.extend(dataFrame.index[dataFrame.index.str.contains(target, case=False, na=False)])
    return res


def create_DataFramesDict_by_sampleNames_from_pivot_Df(df_pivot, dict_samples):
    dicts_of_dfSamplegroups = {}
    for k, values in dict_samples.items():
        dicts_of_dfSamplegroups[k] = df_pivot.loc[values]
        dicts_of_dfSamplegroups[k].dropna(axis=1, inplace=True, how='all')
        # dicts_of_dfSamplegroups[k].dropna(axis=1,inplace=True,)
    return dicts_of_dfSamplegroups


# ΔCt = Ct(target) − Ct(reference).

# ΔΔCt = ΔCt(sample) − ΔCt(control).

# Fold change = 2^(−ΔΔCt).
def findRowsOrColumnsIndexByPortionName(df, patterns: list, orientation="columns"):
    if orientation == 'columns':
        mask = df.columns.str.contains('|'.join(patterns), case=False, na=False)
        return [col for col in df.columns[mask].values.tolist()]
    else:
        mask = df.index.str.contains('|'.join(patterns), case=False, na=False)
        return [col for col in df.index[mask].values.tolist()]


def create_fold_change_values_and_FoldChange_columnsName(targetDf, ref_gene_cols: list, sample_controls: list):
    SetFoldChange_columnsName = set()
    for col in targetDf.columns:
        targetDf[f'delta_{col}'] = targetDf[col] - targetDf[ref_gene_cols].mean(axis=1)
        targetDf[f'deltaDelta_{col}'] = targetDf[f'delta_{col}'] - targetDf.loc[sample_controls, f'delta_{col}'].mean()
        targetDf[f'foldChange_{col}'] = 2 ** (-targetDf[f'deltaDelta_{col}'])
        FoldChange_columnName = f'foldChange_{col}'
        SetFoldChange_columnsName.add(FoldChange_columnName)
    return SetFoldChange_columnsName


def changeLabelName2controlStr(sampleControlNames, xlabels):
    for counter, sample in enumerate(sampleControlNames):
        if sample in xlabels:
            ind = xlabels.index(sample)
            if counter != 0:
                xlabels[ind] = f'Control_{counter}'
            else:
                xlabels[ind] = f'Control'
    return xlabels


def barplot_AllFoldChanges(target_key, target_df, listFoldChangeNames, remove_controlRefGenes=['foldChange_POL2A'],
                           SaveDIR='./', sampleControlNames=None):
    plt.style.use("default")

    xlabels = list(target_df.index.values)
    if sampleControlNames:
        xlabels = changeLabelName2controlStr(sampleControlNames, xlabels)

    fig, ax = plt.subplots(figsize=(15, 10))

    x = np.arange(len(xlabels))  # Base positions

    # Filter columns first (remove control genes before counting)
    filtered_cols = [col for col in listFoldChangeNames if col not in remove_controlRefGenes]
    num_groups = len(filtered_cols)
    # Adjust width and total group width to reduce space
    total_group_width = 0.8  # total width allocated to one sample’s bars
    width = total_group_width / num_groups

    for i, foldChange_col in enumerate(filtered_cols):
        values = target_df[foldChange_col].values

        # Center the bar groups:
        offset = (i - (num_groups - 1) / 2) * width
        positions = x + offset

        # Plot with group shift: x + i*width
        ax.bar(positions, values, width=width, label=foldChange_col)

        # Add labels
        for j, v in enumerate(values):
            ax.text(positions[j], v + 0.05 * max(values), f"{v:.2f}",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Title & axis labels
    ax.set_title(
        f"Fold Change across Samples ({target_key})",
        fontsize=18,
        fontweight='bold',
        pad=25  # move title upward
    )
    ax.set_ylabel("Fold Change", fontsize=18, fontweight='bold')
    ax.set_xlabel("Samples", fontsize=18, fontweight='bold')

    # X-axis labels
    ax.set_xticks(x + (num_groups - 1) * width / 2)
    ax.set_xticklabels(xlabels, rotation=45, ha="right", fontsize=14, fontweight='bold')

    # Grid
    ax.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.7)

    # Legend
    ax.legend(
        title="FoldChange Columns",
        fontsize=14,  # bigger text
        title_fontsize=16,  # bigger title
        loc='upper left',
        bbox_to_anchor=(1.02, 1),  # Move outside (right side)
        borderaxespad=0.
    )

    # Clean spines
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    output_path = SaveDIR + f'Fold Change across Samples in {target_key}.png'
    newPath = check_if_outputFile_not_exist_otherwise_return_path(output_path, index=0)
    plt.savefig(newPath, dpi=300, bbox_inches="tight")
    # print('Done in barplot_AllFoldChanges')
    plt.show()
    if listFoldChangeNames:
        return True
    else:
        return False


def barplot_FoldChange(target_key, target_df, listFoldChangeNames, remove_controlRefGenes=[], SaveDIR='./',
                       sampleControlNames=None):
    # White background
    plt.style.use("default")
    # Select xlabels and values
    xlabels = list(target_df.index.values)
    if sampleControlNames:
        xlabels = changeLabelName2controlStr(sampleControlNames, xlabels)

    # Filter columns first (remove control genes before counting)
    filtered_cols = [col for col in listFoldChangeNames if col not in remove_controlRefGenes]
    for foldChange_col in filtered_cols:
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
        newPath = check_if_outputFile_not_exist_otherwise_return_path(output_path, index=0)
        plt.savefig(newPath, dpi=300, bbox_inches="tight")
        # plt.show()
        # print('Done in barplot_FoldChange')
        if listFoldChangeNames:
            return True
        else:
            return False


def check_if_outputFile_not_exist_otherwise_return_path(path, index=0):
    isfileExist = os.path.isfile(path)
    if isfileExist:
        suffix = os.path.splitext(path)[1]
        beforeSuffix = os.path.splitext(path)[0]
        return check_if_outputFile_not_exist_otherwise_return_path(f"{beforeSuffix}_{index + 1}{suffix}", index + 1)
    else:
        return path


def savefoldChangePlots_by_df_pivot(df_pivot, dict_subSamples: dict[list], listReferenceGeneName: list,
                                    listControlSamples: list[list], listFilterOutFoldChanges=['foldChange_POL2A'],
                                    SaveDIR='./', ReplaceSampleControlName2ControlStr=False, outPutStyle='Aggregated'):
    if outPutStyle == 'Aggregated':
        outputFunc = barplot_AllFoldChanges
        # alternative way
        # filteredPivot = keyDf_DF[1][list(SetFoldChangeNames)]
        # filteredPivot.plot(kind='bar')
        # plt.show()
    else:
        outputFunc = barplot_FoldChange
    dicts_of_dfSamplegroups = {}
    for DfName, listSearch in dict_subSamples.items():
        dicts_of_dfSamplegroups[DfName] = get_sampleNames_from_df_pivot_which_contain_str(df_pivot, listSearch)
    dicts_of_dfSamplegroups = create_DataFramesDict_by_sampleNames_from_pivot_Df(df_pivot, dicts_of_dfSamplegroups)
    # Edit each df in dicts_of_dfSamplegroups by related RefrenceGeneName & ControlSamples
    for ind, keyDf_DF in enumerate(dicts_of_dfSamplegroups.items()):
        ref_gene_cols = findRowsOrColumnsIndexByPortionName(keyDf_DF[1], listReferenceGeneName[ind])
        sample_controls = findRowsOrColumnsIndexByPortionName(keyDf_DF[1], listControlSamples[ind], orientation='rows')
        SetFoldChangeNames = create_fold_change_values_and_FoldChange_columnsName(keyDf_DF[1], ref_gene_cols,

                                                                                  sample_controls)
        if ReplaceSampleControlName2ControlStr:
            outputFunc(keyDf_DF[0], keyDf_DF[1], SetFoldChangeNames, listFilterOutFoldChanges, SaveDIR=SaveDIR,
                       sampleControlNames=sample_controls)
        else:
            outputFunc(keyDf_DF[0], keyDf_DF[1], SetFoldChangeNames, listFilterOutFoldChanges, SaveDIR=SaveDIR)


def plot_target_foldChangeDFs(path, dict_subSamples: dict[list], listReferenceGeneName: list,
                              listControlSamples: list[list], listFilterOutFoldChanges=['foldChange_POL2A'],
                              SaveDIR='./', ReplaceSampleControlName2ControlStr=False, outPutStyle='Aggregated',sheetName='Results', skipRows=34):
    df_CT_Result_table, df_pivot = readExcelAndCreatePivotCT(path, sheetName=sheetName, skipRows=skipRows)
    savefoldChangePlots_by_df_pivot(df_pivot, dict_subSamples, listReferenceGeneName, listControlSamples,
                                    listFilterOutFoldChanges=listFilterOutFoldChanges, SaveDIR=SaveDIR,
                                    ReplaceSampleControlName2ControlStr=ReplaceSampleControlName2ControlStr,
                                    outPutStyle=outPutStyle)


"""# Melt curve"""


def WellPosition2AnotherColValue(df,WellPosition):
    df = df[df['Well Position'] == WellPosition][['Sample Name','Target Name']]
    return df.values.tolist()[0]
def filterMeltDf(dfMelt,dfCT,wellPositions=[],SampleNames=[], TargetNames=[]):
    if SampleNames and TargetNames:
        wellnames = dfCT[(dfCT['Sample Name'].isin(SampleNames)) & (dfCT['Target Name'].isin(TargetNames))][
            'Well Position'].tolist()
        wellPositions.extend(wellnames)
    elif SampleNames:
        wellnames = dfCT[(dfCT['Sample Name'].isin(SampleNames))]['Well Position'].tolist()
        wellPositions.extend(wellnames)
    elif TargetNames:
        wellnames = dfCT[(dfCT['Target Name'].isin(SampleNames))]['Well Position'].tolist()
        wellPositions.extend(wellnames)
    if wellPositions:
        dfMelt = dfMelt[dfMelt['Well Position'].isin(wellPositions)]
    return dfMelt
def saveMeltCurve(dfMeltCurve,dfCT,outputDIR:str):
    grouped = dfMeltCurve.groupby('Well Position').agg(list)
    plt.figure(figsize=(11, 6))
    for Well_Position, row in grouped.iterrows():
        name = '_'.join(WellPosition2AnotherColValue(dfCT, Well_Position))
        plt.plot(row['Temperature'], row['Derivative'], label=f'{Well_Position}: {name}')
    plt.legend(title="MeltCurve Lines",
               fontsize=8,  # bigger text
               title_fontsize=14,  # bigger title
               bbox_to_anchor=(1.02, 1),  # Move outside (right side)
               loc='upper left',
               )
    plt.tight_layout()
    plt.savefig(outputDIR, dpi=300, bbox_inches="tight")
    # plt.show()
def readqpcrExcel_filterMeltDf_saveFigureInOutputDIR(path,skipRows,SheetNames,WellPositions,SampleNames,TargetNames,outputDIR='./'):
    skipRows = int(skipRows)
    dictDfs = pd.read_excel(path, sheet_name=SheetNames, skiprows=skipRows)
    dfMelt = dictDfs[SheetNames[0]]
    dfCT = dictDfs[SheetNames[1]]
    filtered =filterMeltDf(dfMelt, dfCT, wellPositions= WellPositions, SampleNames= SampleNames, TargetNames= TargetNames)
    outputPath = outputDIR + 'meltCurve.png'
    newoutputPath = check_if_outputFile_not_exist_otherwise_return_path(outputPath, index=0)
    saveMeltCurve(filtered,dfCT, newoutputPath)

