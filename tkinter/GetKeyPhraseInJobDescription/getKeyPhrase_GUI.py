from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from functools import partial
import find_keywords_in_job_description
import ast
import json
from SQL_DataBase import sqlDB
from datetime import datetime


# '-------------------------------building functions---------------------------'
def get_all_children(widget):
    children = widget.winfo_children()
    for child in children:
        children += get_all_children(child)
    return children


def win_destroy(event):
    all_widgets = get_all_children(MainRootWin)
    for widget in all_widgets:
        widget.destroy()


def create_menu_drop_down(window_, dictionary, row=0, column=0, text='text', fg='Black', bg='gray'):
    menu_button = Menubutton(window_, text=text, fg=fg, bg=bg, font='masterFrame,13')
    menu_widget = Menu(menu_button, tearoff=0)
    for key, tuple_funcArgs in dictionary.items():
        args = tuple_funcArgs[1:]
        currentFunc = partial(tuple_funcArgs[0],*args)
        menu_widget.add_command(label=key, background='Black', foreground='red',
                                command=currentFunc)
        menu_widget.add_separator()
    menu_button.config(menu=menu_widget)
    menu_button.grid(row=row, column=column)
    return menu_button, menu_widget




def create_top_window(root_win=None, title='Enter Name', geometry='300x50+400+100', width=False, height=False,
                      flag_topLevel=True, GrabFlag=True):
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
                                column_scr_horizontal=1, scr_horizontal=True, scr_vertical=True):
    if scr_vertical == True:
        vertical_scrollbar = Scrollbar(window_, command=widget.yview)
        widget.configure(yscrollcommand=vertical_scrollbar.set)
        if (row_scr_vertical != None) and (column_scr_vertical != None):
            vertical_scrollbar.grid(row=row_scr_vertical, column=column_scr_vertical, sticky='ns')
    if scr_horizontal == True:
        horizontal_scrollbar = Scrollbar(window_, orient='horizontal', command=widget.xview)
        widget.configure(xscrollcommand=horizontal_scrollbar.set)
        if (row_scr_horizontal != None) and (column_scr_horizontal != None):
            horizontal_scrollbar.grid(row=row_scr_horizontal, column=column_scr_horizontal, sticky='we')
        try:
            return vertical_scrollbar, horizontal_scrollbar
        except:
            return horizontal_scrollbar
    return vertical_scrollbar


def pull_up_wins(wins: list):
    for win in wins:
        win.deiconify()


def add_placeholder(entry, placeholder, focusInColor='red'):
    entry.insert(0, placeholder)
    entry.config(fg='grey',font=('arial',16))  # placeholder color

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


def createLabelsEntriesScrulbarsIn_a_page(rootWin, list_labels, list_placeholders, focusInColor='Black', startGridRow=1):
    listEntries = []
    for index, label in enumerate(list_labels):
        Label(rootWin, text=label, font=20, fg='red', ).grid(row=index * 2 + startGridRow, column=0, sticky="w")
        entry = Entry(rootWin, font=('times', 12), fg='blue', width=50)
        entry.grid(row=index * 2 + startGridRow, column=1, sticky="w")
        if list_placeholders:
            add_placeholder(entry, list_placeholders[index],focusInColor=focusInColor)
        listEntries.append(entry)
        connect_scrollbar_to_widget(rootWin, entry, scr_vertical=False,
                                    row_scr_horizontal=index * 2 + startGridRow + 1)
    return listEntries


def createTextAreaIn_a_RootWithLabel_and_button(root, labelStr, buttonStr, func, *funcArgs):
    Label(root, text=labelStr, font=('arial ', 17)).grid(row=0, column=0, padx=40, sticky='W')
    text = Text(root, width=40, height=25)
    text.grid(row=1, column=0, sticky='W')
    connect_scrollbar_to_widget(root, text, 1, 1, 2, 0)
    Button(root, text=buttonStr, font=('arial', 14), command=lambda: func(*funcArgs)).grid(row=3, column=0, padx=40,
                                                                                           sticky='S')
    return text


