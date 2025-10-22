from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from functools import partial
import qpcr
import ast
import os, sys
def resource_path(relative_path: str) -> str:
    # PyInstaller sets sys.frozen = True when your script is running
    # inside a bundled app (both --onefile and --onedir).
    if getattr(sys, 'frozen', False):

        # If it's --onefile, PyInstaller extracts everything into a
        # random temp folder (_MEI12345) and sets sys._MEIPASS.
        # If it's --onedir, there is no _MEIPASS, so we fall back to
        # the folder where the exe lives (sys.executable).
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))

    else:
        # If you're just running the script normally (not frozen),
        # use the directory where your .py file is located.
        base_path = os.path.dirname(os.path.abspath('.'))

    # Build a full absolute path to your resource file
    return os.path.join(base_path, relative_path)
samplePath = resource_path('qPCR_project/SampleData/QPCR FH.xls')
# '-------------------------------building functions---------------------------'
def win_destroy(event):
    all_widgets = get_all_children(window)
    for widget in all_widgets:
        widget.destroy()
def pull_up_wins(wins:list):
    for win in wins:
        win.deiconify()
def create_menu_drop_down(window_, dictionary, row=0, column=0, text='text', fg='black', bg='gray'):
    menu_button = Menubutton(window_, text=text, fg=fg, bg=bg, font='arial,13')
    menu_widget = Menu(menu_button, tearoff=0)
    for key, tuple_funcArgs in dictionary.items():
        currentFunc = partial(tuple_funcArgs[0])
        menu_widget.add_command(label=key, background='black', foreground='red',
                                command=currentFunc)
        menu_widget.add_separator()
    menu_button.config(menu=menu_widget)
    menu_button.grid(row=row, column=column)
    return menu_button, menu_widget


def delete_menu_command_by_label(menu_, label_to_delete):
    for index in range(1, menu_.index('end')):
        try:
            label = menu_.entrycget(index, 'label')
            if label == label_to_delete:
                menu_.delete(index, index + 1)
                return 'done'
        except:
            pass


def create_top_window(root_win=None, title='Enter Name', geometry='300x50+400+100', width=False, height=False,
                      flag_topLevel=True,GrabFlag=True):
    # print(root_win)
    if flag_topLevel == True:
        func_window_ = Toplevel(root_win)
        if GrabFlag:
            func_window_.grab_set()
    else:
        func_window_ = Tk()
    func_window_.title(title)
    func_window_.geometry(geometry)
    func_window_.resizable(width=width, height=height)
    return func_window_

def connect_scrollbar_to_widget(window_, widget, row_scr_vertical=0, column_scr_vertical=0, row_scr_horizontal=1,
                                column_scr_horizontal=1, scr_horizontal=True,scr_vertical= True):
    if scr_vertical == True:
        vertical_scrollbar = Scrollbar(window_,command=widget.yview)
        widget.configure(yscrollcommand=vertical_scrollbar.set)
        if (row_scr_vertical != None) and (column_scr_vertical != None):
            vertical_scrollbar.grid(row=row_scr_vertical, column=column_scr_vertical, sticky='ns')
    if scr_horizontal == True:
        horizontal_scrollbar = Scrollbar(window_, orient='horizontal',command=widget.xview)
        widget.configure(xscrollcommand=horizontal_scrollbar.set)
        if (row_scr_horizontal != None) and (column_scr_horizontal != None):
            horizontal_scrollbar.grid(row=row_scr_horizontal, column=column_scr_horizontal, sticky='we')
        try:
            return vertical_scrollbar, horizontal_scrollbar
        except:
            return horizontal_scrollbar
    return vertical_scrollbar


