from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from functools import partial
import qpcr
import ast


# '-------------------------------building functions---------------------------'
def win_destroy(event):
    all_widgets = get_all_children(window)
    for widget in all_widgets:
        widget.destroy()

def create_menu_drop_down(window_, dictionary, row=0, column=0, text='text', fg='black', bg='gray'):
    menu_button = Menubutton(window_, text=text, fg=fg, bg=bg, font='ariyal,13')
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
def pull_up_wins(wins:list):
    for win in wins:
        win.deiconify()

def add_placeholder(entry, placeholder,focusInColor='red'):
    entry.insert(0, placeholder)
    entry.config(fg='grey')  # placeholder color

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, END)
            entry.config(fg=focusInColor)  # user text color

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
def createLabelsEntriesScrulbarsIn_a_page(rootWin,list_labels,list_placeholders,startGridRow=1):
    listEntries = []
    for index, label in enumerate(list_labels):
        Label(rootWin, text=label, font=20, fg='red', ).grid(row=index * 2 + startGridRow, column=0, sticky="w")
        entry = Entry(rootWin, font=('times', 12), fg='blue', width=50)
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


# '-------------------------------main functions---------------------------'
def openFoldChangePage():
    outputFlagBool = BooleanVar()
    FoldChangeWin = create_top_window(root_win=window, title='Fold Change window', geometry='600x250+400+100', width=False, height=False,
                      GrabFlag=False)
    ListofDfForUseInsaveBarPlots = []
    def createDf_and_showIt():
        try:
            excelFilePath = fd.askopenfilename(title='select file',
                                              filetypes=[('exel files', "*.xlsx"), ('exel files', "*.xls"), ])

            df, df_pivot = qpcr.read_excel(excelFilePath)
            FoldChangeTableWin = create_top_window(root_win=FoldChangeWin, title='Table of Fold Change window',
                                                   geometry='600x200+400+100',
                                                   width=False, height=False, )
            # create df_toShow by .reset_index() which add indexes to a new column and reset indexes to int
            df_toShow = df_pivot.reset_index()
            # Create Treeview with DataFrame columns
            tree = ttk.Treeview(FoldChangeTableWin, columns=list(df_toShow.columns), show="headings")
            # Define headings
            for col in df_toShow.columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center")
            # Insert rows from DataFrame
            for sampleName, row in df_toShow.iterrows():
                tree.insert("", END, values=list(row))
            mb.showinfo('Thumbs up', 'Your data is successfully loaded')
            # connect scrollbars to tree_widget
            vertical_scrollbar, horizontal_scrollbar = connect_scrollbar_to_widget(FoldChangeTableWin, tree,
                                                                                   row_scr_vertical=None,
                                                                                   row_scr_horizontal=None,
                                                                                   scr_horizontal=True)
            # pack elements
            vertical_scrollbar.pack(side="right", fill="y")
            horizontal_scrollbar.pack(side="bottom", fill="x")
            tree.pack(fill="both", expand=True)
            # pull up windows in correct order
            pull_up_wins([window, FoldChangeWin, FoldChangeTableWin])
            ListofDfForUseInsaveBarPlots.clear()
            ListofDfForUseInsaveBarPlots.append(df_pivot)
        except:
            pull_up_wins([window, FoldChangeWin])
    def showHelp():
        helpWin = create_top_window(root_win=FoldChangeWin, title='Instruction',
                                               geometry='600x200+400+100',
                                               width=False, height=False, )
        helpText = Text(helpWin, width=40, height=25, font=("Arial", 12))
        text = '''This function creates a Fold Change bar plot for a gene of interest.

        -   X-axis: Sample names

        -   Y-axis: Fold change

        Parameters:

        -   SubTables: A Python dictionary mapping sub-table names (e.g., df_SIRNA, df_Starved) to lists of sample identifiers.

        -   RefGeneNames: A nested Python list of reference gene names (e.g., [['POL2A'], ['POL2A']]).

        -   ControlSamples: A nested Python list of control sample names (e.g., [['PC12-CTR-SIRNA'], ['PC12-Starved']]).

        -   FilterOutFoldChanges: A list of fold-change identifiers to filter out (e.g., ['foldChange_POL2A']).

        Notes:

        -   Placeholders in each entry indicate the expected data type and can be customized with your specific experiment settings.
            The output directory flag (bottom-right corner of the interface) controls where plots are saved:

           -    Red (default): You must specify your desired output directory.

           -    Green (when clicked): The program automatically uses the current app location as the output directory.'''
        helpText.insert(0.0,text)
        text_vertical_scrollbar, text_horizontal_scrollbar = connect_scrollbar_to_widget(helpWin, helpText,
                                                                               row_scr_vertical=None,
                                                                               row_scr_horizontal=None,
                                                                               scr_horizontal=True)
        text_vertical_scrollbar.pack(side="right", fill="y")
        text_horizontal_scrollbar.pack(side="bottom", fill="x")
        helpText.pack(fill="both", expand=True)
        helpText.configure(state='disabled')
    def saveBarPlots():
        valuesOfEntriesInFoldChangeWin = [wid.get() for wid in childWidgetsOfFoldChangeWin if wid.widgetName == 'entry']
        dict_dfs = ast.literal_eval(valuesOfEntriesInFoldChangeWin[3])
        listReferenceGeneName = ast.literal_eval(valuesOfEntriesInFoldChangeWin[2])
        listControlSamples = ast.literal_eval(valuesOfEntriesInFoldChangeWin[1])
        listFilterOutFoldChanges = ast.literal_eval(valuesOfEntriesInFoldChangeWin[0])
        # this below nested block of codes says:
        # hey if user load data go by first condition else second
        # also in each one check outputFlag to use defult or not
        if ListofDfForUseInsaveBarPlots:
            if outputFlagBool.get() == False:
                outputDIR = fd.askdirectory(title='Select Output Directory') + '/'
                if outputDIR:
                    qpcr.savefoldChangePlots_by_df_pivot(ListofDfForUseInsaveBarPlots[0],dict_dfs,listReferenceGeneName,listControlSamples,listFilterOutFoldChanges=listFilterOutFoldChanges,SaveDIR=outputDIR)
            else:
                qpcr.savefoldChangePlots_by_df_pivot(ListofDfForUseInsaveBarPlots[0], dict_dfs, listReferenceGeneName,listControlSamples,listFilterOutFoldChanges=listFilterOutFoldChanges)
            ListofDfForUseInsaveBarPlots.clear()
        else:
            excelFilePath = fd.askopenfilename(title='Select File',
                                               filetypes=[('exel files', "*.xlsx"), ('exel files', "*.xls"), ])
            if excelFilePath:
                if outputFlagBool.get() == False:
                    outputDIR = fd.askdirectory(title='Select Output Directory') + '/'
                    if outputDIR:
                        qpcr.plot_target_foldChangeDFs(excelFilePath,dict_dfs,listReferenceGeneName,listControlSamples,listFilterOutFoldChanges=listFilterOutFoldChanges,SaveDIR=outputDIR)
                else:
                    qpcr.plot_target_foldChangeDFs(excelFilePath,dict_dfs,listReferenceGeneName,listControlSamples,listFilterOutFoldChanges=listFilterOutFoldChanges)
        if outputDIR:
            mb.showinfo('thumbs up',f'Data is saved in {outputDIR}')
        else:
            mb.showinfo('thumbs up',f'Data is saved successfully')
    def changeOutputFlag():
        if outputFlagBool.get() == False:
            flagButton.configure(fg='green',text='Output directory is:\n where your app located')
            outputFlagBool.set(True)
        else:
            flagButton.configure(fg='red',text='Output directory is:\n not where your app located')
            outputFlagBool.set(False)
    # create necessary widgets by below lists
    list_labels = ['SubTabels', 'RefGeneNames', 'ControlSamples', 'FilterOutFoldChanges']
    list_placeholders = ["{'df_SIRNA':['CTR','siRNA' ],'df_Starved':['Starved','PC12-EB','VLP1','Differentiated']}",
                         "[['POL2A'],['POL2A']]", "[['PC12-CTR-SIRNA'], ['PC12-Starved']]", "['foldChange_POL2A']"]
    Button(FoldChangeWin,
           text='load and show Data Frame',
           bg='white',
           fg='black',
           command=createDf_and_showIt).grid(row=0, column=0)
    Button(FoldChangeWin,
           text='Help',
           bg='white',
           fg='Green',
           command=showHelp).grid(row=0, column=1,sticky="E")

    createLabelsEntriesScrulbarsIn_a_page(FoldChangeWin, list_labels, list_placeholders, startGridRow=1)
    childWidgetsOfFoldChangeWin = FoldChangeWin.grid_slaves()
    biggistRowUntilNow = max(childWidget.grid_info()["row"] for childWidget in childWidgetsOfFoldChangeWin)
    Button(FoldChangeWin,
           text='Save bar plots',
           bg='black',
           fg='Green',
           font=('times',20),
           command=saveBarPlots).grid(row=biggistRowUntilNow + 1, column=0, sticky="W")
    flagButton = Button(FoldChangeWin,
           text= 'Output directory is:\n not where your app located',
           bg='black',
           fg='red',
           font=('times', 10),
           command=changeOutputFlag)
    flagButton.grid(row=biggistRowUntilNow + 1, column=1, sticky="E")