def CreateMasterFrameInCanavasConnected2Scrulbar_s(root, bothScr=FALSE):
    canvas = Canvas(root)
    if bothScr:
        vertical_scrollbar, horizontal_scrollbar = connect_scrollbar_to_widget(root, canvas,
                                                                               row_scr_vertical=None,
                                                                               row_scr_horizontal=None,
                                                                               scr_horizontal=True)
        horizontal_scrollbar.pack(side="bottom", fill="x")
    else:
        vertical_scrollbar = connect_scrollbar_to_widget(root, canvas,
                                                         row_scr_vertical=None,
                                                         row_scr_horizontal=None,
                                                         scr_horizontal=False)
    # pack elements
    vertical_scrollbar.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)
    # 2. Frame inside canvas
    masterFrame = Frame(canvas)
    canvas.create_window((0, 0), window=masterFrame, anchor="nw")

    # 3. Update scrollable area when frame changes size
    def update_scrollbarRegion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    masterFrame.bind("<Configure>", update_scrollbarRegion)
    return masterFrame


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

def draw_score(canvas, x, y, radius, score, max_score=100):
    """
    Draw a circular score indicator
    :param canvas: Tkinter Canvas
    :param x, y: center coordinates
    :param radius: circle radius
    :param score: current score
    :param max_score: maximum possible score
    """
    def asignColor(score:float):
        if score < 50:
            return 'red'
        elif 50 <= score <= 70:
            return 'Yellow'
        else:
            return 'green'
    color = asignColor(score)
    start_angle = -90  # start from top
    extent = (score / max_score) * 360  # portion of circle to fill

    # Draw background circle (light gray)
    canvas.create_oval(x-radius, y-radius, x+radius, y+radius, outline="", fill="#eee")

    # Draw filled arc (representing the score)

    canvas.create_arc(x-radius, y-radius, x+radius, y+radius,
                      start=start_angle, extent=extent,
                      outline="", fill=color)

    # inner circle to make it like a ring
    canvas.create_oval(x-radius*0.7, y-radius*0.7, x+radius*0.7, y+radius*0.7,
                       outline="", fill="white")

    # Add text
    canvas.create_text(x, y, text=f"{score}/{max_score}", font=("Arial", 14, "bold"))
def getRow_and_Col_from_widget(Widget):
    return Widget.grid_info()["column"], Widget.grid_info()["row"]
def getBiggestRow_and_colIndex(root,):
    childWidgetsOfFoldChangeWin = root.grid_slaves()
    biggistRow = max(childWidget.grid_info()["row"] for childWidget in childWidgetsOfFoldChangeWin)
    biggistCol = max(childWidget.grid_info()["column"] for childWidget in childWidgetsOfFoldChangeWin)
    return biggistCol,biggistRow
def create_menuBtns_in_frount_of_EntryWidgets(root,entrywidgets:list,menueBtnText:list,DictFieldValues):
    def paste(entry,insertText):
        entry.delete(0,END)
        entry.config(fg='Black')
        entry.insert(0,insertText)
    for i, entry in enumerate(entrywidgets):
        col, row = getRow_and_Col_from_widget(entry)
        dictKeyFuncs = {}
        for key in DictFieldValues[menueBtnText[i]]:
            if key:
                dictKeyFuncs[key] = (paste,entry,key)
        create_menu_drop_down(root, column=col+1, row=row, text=menueBtnText[i],
                              dictionary=dictKeyFuncs)
def Write_Or_UpdatejsonUniqueFileds(dictFieldValues:dict):
    try:
        with open("jsonDataBase/Uniques.json", "r") as f:
            dictUniquefields = json.load(f)
        for field,value in dictFieldValues.items():
            if value not in dictUniquefields[field]:
                dictUniquefields[field].append(value)
    except:
        dictUniquefields = dict()
        for field,value in dictFieldValues.items():
            dictUniquefields[field] = [value,]
    with open("jsonDataBase/Uniques.json", "w") as f:
        json.dump(dictUniquefields, f, indent=4)

def changeOutputFlag(outputFlagBool,widget,FalseText,TrueText):
    if outputFlagBool.get() == False:
        widget.configure(fg='green',text=TrueText)
        outputFlagBool.set(True)
    else:
        widget.configure(fg='red',text=FalseText)
        outputFlagBool.set(False)