def add_placeholder(entry, placeholder,focusInColor='red'):
    entry.insert(0, placeholder)
    entry.config(fg='Grey')  # placeholder color

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, END)
            entry.config(fg=focusInColor)  # user text color

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg='Grey')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
def createLabelsEntriesScrulbarsIn_a_page(rootWin,list_labels,list_placeholders,startGridRow=1):
    listEntries = []
    for index, label in enumerate(list_labels):
        Label(rootWin, text=label, font=20, fg='red', ).grid(row=index * 2 + startGridRow, column=0, sticky="w")
        entry = Entry(rootWin, font=('times', 13), fg='blue', width=50)
        entry.grid(row=index * 2 + startGridRow, column=1, sticky="w")
        add_placeholder(entry, list_placeholders[index])
        listEntries.append(entry)
        connect_scrollbar_to_widget(rootWin, entry, scr_vertical=False,
                                    row_scr_horizontal=index * 2 + startGridRow + 1)
    return listEntries

def get_all_children(widget):
    children = widget.winfo_children()
    for child in children:
        children += get_all_children(child)
    return children

def getBiggestRow_and_colIndex(root,):
    childWidgetsOfFoldChangeWin = root.grid_slaves()
    biggistRow = max(childWidget.grid_info()["row"] for childWidget in childWidgetsOfFoldChangeWin)
    biggistCol = max(childWidget.grid_info()["column"] for childWidget in childWidgetsOfFoldChangeWin)
    return biggistCol,biggistRow
def printTableInWindow(root, table_df, labelName: str):
    Label(root, text=labelName, font=('arial ', 17)).pack(side=TOP)
    # Create a style
    style = ttk.Style(root)

    # Change font of all Treeviews
    style.configure("Treeview", font=("Helvetica", 13,))

    # Change font of the headings
    style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))    # Create Treeview with DataFrame columns
    tree = ttk.Treeview(root, columns=list(table_df.columns), show="headings")
    # Define headings
    colWidths = [170,110,160,110]
    for i,col in enumerate(table_df.columns):
        tree.heading(col, text=col)
        try:
            tree.column(col, width=colWidths[i], anchor="center")
        except IndexError:
            tree.column(col, width=145, anchor="center")
    # Insert rows from DataFrame
    for sampleName, row in table_df.iterrows():
        tree.insert("", END, values=list(row))
        tree.insert("", END, values=['-' * int(120 / len(row)) for row_ in list(row)])
    # connect scrollbars to tree_widget
    vertical_scrollbar, horizontal_scrollbar = connect_scrollbar_to_widget(root, tree,
                                                                           row_scr_vertical=None,
                                                                           row_scr_horizontal=None,
                                                                           scr_horizontal=True)
    # pack elements
    vertical_scrollbar.pack(side="right", fill="y")
    horizontal_scrollbar.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)

    def copyRow2clipboard(event=None,index=0):
        selected = tree.focus()
        if not selected:
            return
        values = tree.item(selected, "values")
        if values:
            # Copy all cell text or one cell
            text = "\t".join(map(str, values))
            tree.clipboard_clear()
            if index == 0:
                tree.clipboard_append(values[index])
            else:
                tree.clipboard_append(text)
    tree.bind("<Control-c>", lambda event: copyRow2clipboard(event,0))
def readWholeexcel(excelFilePath,sheetName=None):
    if sheetName:
        df = qpcr.pd.read_excel(excelFilePath, sheet_name=sheetName, header=None)
        cols = df.columns.tolist()
        df['RowNum'] = [i + 1 for i in df.index]
        return df[['RowNum'] + cols]
    else:
        dict_df = qpcr.pd.read_excel(excelFilePath, sheet_name=sheetName, header=None)
        for sheet , df in dict_df.items():
            cols = df.columns.tolist()
            df['RowNum'] = [i + 1 for i in df.index]
            dict_df[sheet] = df[['RowNum'] + cols]
        return dict_df
def topMost(win_root,Btn):
    is_on_top = win_root.attributes('-topmost')
    win_root.attributes('-topmost', not is_on_top)
    if is_on_top:
        Btn.config(bg='Red')
    else:
        Btn.config(bg='Green')