def openMeltCurvePage():
    meltCurveWin = create_top_window(root_win=window, title='Melt Curve window', geometry='600x200+400+100', width=False, height=False,
                                      flag_topLevel=False)
    # directoryOf_file = fd.askopenfilename(title='select file',
    #                                       filetypes=[('exel files', "*.xlsx"), ('exel files', "*.xls"), ])
    # for i in range(4)









# '-----------------------setup------------------------------'

# '-----------------------create main window------------------------------'
window = create_top_window(title='qPCR Tool-kit', geometry='710x600+300+45', flag_topLevel=False)
# '-------------------------------initialization---------------------------'

# '-------------------------------frame---------------------------'
TopFramInRootWin = Frame(window, width=690, height=25, bg='gray')
TopFramInRootWin.pack(side=TOP)

# '-------------------------------variables---------------------------'


# '-------------------------------memu---------------------------'
Functions_menu_but, menu_seller = create_menu_drop_down(TopFramInRootWin, {'FoldChange': (openFoldChangePage,),'meltCurve': (openMeltCurvePage,),},
                                               text='Functions', column=0)


# '-------------------------------buttons---------------------------'


# '-------------------------------list-box--------------------------'

# '-------------------------------Entries---------------------------'

# '-------------------------------labels---------------------------'

# '-------------------------------text-boxs--------------------------'

# '-------------------------------scrollbar---------------------------'

# '-------------------------------main functions---------------------------'








# '-------------------------------binding---------------------------'
window.bind('<Destroy>', win_destroy)
window.mainloop()