def convertEntryStr2PythonObj(STR):
    def checkOneBracketMatch_or_notAtAll(STR):
        if (STR.count('[') == 1) and (STR.count(']') == 1):
            if (STR[0] == '[') and (STR[-1] == ']'):
                return 'BracketMatch'
            return False
        elif (STR.count('[') == 0) and (STR.count(']') == 0):
            return 'UnBracket'
        else:
            return False
    StrChecked = checkOneBracketMatch_or_notAtAll(STR)
    if StrChecked:
        if StrChecked == 'BracketMatch':
            return ast.literal_eval(STR)
        else:
            return STR
    else:
        raise ValueError
def get_result_by_searchQuery_from_Entries(listEntries,containFlagBool,list_labels):
    dictColVal = {}
    for ind, entry in enumerate(listEntries):
        current_fg = entry.cget("fg")
        if (current_fg == 'Black') and (entry.get() != ''):
            try:
                entryContent = convertEntryStr2PythonObj(entry.get())
                if containFlagBool:
                    dictColVal[f'{list_labels[ind]}__contains'] = entryContent
                else:
                    dictColVal[list_labels[ind]] = entryContent
            except ValueError:
                mb.showerror('Syntax Error','Style of entries is not expected; Something in get_result_by_searchQuery_from_Entries is wrong')
    if dictColVal:
        res = sqlDB.search(
            'JobInfo',
            'MojiDB',
            **dictColVal
        )
        return res, dictColVal

def showHelp(root,text):
    helpWin = create_top_window(root_win=root, title='Instruction',
                                           geometry='',
                                           width=False, height=False, )
    helpText = Text(helpWin, width=50, height=25, font=("Arial", 12))
    text = text
    helpText.insert(0.0,text)
    text_vertical_scrollbar, text_horizontal_scrollbar = connect_scrollbar_to_widget(helpWin, helpText,
                                                                           row_scr_vertical=None,
                                                                           row_scr_horizontal=None,
                                                                           scr_horizontal=True)
    text_vertical_scrollbar.pack(side="right", fill="y")
    text_horizontal_scrollbar.pack(side="bottom", fill="x")
    helpText.pack(fill="both", expand=True)
    helpText.configure(state='disabled')
def createExtractBtnIn_displayHardSkills_and_SoftSkills(root,resumeText,jobDecriptionText):

    def ExtractText(text:str,fileName):
        outputDIR = fd.askdirectory(title='Select Output Directory')
        if outputDIR:
            with open(outputDIR + '/' + fileName,'w', encoding="utf-8") as file:
                file.write(text)
    Button(root, text='Extract Resume',command=lambda :ExtractText(resumeText,'Selected_Resume.txt')).pack(side=TOP, anchor='nw')
    Button(root, text='Extract Job Description',command=lambda :ExtractText(jobDecriptionText,'Selected_Job Description.txt')).pack(side=TOP, anchor='nw')
def displayHardSkills_and_SoftSkills(root,score,hard_df,soft_df,resumeText=None,jobDecriptionText=None,extractFlag=False):
    # create win
    ComparisonWin = create_top_window(root_win=root, title='Compare your resume with Job description',
                                      geometry='800x350+400+100',
                                      width=False, height=False, GrabFlag=False)
    if extractFlag:
        createExtractBtnIn_displayHardSkills_and_SoftSkills(ComparisonWin,resumeText,jobDecriptionText)

    # create canvas & connect it to Vertical scrollbar
    ComparisonMasterFrame = CreateMasterFrameInCanavasConnected2Scrulbar_s(ComparisonWin)
    # crate Circular score indicator in ComparisonMasterFrame
    OvalCanvas = Canvas(ComparisonMasterFrame, width=150, height=150, bg="white")
    OvalCanvas.pack(side=LEFT)
    draw_score(OvalCanvas, 75, 75, 60, score=score * 100)
    # put Frames in canvas
    hardSkillsFramInComparisonWin = Frame(ComparisonMasterFrame, bg='gray')
    hardSkillsFramInComparisonWin.pack(side=TOP)
    softSkillsFramInComparisonWin = Frame(ComparisonMasterFrame, bg='gray')
    softSkillsFramInComparisonWin.pack(side=TOP)
    # print tables
    printTableInWindow(hardSkillsFramInComparisonWin, hard_df, 'Hard Skills')
    printTableInWindow(softSkillsFramInComparisonWin, soft_df, 'Soft Skills')