def showHelp(root, text):
    helpWin = create_top_window(root_win=root, title='Instruction',
                                geometry='600x200+400+100',
                                width=False, height=False, GrabFlag=False)
    helpWin.focus_set()
    helpText = Text(helpWin, width=40, height=25, font=("Arial", 12),wrap='word')

    helpText.insert(0.0, text)
    text_vertical_scrollbar, text_horizontal_scrollbar = connect_scrollbar_to_widget(helpWin, helpText,
                                                                                     row_scr_vertical=None,
                                                                                     row_scr_horizontal=None,
                                                                                     scr_horizontal=True)
    text_vertical_scrollbar.pack(side="right", fill="y")
    text_horizontal_scrollbar.pack(side="bottom", fill="x")
    helpText.pack(fill="both", expand=True)
    helpText.configure(state='disabled')
    helpWin.bind("<FocusOut>", lambda event: helpWin.destroy())
# '-------------------------------main functions---------------------------'
def openFoldChangePage():
    SampleNameFlagBool = BooleanVar()
    FoldChangeWin = create_top_window(root_win=window, title='Fold Change window', geometry='', width=False, height=False,
                      GrabFlag=False)
    ListofDfForUseInsaveBarPlots = []
    def createDF(sheetName,skipRows):
        excelFilePath = fd.askopenfilename(title='select file',
                                           filetypes=[('exel files', "*.xlsx"), ('exel files', "*.xls"), ])
        try:
            try:
                df, df_pivot = qpcr.readExcelAndCreatePivotCT(excelFilePath,sheetName=sheetName,skipRows=skipRows)
                ListofDfForUseInsaveBarPlots.clear()
                ListofDfForUseInsaveBarPlots.append(df_pivot)
                return df, df_pivot
            except:
                df = readWholeexcel(excelFilePath,sheetName)
                return df, _
        except:
            mb.showerror(title='ReadError',message='Error in "createDF"')
    def createDf_and_showIt():
        def export(dataFrame:qpcr.pd.DataFrame):
            outputDIR = fd.askdirectory(title='Select Output Directory')
            if outputDIR:
                dataFrame.to_csv(outputDIR + "/pivotTable.csv",index=False)
                mb.showinfo('Done')
        try:
            valuesOfEntriesInFoldChangeWin = [wid.get() for wid in entries]
            skipRows = ast.literal_eval(valuesOfEntriesInFoldChangeWin[4])
            sheetName = valuesOfEntriesInFoldChangeWin[5]
            df, df_pivot = createDF(sheetName, skipRows)
            FoldChangeTableWin = create_top_window(root_win=FoldChangeWin, title='Table of Fold Change window',
                                                   geometry='600x250+400+100',
                                                   width=False, height=False, GrabFlag=False)
            try:
                # create df_toShow by .reset_index() which add indexes to a new column and reset indexes to int
                df_toShow = df_pivot.reset_index()
                # create Btn to keep page on top
                TopMostBtn = Button(FoldChangeTableWin, text='TopMost', bg='Red',
                                    command=lambda: topMost(FoldChangeTableWin, TopMostBtn))
                TopMostBtn.pack(side=TOP, anchor='ne')
                pivotExportBtn = Button(FoldChangeTableWin, text='Export', bg='Green',
                                    command=lambda: export(df_toShow))
                pivotExportBtn.pack(side=TOP, anchor='ne')
                # Create Treeview with DataFrame columns
                printTableInWindow(FoldChangeTableWin, df_toShow, 'Pivot table')
                mb.showinfo('Thumbs up', 'Your data is successfully loaded')
                # pull up windows in correct order
                pull_up_wins([window, FoldChangeWin, FoldChangeTableWin])
            except:
                # Create Treeview with DataFrame columns
                printTableInWindow(FoldChangeTableWin, df, 'Whole Data to check')
                pull_up_wins([window, FoldChangeWin, FoldChangeTableWin])
        except:
            mb.showerror(title='Error in createDf_and_showIt',message='App can not read the excel data')
            pull_up_wins([window, FoldChangeWin])
    def saveBarPlots():
        valuesOfEntriesInFoldChangeWin = [wid.get() for wid in entries]
        try:
            dict_dfs = ast.literal_eval(valuesOfEntriesInFoldChangeWin[0])
            listReferenceGeneNames = ast.literal_eval(valuesOfEntriesInFoldChangeWin[1])
            listControlSamples = ast.literal_eval(valuesOfEntriesInFoldChangeWin[2])
            listFilterOutFoldChanges = ast.literal_eval(valuesOfEntriesInFoldChangeWin[3])
            skipRows = ast.literal_eval(valuesOfEntriesInFoldChangeWin[4])
        except SyntaxError:
            mb.showerror('SyntaxError',"Please check syntax of 'SubTabels', 'RefGeneNames', 'ControlSamples', 'FilterOutFoldChanges'")
        sheetName = valuesOfEntriesInFoldChangeWin[5]
        aggregatedFlag = valuesOfEntriesInFoldChangeWin[6]
        outputFlagStr = valuesOfEntriesInFoldChangeWin[6]
        if ListofDfForUseInsaveBarPlots:
            if outputFlagStr == 'YES':
                outputDIR = fd.askdirectory(title='Select Output Directory')
                if outputDIR:
                    response =qpcr.savefoldChangePlots_by_df_pivot(ListofDfForUseInsaveBarPlots[0],dict_dfs,listReferenceGeneNames,listControlSamples,listFilterOutFoldChanges=listFilterOutFoldChanges,SaveDIR=outputDIR + '/',ReplaceSampleControlName2ControlStr=SampleNameFlagBool.get(),outPutStyle=aggregatedFlag)
                    mb.showinfo('Done', f'Plot-s are saved in {outputDIR}, Response is {response}')
                else:
                    mb.showerror(title='Output error when you load data', message='No Directory is selected')
            else:
                response =qpcr.savefoldChangePlots_by_df_pivot(ListofDfForUseInsaveBarPlots[0], dict_dfs, listReferenceGeneNames,listControlSamples,listFilterOutFoldChanges=listFilterOutFoldChanges,ReplaceSampleControlName2ControlStr=SampleNameFlagBool.get(),outPutStyle=aggregatedFlag)
                mb.showinfo('Done', f'Plot-s are saved in {__file__}, Response is {response}')
            ListofDfForUseInsaveBarPlots.clear()
        else:
            df, df_pivot = createDF(sheetName,skipRows)
            saveBarPlots()
        pull_up_wins([FoldChangeWin])
    def changeSampleName2ControlFlag():
        if SampleNameFlagBool.get() == False:
            sampleNameFlagButton.configure(fg='green')
            SampleNameFlagBool.set(True)
        else:
            sampleNameFlagButton.configure(fg='red')
            SampleNameFlagBool.set(False)
    # create necessary widgets by below lists
    text = '''This function creates a Fold Change bar plot for a gene of interest.

            -   X-axis: Sample names

            -   Y-axis: Fold change

            Parameters:

            -   SubTables: A Python dictionary mapping sub-table names (e.g., df_SIRNA, df_Starved) to lists of sample identifiers.

            -   RefGeneNames: A nested Python list of reference gene names (e.g., [['POL2A'], ['POL2A']]).

            -   ControlSamples: A nested Python list of control sample names (e.g., [['PC12-CTR-SIRNA'], ['PC12-Starved']]).

            -   FilterOutFoldChanges: A list of fold-change identifiers to filter out (e.g., ['foldChange_POL2A']).

            Notes:

            -   Placeholders in each entry indicate the expected data and can be customized with your specific experiment settings.
                The Choose output directory controls where plots will be save:

               -    Yes: You must specify your desired output directory.
               -    No: The program automatically uses the current app location as the output directory.'''
    list_labels = ['SubTabels', 'RefGeneNames', 'ControlSamples', 'FilterOutFoldChanges','SkipRows','SheetName',"OutPutType","ChooseOutputDirectory"]
    list_placeholders = ["{'df_SIRNA':['CTR','siRNA' ],'df_Starved':['Starved','PC12-EB','VLP1','Differentiated']}",
                         "[['POL2A'],['POL2A']]", "[['PC12-CTR-SIRNA'], ['PC12-Starved']]", "['foldChange_POL2A']",'38','Results','Aggregated','YES']
    Button(FoldChangeWin,
           text='load &\n show Data Frame',
           bg='white',
           fg='black',
           command=createDf_and_showIt).grid(row=0, column=0,sticky="W")
    Button(FoldChangeWin,
           text='Help',
           bg='white',
           fg='Green',
           command=lambda :showHelp(FoldChangeWin,text)).grid(row=0, column=1,sticky="E")
    TopMostBtn = Button(FoldChangeWin, text='TopMost', bg='Red',
                        command=lambda: topMost(FoldChangeWin, TopMostBtn))
    TopMostBtn.grid(row=0, column=2,sticky="E")

    entries=createLabelsEntriesScrulbarsIn_a_page(FoldChangeWin, list_labels, list_placeholders, startGridRow=1)
    # childWidgetsOfFoldChangeWin = FoldChangeWin.grid_slaves()
    _ , biggistRowUntilNow = getBiggestRow_and_colIndex(FoldChangeWin)
    Button(FoldChangeWin,
           text='Save bar plots',
           bg='black',
           fg='Green',
           font=('times',20),
           command=saveBarPlots).grid(row=biggistRowUntilNow + 1, column=0, sticky="W")
    sampleNameFlagButton = Button(FoldChangeWin,
           text='SampleControlStr\nAsNameFlag',
           bg='black',
           fg='red',
           font=('times', 10),
           command=lambda :changeSampleName2ControlFlag())
    sampleNameFlagButton.grid(row=biggistRowUntilNow + 1, column=1, sticky="W")
    