def openSelectedFromListBoxWidget(event,ListBoxWidget):
    if ListBoxWidget.get(0, END):
        cursorSelected = ListBoxWidget.curselection()
    return cursorSelected
def EnterPortionResultsInListBox(root,results):
    previewFields = ['id_', 'Score', 'SubmitTime', 'JobTitle', 'PositionType', 'CompanyName']
    allFields = ['id_', 'SoftSkillTable', 'HardSkillTable', 'Score', 'Resume', 'jobDescription', 'SubmitTime',
                 'JobTitle', 'PositionType', 'CompanyName']
    def handleSelected(event,res,ResListBox):
        IntSelected = openSelectedFromListBoxWidget(event,ResListBox)
        if IntSelected:
            index = IntSelected[0]
            resumeText = res[index][allFields.index('Resume')]
            jobDecriptionText = res[index][allFields.index('jobDescription')]
            score = res[index][allFields.index('Score')]
            hard_SkillsJson = res[index][allFields.index('HardSkillTable')]
            soft_SkillsJson = res[index][allFields.index('SoftSkillTable')]
            SoftSkillTable = find_keywords_in_job_description.pd.read_json(soft_SkillsJson)
            hardSkillTable = find_keywords_in_job_description.pd.read_json(hard_SkillsJson)
            displayHardSkills_and_SoftSkills(root,score,hardSkillTable,SoftSkillTable,resumeText,jobDecriptionText,extractFlag=True)
        else:
            mb.showerror('IntSelected Error','App can not find cursor Selected from ListBox')

    resultIndexes = [allFields.index(ele) for ele in previewFields]
    resultWin = create_top_window(root.master, title='Search', geometry='', GrabFlag=False)
    ResListBox = Listbox(resultWin, width=95, height=15, font=75, selectforeground='red')
    ResListBoxVertical_scrollbar, ResListBoxHorizontal_scrollbar = connect_scrollbar_to_widget(resultWin, ResListBox,
                                                                                     row_scr_vertical=None,
                                                                                     row_scr_horizontal=None,
                                                                                     scr_horizontal=True)
    ResListBoxVertical_scrollbar.pack(side="right", fill="y")
    ResListBoxHorizontal_scrollbar.pack(side="bottom", fill="x")
    ResListBox.pack()
    for res in results[0]:
        ResListBox.insert(END,', '.join([f'{allFields[i]}: {res[i]}' for i in resultIndexes]))
    ResListBox.bind('<<ListboxSelect>>',lambda event: handleSelected(event,results[0],ResListBox))
# '-------------------------------main functions---------------------------'
def scan():
    # get date & time
    DateTimeNow = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    # get texts content
    resumeText = resumeTextWidget.get(0.0, END)
    jobDescriptionText = jobDescriptionTextWidget.get(0.0, END)
    if resumeText != '\n' and jobDescriptionText != '\n':
        soft_df, hard_df, score = find_keywords_in_job_description.find_keywordFrequency(resumeText,
                                                                                         jobDescriptionText,
                                                                                         soft_Skills,
                                                                                         hard_Skills)
        displayHardSkills_and_SoftSkills(MainRootWin, score, hard_df, soft_df)

        #convert tables as json string
        jsonHard_df=hard_df.to_json()
        jsonSoft_df=soft_df.to_json()
        # update DB
        sqlDB.insert(
            'JobInfo',
            'MojiDB',
            SoftSkillTable=jsonSoft_df,
            HardSkillTable=jsonHard_df,
            Score=score,
            Resume=resumeText,
            jobDescription=jobDescriptionText,
            SubmitTime=DateTimeNow,
            JobTitle=EntriesListInBottomBottomFramInRootWin[0].get(),
            PositionType=EntriesListInBottomBottomFramInRootWin[1].get(),
            CompanyName=EntriesListInBottomBottomFramInRootWin[2].get())
        # delete text in resume area
        resumeTextWidget.delete(0.0, END)
        dictFieldValues = dict(
            JobTitle=EntriesListInBottomBottomFramInRootWin[0].get(),
            PositionType=EntriesListInBottomBottomFramInRootWin[1].get(),
            CompanyName=EntriesListInBottomBottomFramInRootWin[2].get()
        )
        Write_Or_UpdatejsonUniqueFileds(dictFieldValues)
    else:
        mb.showwarning('Empty Text Area', 'Both resume and Job descriptions must be filled out')
def SearchWinPage():
    HELP_TEXT = """
    🔍 How to Use the Search Tool

    1) Fill the Entry Boxes
       - Type the values you want to search for in the corresponding entry fields.
       - You can enter:
           * Single value (e.g., 'senior')
           * Multiple values as a list (e.g., ['Entry-Level', 'senior'])

    2) Use the Menu Buttons (Right Side)
       - Each menu button inserts a predefined value into the matching entry field.
       - This helps you quickly choose valid search values without typing.

    3) Contain Flag
       - If you enable the Contain flag, the search will look for records containing the entered text (substring match).
       - When active, the flag turns green.
       - Example: entering 'sen' with Contain enabled will match results like 'senior'.

    4) Search Button
       - When clicked, the app collects all values from the entries, converts them into a query, and calls results
       - This fetches rows from the database table 'JobInfo' that match your conditions.

    5) Search Features
       Depending on what you type in the entries, you can perform:
           * Exact match → Role="senior"
           * Multiple exact matches → Role="senior", Department="IT"
           * And conditions → return result if Role="senior", and Department="HR" == True
           * IN clause → Role=["Entry-Level", "senior"]
           * Contains → Role__contains="sen"
           * Operators → Age__operator=(">=", 30)
    """

    def SearchResultPage(root,listEntries):
        try:
            results, dictColVal = get_result_by_searchQuery_from_Entries(listEntries, containFlagBool, list_labels)
            EnterPortionResultsInListBox(root.master, results)
            # destroy previous window
            root.destroy()
        except:
            mb.showerror('value error','Something in SearchResultPage function is wrong')
    containFlagBool = BooleanVar()
    list_labels = ['ID', 'JobTitle', 'PositionType', 'CompanyName','Score']
    try:
        with open("jsonDataBase/Uniques.json", "r") as f:
            dictUniquefields = json.load(f)
        # create window, labels_Entries, Menus, Buttons
        searchWin = create_top_window(MainRootWin, title='Search', geometry='')

        EntriesListInSearchWin = createLabelsEntriesScrulbarsIn_a_page(
            searchWin,
            list_labels,
            ['Integer', 'Data analytics', 'Entry-Level', 'Npower','>= 55'], startGridRow=0)
        create_menuBtns_in_frount_of_EntryWidgets(searchWin, EntriesListInSearchWin[1:-1], list_labels[1:-1],
                                                  dictUniquefields)
        _, biggistRowUntilNow = getBiggestRow_and_colIndex(searchWin)
        Button(searchWin,
               text='Search',
               bg='white',
               fg='Black',
               command=lambda: SearchResultPage(searchWin,EntriesListInSearchWin)).grid(row=biggistRowUntilNow, column=0)
        ContainBtn =Button(searchWin,
               text='ContainFlag: inactive',
               bg='white',
               fg='red',
               command=lambda: changeOutputFlag(containFlagBool,ContainBtn,'ContainFlag: inactive','ContainFlag: active'))
        ContainBtn.grid(row=biggistRowUntilNow, column=1,sticky='E')
        Button(searchWin,
               text='Help',
               bg='white',
               fg='Green',
               font=('Arial',16),
               command=lambda : showHelp(searchWin,HELP_TEXT)).grid(row=biggistRowUntilNow, column=2)
    except:
        mb.showerror('Load Error','Uniques.json is broken or not exist')