def openMeltCurvePage():
    meltCurveWin = create_top_window(root_win=window, title='Melt Curve window', geometry='', width=False, height=False,
                                      GrabFlag=False)
    # create necessary widgets by below lists
    list_labels = ['wellPositions', 'SampleNames','TargetNames', 'SkipRows', 'SheetNames', "ChooseOutputDirectory"]
    list_placeholders = ["B2,B3","Sample1,Sample2","Gene2,Gene3", '34', 'Melt Curve Raw Data, Results', 'YES']
    def savecurvePlots():
        valuesOfEntriesInFoldChangeWin = [(wid.get(),wid.cget("fg")) for wid in entries]
        # check cget of fg
        if valuesOfEntriesInFoldChangeWin[0][1] == 'Grey':
            wellPositions = []
        else:
            wellPositions = [val.strip() for val in valuesOfEntriesInFoldChangeWin[0][0].split(',')]
        if valuesOfEntriesInFoldChangeWin[1][1] == 'Grey':
            SampleNames = []
        else: SampleNames = [val.strip() for val in valuesOfEntriesInFoldChangeWin[1][0].split(',')]
        if valuesOfEntriesInFoldChangeWin[2][1] == 'Grey':
            TargetNames = []
        else: TargetNames = [val.strip() for val in valuesOfEntriesInFoldChangeWin[2][0].split(',')]
        SkipRows = valuesOfEntriesInFoldChangeWin[3][0]
        SheetNames = [val.strip() for val in valuesOfEntriesInFoldChangeWin[4][0].split(',')]
        ChooseOutputDirectory = valuesOfEntriesInFoldChangeWin[5][0]
        excelFilePath = fd.askopenfilename(title='select file',
                                           filetypes=[('exel files', "*.xlsx"), ('exel files', "*.xls"), ])

        try:
            if excelFilePath:
                if ChooseOutputDirectory == 'YES':
                    outputDIR = fd.askdirectory(title='Select Output Directory')
                    if outputDIR:
                        qpcr.readqpcrExcel_filterMeltDf_saveFigureInOutputDIR(excelFilePath, SkipRows, SheetNames, wellPositions,
                                                                      SampleNames, TargetNames, outputDIR=outputDIR)
                        mb.showinfo('Done', f'Plot is saved in {outputDIR}')
                    else:
                        mb.showerror(title='Output error', message='No Directory is selected')
                else:
                    qpcr.readqpcrExcel_filterMeltDf_saveFigureInOutputDIR(excelFilePath, SkipRows, SheetNames,
                                                                          wellPositions,
                                                                          SampleNames, TargetNames,)
                    mb.showinfo('Done', f'Plot is saved in {__file__}')
            else:
                mb.showerror(title='Input error', message='No data is selected')
        except:
            mb.showerror(title='Syntax Error', message='Inserted data is not match with input excel file')
        pull_up_wins([window,meltCurveWin])
    TopMostBtn = Button(meltCurveWin, text='TopMost', bg='Red',
                        command=lambda: topMost(meltCurveWin, TopMostBtn))
    TopMostBtn.grid(row=0, column=2, sticky="E")
    entries = createLabelsEntriesScrulbarsIn_a_page(meltCurveWin, list_labels, list_placeholders, startGridRow=1)
    # childWidgetsOfFoldChangeWin = FoldChangeWin.grid_slaves()
    _, biggistRowUntilNow = getBiggestRow_and_colIndex(meltCurveWin)
    Button(meltCurveWin,
           text='Save bar plots',
           bg='black',
           fg='Green',
           font=('times', 20),
           command=savecurvePlots).grid(row=biggistRowUntilNow + 1, column=0, sticky="W")
    Button(meltCurveWin,
           text='Help',
           bg='white',
           fg='Green',
           command=lambda :showHelp(meltCurveWin,app_description)).grid(row=biggistRowUntilNow + 1, column=1, sticky="E")
    app_description = """1. This app is designed to generate image plots of qPCR MeltCurve data directly from Excel files. 
       It allows users to visualize melt curve profiles for all wells or specific samples and targets based on user input.

       2. Main Features:

          • Excel File Selection:
            The app prompts the user to select an Excel file containing MeltCurve data (.xlsx or .xls format).

          • Customizable Parameters:

            - Skip Rows: Users can specify how many initial rows to skip when reading the Excel file 
              (useful if headers or notes exist above the data).

            - Sheet Names: Users must enter two sheet names (comma-separated) to process specific sheets within the file.

            - Well Positions, Sample Names, Target Names:
              If these fields are left empty, the app plots all MeltCurve data from the file.
              If any of these are specified, the app filters the data and plots only the selected wells, 
              samples, or targets.

          • Output Directory Options:

            - If “Choose Output Directory” is set to YES, the user can select a custom folder 
              where all generated plots will be saved.
            - If set to NO, the plots are saved in the current script directory."""


def OpenSampleDataPage():
    all_sheets = readWholeexcel(samplePath,sheetName=None)
    pageLoc = 0
    for sheetName in all_sheets:
        Win = create_top_window(root_win=window, title=sheetName, geometry=f'600x250+{400 + pageLoc}+{100+ pageLoc}', width=False,
                                          height=False,
                                          GrabFlag=False)
        df = all_sheets[sheetName]
        # Create Treeview with DataFrame columns
        printTableInWindow(Win, df, sheetName)
        pageLoc += 30







# '-----------------------setup------------------------------'

# '-----------------------create main window------------------------------'
window = create_top_window(title='BioTools', geometry='710x600+300+45', flag_topLevel=False)
# '-------------------------------initialization---------------------------'

# '-------------------------------frame---------------------------'
TopFramInRootWin = Frame(window, width=690, height=25, bg='gray')
TopFramInRootWin.pack(side=TOP)

# '-------------------------------variables---------------------------'


# '-------------------------------memu---------------------------'
Functions_menu_but, menu_seller = create_menu_drop_down(TopFramInRootWin, {'FoldChange': (openFoldChangePage,),'meltCurve': (openMeltCurvePage,),'SampleData':(OpenSampleDataPage,)},
                                               text='Functions', column=0)


# '-------------------------------buttons---------------------------'


# '-------------------------------list-box--------------------------'

# '-------------------------------Entries---------------------------'

# '-------------------------------labels---------------------------'

# '-------------------------------text-boxs--------------------------'

# '-------------------------------scrollbars---------------------------'







# '-------------------------------binding---------------------------'
window.bind('<Destroy>', win_destroy)
window.mainloop()