def UploadTextFile(TextWidgetName):
    TextWidget = globals()[TextWidgetName]
    file_path = fd.askopenfilename(
        title="Select a text file",
        filetypes=[
            ("Text files", "*.txt"),
            ("Log files", "*.log"),
            ("Markdown", "*.md"),
            ("reStructuredText", "*.rst"),
            ("CSV files", "*.csv"),
            ("TSV files", "*.tsv"),
            ("JSON files", "*.json"),
            ("YAML files", ("*.yaml", "*.yml")),
            ("XML/HTML files", ("*.xml", "*.html", "*.htm")),
            ("INI files", "*.ini"),
            ("TOML files", "*.toml"),
            ("Env files", "*.env"),
        ]
    )
    TextWidget.delete(0.0,END)
    if file_path:
        with open(file_path) as file:
            content = file.read()
            TextWidget.insert(0.0,content)

# '-----------------------setup------------------------------'
with open("jsonDataBase/hard_Skills.json", "r") as f:
    hard_Skills = json.load(f)
with open("jsonDataBase/soft_Skills.json", "r") as f:
    soft_Skills = json.load(f)
sqlDB.table_maker(
    'JobInfo',
    'MojiDB',
    'SoftSkillTable Text',
    'HardSkillTable Text',
    'Score REAL',
    'Resume Text',
    'jobDescription Text',
    'SubmitTime DATETIME',
    'JobTitle VARCHAR(60)',
    'PositionType VARCHAR(60)',
    'CompanyName VARCHAR(60)')
# '-----------------------create main MainRootWin------------------------------'
MainRootWin = create_top_window(title='Scan Job for Keywords', geometry='', flag_topLevel=False)
# '-------------------------------initialization---------------------------'

# '-------------------------------frames---------------------------'
TopFramInRootWin = Frame(MainRootWin, width=690, height=25, bg='gray')
TopFramInRootWin.pack(side=TOP)
MiddelFramInRootWin = Frame(MainRootWin, bg='gray')
MiddelFramInRootWin.pack(side=TOP)
BottomFramInRootWin = Frame(MainRootWin, width=690, height=25, bg='gray')
BottomFramInRootWin.pack(side=TOP)

BottomBottomFramInRootWin = Frame(MainRootWin, bg='gray')
BottomBottomFramInRootWin.pack(side=TOP)
# two frames for middel part of MainRootWin
LeftMiddelFramInRootWin = Frame(MiddelFramInRootWin, bg='gray')
LeftMiddelFramInRootWin.grid(row=0, column=0, padx=2)
RightMiddelFramInRootWin = Frame(MiddelFramInRootWin, bg='gray')
RightMiddelFramInRootWin.grid(row=0, column=1, padx=2)

# '-------------------------------variables---------------------------'


# '-------------------------------memu---------------------------'
Functions_menu_but, menu_Functions = create_menu_drop_down(TopFramInRootWin,
                                                        {'Search': (SearchWinPage,), },
                                                        text='Functions', column=0)

# '-------------------------------buttons---------------------------'
Button(BottomFramInRootWin, text='Scan', font=('arial', 14),bg='green', command=scan).pack(side=BOTTOM)

# '-------------------------------list-box--------------------------'

# '-------------------------------labels & Entries---------------------------'
EntriesListInBottomBottomFramInRootWin = createLabelsEntriesScrulbarsIn_a_page(
    BottomBottomFramInRootWin,
    ['Job Title','Position Type','Company Name'],
['','Entry-Level',''],startGridRow=0)

# '-------------------------------text-boxs--------------------------'
resumeTextWidget = createTextAreaIn_a_RootWithLabel_and_button(LeftMiddelFramInRootWin, 'CV', 'Upload', UploadTextFile,'resumeTextWidget' )
jobDescriptionTextWidget = createTextAreaIn_a_RootWithLabel_and_button(RightMiddelFramInRootWin, 'Job Description',
                                                                       'Upload', UploadTextFile, 'jobDescriptionTextWidget')
# '-------------------------------scrollbars---------------------------'


# '-------------------------------binding---------------------------'
MainRootWin.bind('<Destroy>', win_destroy)
MainRootWin.mainloop()
