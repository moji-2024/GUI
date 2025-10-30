from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from functools import partial
import find_keywords_in_job_description
import re
import json
from SQL_DataBase import sqlDB
from datetime import datetime
import os, sys
import PyPDF2
from docx import Document
# '-------------------------------building function for handle paths in .exe file---------------------------'

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
JsonDataBasePath = resource_path('GetKeyPhraseInJobDescription/jsonDataBase')
# print(JsonDataBasePath)
# print(__file__)
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
    Button(root, text=buttonStr,fg='Blue' ,font=('arial', 14), command=lambda: func(*funcArgs)).grid(row=3, column=0, padx=40,
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
    canvas.create_text(x, y, text=f"%{score}", font=("Arial", 14, "bold"))
def getRow_and_Col_from_widget(Widget):
    return Widget.grid_info()["column"], Widget.grid_info()["row"]
def getBiggestRow_and_colIndex(root,):
    childWidgetsOfFoldChangeWin = root.grid_slaves()
    biggistRow = max(childWidget.grid_info()["row"] for childWidget in childWidgetsOfFoldChangeWin)
    biggistCol = max(childWidget.grid_info()["column"] for childWidget in childWidgetsOfFoldChangeWin)
    return biggistCol,biggistRow
def pasteStrInTk_entry(entry,insertText):
    entry.delete(0,END)
    entry.config(fg='Black')
    entry.insert(0,insertText)
def create_menuBtns_in_frount_of_EntryWidgets(root,entrywidgets:list,menueBtnText:list,DictFieldValues):
    ListMenuBtnsAndMenuwidget = []

    for i, entry in enumerate(entrywidgets):
        col, row = getRow_and_Col_from_widget(entry)
        dictKeyFuncs = {}
        for key in DictFieldValues[menueBtnText[i]]:
            if key:
                dictKeyFuncs[key] = (pasteStrInTk_entry,entry,key)
        menu_button, menu_widget = create_menu_drop_down(root, column=col+1, row=row, text=menueBtnText[i],
                              dictionary=dictKeyFuncs)
        ListMenuBtnsAndMenuwidget.append((menu_button, menu_widget))
    return ListMenuBtnsAndMenuwidget

def changeOutputFlag(outputFlagBool,widget,FalseText,TrueText):
    if outputFlagBool.get() == False:
        widget.configure(fg='green',text=TrueText)
        outputFlagBool.set(True)
    else:
        widget.configure(fg='red',text=FalseText)
        outputFlagBool.set(False)

def check_ComparativeOperatorInTuple(listStrElements):
    if len(listStrElements) == 2:
        if listStrElements[0] in ('<', '>', '<=', '>=', '='):
            float(listStrElements[1])
            return True
    return False
def searchEntryValidation(label_,entry_):
    # list_labels = ['id_', 'Job Title', 'Position Type', 'Company Name', 'Employer Name', 'Score']
    listElements = entry_.get().split(',')
    if label_ == 'id_':
        if all([ele.strip().isnumeric() for ele in listElements]):
            if len(listElements) == 1:
                return listElements[0]
            return listElements
        else: raise ValueError
    elif label_ == 'Score':
        if check_ComparativeOperatorInTuple(listElements):
            return tuple(listElements)
        else:
            raise ValueError
    else:
        if len(listElements) == 1:
            return listElements[0]
        return listElements

def get_DB_result_by_searchQuery_from_Entries(listEntries,containFlagBool,Db_ColNames):
    dictColVal = {}
    redFlag = False
    for col, entry in zip(Db_ColNames,listEntries):
        current_fg = entry.cget("fg")
        if (current_fg == 'Black') and (entry.get() != ''):
            try:
                valuableValue = searchEntryValidation(col, entry)
                if containFlagBool.get():
                    if type(valuableValue) == str:
                        dictColVal[f'{col}__contains'] = valuableValue
                    else:
                        raise ValueError
                else:
                    if col == 'Score':
                        dictColVal[f'{col}__operator'] = valuableValue
                    else:
                        dictColVal[col] = valuableValue
            except ValueError:
                redFlag = True
                mb.showerror('Syntax Error','Style of entries is not expected; Something in get_DB_result_by_searchQuery_from_Entries is wrong')
    if dictColVal:
        return sqlDB.search(
            'JobInfo',
            'MojiDB',
            **dictColVal
        )
    else:
        if redFlag == False:
            return sqlDB.view('JobInfo','MojiDB',)

def showHelp(root,text):
    helpWin = create_top_window(root_win=root, title='Instruction',
                                           geometry='',
                                           width=False, height=False,GrabFlag=False )
    helpWin.focus_set()
    helpText = Text(helpWin, width=70, height=25, font=("Arial", 12),wrap='word')
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
    helpWin.bind("<FocusOut>", lambda event: helpWin.destroy())
def deleteCommandFromMenu(menu_,AllowMenuEntries:list):
    '''
    delete commands which are not allowed
    Returns:
    menu_
    '''
    lastIndex = menu_.index("end")
    if lastIndex:
        for i in range(menu_.index("end") + 1):  # menu.index("end") gives last index
            item_type = menu_.type(i)
            if item_type != 'separator':
                commandName = menu_.entrycget(i, 'label')
                if commandName not in AllowMenuEntries:
                    menu_.delete(i)
                    deleteCommandFromMenu(menu_, AllowMenuEntries)
                    break
        if menu_.type(lastIndex) == 'separator':
            menu_.delete(lastIndex)
    return menu_
def addCommandToMenu(menu_widget,AllowMenuEntries,Tk_entry):
    labels = [menu_widget.entrycget(i, "label")
              for i in range(menu_widget.index("end") + 1)
              if menu_widget.type(i) != "separator"]
    for AllowMenuEntry in AllowMenuEntries:
        if (AllowMenuEntry not in labels) and (AllowMenuEntry != ''):
            currentFunc = partial(pasteStrInTk_entry, Tk_entry,AllowMenuEntry)
            menu_widget.add_command(label=AllowMenuEntry, background='Black', foreground='red',
                                    command=currentFunc)
            menu_widget.add_separator()
def updateMenu(ListMenuBtnsAndMenuwidget,dictUniqueMetaData,Tk_entries=None):
    for i, Tuple in enumerate(ListMenuBtnsAndMenuwidget):
        menuBtn, menu_ = Tuple[0], Tuple[1]
        menuBtnName = menuBtn.cget('text')
        AllowMenuEntries = dictUniqueMetaData[menuBtnName]
        if Tk_entries:
            addCommandToMenu(menu_, AllowMenuEntries, Tk_entries[i])
        else:
            deleteCommandFromMenu(menu_, AllowMenuEntries)


def Extraction_and_deleteInformationPage(root,resumeText,jobDescriptionText,cursorListBoxSelected,DB_resultSetPrimaryKey,ResListBox):
    # this page help to extract resume & job Description Text as well as metadata as a csv file. Also delete recoreded Data from database.
    DictData = {
        key.strip(): value.strip()
        for key, value in (
            rowItem.split(':', 1) for rowItem in ResListBox.get(cursorListBoxSelected).split(';')
        )
    }
    FileName = '_'.join([name if name != '_' else '' for name in [DictData['JobTitle'],DictData['CompanyName']]])
    def ExtractMetadata():
        outputDIR = fd.askdirectory(title='Select Output Directory')
        if outputDIR:
            find_keywords_in_job_description.pd.DataFrame(DictData,index=[0]).to_csv(os.path.join(outputDIR,f'{FileName}metaData.csv'),index=False)
            mb.showinfo('Done')
    def DeleteRecord():
        ResListBox.delete(cursorListBoxSelected)
        sqlDB.delete('JobInfo','MojiDB',id_=DictData['id_'])
        # Update menus in main page
        dictUniqueMetaData = createDictJobMetaDataWithDistinctValues(MenuNamesInFrontEntries)
        updateMenu(ListMenuBtnsAndMenuwidget,dictUniqueMetaData)
        # destroy extra win
        if not ResListBox.get(0,END):
            root.master.destroy()
        root.destroy()

    def ExtractText(text:str,fileName):
        outputDIR = fd.askdirectory(title='Select Output Directory')
        if outputDIR:
            with open(outputDIR + '/' + fileName,'w', encoding="utf-8") as file:
                file.write(text)
            mb.showinfo('Done')

    Button(root, text='Delete Record', bg='Black', fg='Red',
           command=lambda: DeleteRecord()).pack(side=TOP, anchor='ne')
    Button(root, text='Extract Resume',command=lambda :ExtractText(resumeText,f'{FileName}Resume.txt')).pack(side=TOP, anchor='nw')
    Button(root, text='Extract Job Description',command=lambda :ExtractText(jobDescriptionText,f'{FileName}JobDescription.txt')).pack(side=TOP, anchor='nw')
    Button(root, text='Extract Metadata',
           command= ExtractMetadata).pack(side=TOP, anchor='nw')
def topMost(win_root,Btn):
    is_on_top = win_root.attributes('-topmost')
    win_root.attributes('-topmost', not is_on_top)
    if is_on_top:
        Btn.config(bg='Red')
    else:
        Btn.config(bg='Green')
def displayHardSkills_and_SoftSkills(root,score,hard_df,soft_df,resumeText=None,jobDescriptionText=None,cursorListBoxSelected=None,DB_resultSetPrimaryKey=None,ResListBox=None,extractFlag=False,insertedRowId=None):
    def DeleteRecord(DBTableRowID):
        sqlDB.delete('JobInfo','MojiDB',id_=DBTableRowID)
        ComparisonWin.destroy()
        dictUniqueMetaData = createDictJobMetaDataWithDistinctValues(MenuNamesInFrontEntries)
        updateMenu(ListMenuBtnsAndMenuwidget, dictUniqueMetaData,)
    # create win
    ComparisonWin = create_top_window(root_win=root, title='Compare your resume with Job description',
                                      geometry='800x350+400+100',
                                      width=False, height=False, GrabFlag=False)
    if insertedRowId:
        Button(ComparisonWin, text='Delete Record', bg='Black', fg='Red',
               command=lambda: DeleteRecord(insertedRowId)).pack(side=TOP, anchor='ne')
    if extractFlag:
        Extraction_and_deleteInformationPage(ComparisonWin,resumeText,jobDescriptionText,cursorListBoxSelected,DB_resultSetPrimaryKey,ResListBox)

    # create canvas & connect it to Vertical scrollbar
    ComparisonMasterFrame = CreateMasterFrameInCanavasConnected2Scrulbar_s(ComparisonWin)
    # crate Circular score indicator in ComparisonMasterFrame
    OvalCanvas = Canvas(ComparisonMasterFrame, width=150, height=150, bg="white")
    OvalCanvas.pack(side=LEFT)
    draw_score(OvalCanvas, 75, 75, 60, score=score)
    # put btn of TopMost for keep page always on top of other pages
    TopMostBtn = Button(ComparisonMasterFrame,text='TopMost', bg='Red', command=lambda: topMost(ComparisonWin,TopMostBtn))
    TopMostBtn.pack(side=TOP,anchor='ne')
    # put Frames in canvas
    hardSkillsFramInComparisonWin = Frame(ComparisonMasterFrame, bg='gray')
    hardSkillsFramInComparisonWin.pack(side=TOP)
    softSkillsFramInComparisonWin = Frame(ComparisonMasterFrame, bg='gray')
    softSkillsFramInComparisonWin.pack(side=TOP)
    # print tables
    printTableInWindow(hardSkillsFramInComparisonWin, hard_df, 'Hard Skills')
    printTableInWindow(softSkillsFramInComparisonWin, soft_df, 'Soft Skills')
def removewhiteSpaceInListElements(lst:list[str]):
    return [ele.replace(" ",'') for ele in lst]
def openSelectedFromListBoxWidget(event,ListBoxWidget):
    if ListBoxWidget.get(0, END):
        cursorSelected = ListBoxWidget.curselection()
    return cursorSelected
def EnterPortionResultsDetailsInListBox(root,results):
    previewFields = ['id_', 'Score', 'SubmitTime', 'JobTitle', 'PositionType', 'CompanyName','EmployerName']
    allFields = ['id_', 'SoftSkillTable', 'HardSkillTable', 'Score', 'Resume', 'jobDescription', 'SubmitTime',
                 'JobTitle', 'PositionType', 'CompanyName','EmployerName']
    def handleSelected(event,res,ResListBox):
        IntSelected = openSelectedFromListBoxWidget(event,ResListBox)
        if IntSelected:
            # res: [(row1),(row2),...]
            index = IntSelected[0]
            resumeText = res[index][allFields.index('Resume')]
            jobDescriptionText = res[index][allFields.index('jobDescription')]
            score = res[index][allFields.index('Score')]
            hard_SkillsJson = res[index][allFields.index('HardSkillTable')]
            soft_SkillsJson = res[index][allFields.index('SoftSkillTable')]
            SoftSkillTable = find_keywords_in_job_description.pd.read_json(soft_SkillsJson)
            hardSkillTable = find_keywords_in_job_description.pd.read_json(hard_SkillsJson)
            displayHardSkills_and_SoftSkills(resultWin,score,hardSkillTable,SoftSkillTable,resumeText,jobDescriptionText,cursorListBoxSelected=index,ResListBox=ResListBox,extractFlag=True)
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
        ResListBox.insert(END,'; '.join([f'{allFields[i]}: {res[i]}' if res[i] else f'{allFields[i]}: _' for i in resultIndexes]))
    ResListBox.bind('<<ListboxSelect>>',lambda event: handleSelected(event,results[0],ResListBox))
def updateJsonFile(listStrSkills:list,previosSkills:list,jsonFileName:str):
    skillSet = [skill.strip() for skill in listStrSkills if (skill not in previosSkills) and (skill.isspace() == False) and (skill != '')] + previosSkills
    with open(os.path.join(JsonDataBasePath, jsonFileName), "w") as f:
        json.dump(skillSet, f, indent=4)
def createDictJobMetaDataWithDistinctValues(JobMetaDataFields):
    DictJobMetaDataWithDistinctValues ={}
    for JobMetaData in JobMetaDataFields:
        DictJobMetaDataWithDistinctValues[JobMetaData] = sqlDB.getDistinctCol('MojiDB', 'JobInfo', JobMetaData)
    return DictJobMetaDataWithDistinctValues
# '-------------------------------main functions---------------------------'
def ScanPage(labelsFromMainPage,entriesFromMainPage):
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

        #convert tables as json string
        jsonHard_df=hard_df.to_json()
        jsonSoft_df=soft_df.to_json()
        # validate entriesFromMainPage
        for entry in entriesFromMainPage:
            if ';' in entry.get():
                mb.showerror('Entries error','Entries can not contain colons (;)')
                return

        # create Dict of Field:Values of main page entries
        dictFieldValues = {
            label_: re.sub(r' ,',', ',re.sub(r'\s{2,}', ' ', entry.get())).title() if entry.cget("fg") == 'Black' else ''
            for label_, entry in zip(labelsFromMainPage, entriesFromMainPage)
        }
        # update DB
        rowId = sqlDB.insert(
            'JobInfo',
            'MojiDB',
            SoftSkillTable=jsonSoft_df,
            HardSkillTable=jsonHard_df,
            Score=score,
            Resume=resumeText,
            jobDescription=jobDescriptionText,
            SubmitTime=DateTimeNow,
            **dictFieldValues,
        )
        # delete text in resume text-area
        resumeTextWidget.delete(0.0, END)
        # create dictFieldValues with distinct values
        dictUniqueMetaData = createDictJobMetaDataWithDistinctValues(labelsFromMainPage)
        # update menu buttons in front of entries in main page
        updateMenu(ListMenuBtnsAndMenuwidget, dictUniqueMetaData,entriesFromMainPage)

        # Display result to user
        displayHardSkills_and_SoftSkills(MainRootWin, score, hard_df, soft_df,insertedRowId=rowId)
    else:
        mb.showwarning('Empty Text Area', 'Both resume and Job descriptions must be filled out')
def SearchPage(labelsFromMainPage):
    HELP_TEXT = """
    🔍 How to Use the Search Tool

    1) Fill the Entry Boxes
       - Type the values you want to search for in the corresponding entry fields.
       - You can enter:
           * Single value (e.g., senior)
           * Multiple values as a list (e.g., Entry-Level, senior)

    2) Use the Menu Buttons (Right Side)
       - Each menu button inserts a predefined value into the matching entry field.
       - This helps you quickly choose valid search values without typing.

    3) Contain Flag
       - If you enable the Contain flag, the search will look for records containing the entered text (substring match).
       - When active, the flag turns green.
       - Example: entering 'sen' with Contain enabled will match results like 'senior'.
       * Note: when button turn to green you cannot fill out any entry with Multiple values

    4) Search Commit Button
       - When clicked, the app collects all values from the entries, converts them into a query, and calls results
       - This fetches rows from the database table 'JobInfo' that match your conditions.

    5) Search Features
       Depending on what you type in the entries, app perform:
           * Exact match → PositionType="senior"
           * Multiple exact matches → PositionType="senior", CompanyName="IT"
           * And conditions → return result if Role="senior", and Department="HR" == True
           * IN clause → PositionType IN ["Entry-Level", "senior"]
           * Contains → PositionType__contains="sen"
           * Operators → Score__operator=(">=", 30)
    Note: Make do not click containFlag Button when you want Search by score value or id_ value-s
    """
    def SearchResultPage(root,listEntries):
        results = get_DB_result_by_searchQuery_from_Entries(listEntries, containFlagBool, listKeysAccesptByDB_and_DictInMenu)
        if results:
            if results[0]:
                EnterPortionResultsDetailsInListBox(root.master, results)
                # destroy previous window
                root.destroy()
            else:
                mb.showwarning('Empty Result', "Query is not match with any result")
        else:
            mb.showwarning('Empty Result', "Application cannot return any result")
    def ExtractMetadataFromDBRows():
        res =sqlDB.view('JobInfo','MojiDB',)
        rows = res[0]
        columns = res[1][6:]
        dictData = {col: list(vals) for col, vals in zip(columns, zip(*(row[6:] for row in rows)))}
        outputDIR = fd.askdirectory(title='Select Output Directory')
        if outputDIR:
            find_keywords_in_job_description.pd.DataFrame(dictData).to_csv(os.path.join(outputDIR,'wholeMetaData.csv'),index=False)
            searchWin.destroy()
            mb.showinfo('Done')

    containFlagBool = BooleanVar()
    list_labelsInSearchPage = ['id_', 'Job Title', 'Position Type', 'Company Name', 'Employer Name','Score']
    if sqlDB.is_tableNotEmpty('MojiDB', 'JobInfo'):

        DictJobMetaData = createDictJobMetaDataWithDistinctValues(labelsFromMainPage)
        # create window, labels_Entries, Menus, Buttons
        searchWin = create_top_window(MainRootWin, title='Search', geometry='')

        EntriesListInSearchWin = createLabelsEntriesScrulbarsIn_a_page(
            searchWin,
            list_labelsInSearchPage,
            ['Integer ex: 1', 'Data analyst', "Entry-Level, Senior", 'Npower', 'Someone name: Alex', ">=, 55.5"],
            startGridRow=0)
        listKeysAccesptByDB_and_DictInMenu = removewhiteSpaceInListElements(list_labelsInSearchPage)
        create_menuBtns_in_frount_of_EntryWidgets(searchWin, EntriesListInSearchWin[1:-1],
                                                  listKeysAccesptByDB_and_DictInMenu[1:-1],
                                                  DictJobMetaData)
        _, biggistRowUntilNow = getBiggestRow_and_colIndex(searchWin)
        Button(searchWin,
               text='Search Commit',
               bg='white',
               fg='Black',
               command=lambda: SearchResultPage(searchWin, EntriesListInSearchWin)).grid(row=biggistRowUntilNow,
                                                                                         column=0)
        ContainBtn = Button(searchWin,
                            text='ContainFlag: inactive',
                            bg='white',
                            fg='red',
                            command=lambda: changeOutputFlag(containFlagBool, ContainBtn, 'ContainFlag: inactive',
                                                             'ContainFlag: active'))
        ContainBtn.grid(row=biggistRowUntilNow, column=1, sticky='E')
        Button(searchWin,
               text='ExtractMetadataFromDBRows',
               bg='Black',
               fg='Green',
               font=('Arial', 16),
               command=ExtractMetadataFromDBRows).grid(row=biggistRowUntilNow, column=1,sticky='s')
        Button(searchWin,
               text='Help',
               bg='white',
               fg='Green',
               font=('Arial', 16),
               command=lambda: showHelp(searchWin, HELP_TEXT)).grid(row=biggistRowUntilNow, column=2)
    else:
        mb.showinfo('Empty Database','There is nothing to search')
def Add_SkillPage(hard_Skills:list,soft_Skills:list):
    def add_into_json_files(LabelEntries:dict):
        Add_SkillPageDestroyFlag = False
        for label,entry in LabelEntries.items():
            current_fg = entry.cget("fg")
            if (current_fg == 'Black') and (entry.get() != ''):
                Add_SkillPageDestroyFlag = True
                listStrSkills = entry.get().split(',')
                if label == 'Soft Skill-s':
                    updateJsonFile(listStrSkills, soft_Skills, 'soft_Skills.json')
                else:
                    updateJsonFile(listStrSkills, hard_Skills, 'hard_Skills.json')
                mb.showinfo('Done')
            if Add_SkillPageDestroyFlag:
                Add_SkillWin.destroy()
    # create window, labels_Entries, Buttons
    Add_SkillWin = create_top_window(MainRootWin, title='Search', geometry='',GrabFlag=False)
    labels = ['Soft Skill-s','Hard Skill-s']
    EntriesListInSearchWin = createLabelsEntriesScrulbarsIn_a_page(
        Add_SkillWin,labels,
        ['Enter one or more skill ex: skill1, skill2','Enter one or more skill ex: skill1, skill2'], startGridRow=0)
    _, biggistRowUntilNow = getBiggestRow_and_colIndex(Add_SkillWin)
    dictLabelEntries = {label:entry for label,entry in zip(labels,EntriesListInSearchWin)}
    Button(Add_SkillWin,
           text='Commit',
           bg='white',
           fg='Black',
           command=lambda: add_into_json_files(dictLabelEntries)).grid(row=biggistRowUntilNow, column=0)
    return hard_Skills,soft_Skills
def UploadTextFile(TextWidgetName):
    TextWidget = globals()[TextWidgetName]
    file_path = fd.askopenfilename(
        title="Select a text file",
        filetypes=[
            ("Word files", "*.docx"),
            ("PDF files", "*.pdf"),
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
        ext = os.path.splitext(file_path)[1]  # includes the dot, e.g. ".csv"
        if ext == '.pdf':
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                content = ""
                for page in reader.pages:
                    content += page.extract_text()
            TextWidget.insert(0.0,content)
        elif ext == '.docx':
            # Load the Word file
            doc = Document(file_path)
            # Extract all text
            content = ''
            for para in doc.paragraphs:
                content += para.text + '\n'
            TextWidget.insert(0.0,content)
        else:
            with open(file_path) as file:
                content = file.read()
            TextWidget.insert(0.0,content)

# '-----------------------setup------------------------------'
with open(os.path.join(JsonDataBasePath, 'hard_Skills.json'), "r") as f:
    hard_Skills = json.load(f)
with open(os.path.join(JsonDataBasePath, 'soft_Skills.json'), "r") as f:
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
    'JobTitle VARCHAR(120)',
    'PositionType VARCHAR(60)',
    'CompanyName VARCHAR(120)',
    'EmployerName VARCHAR(120)')
JobRelatedLabelsInMainPage = ['Job Title','Position Type','Company Name','Employer Name']
MenuNamesInFrontEntries = removewhiteSpaceInListElements(JobRelatedLabelsInMainPage)
DictJobMetaData = createDictJobMetaDataWithDistinctValues(MenuNamesInFrontEntries)
# '-----------------------create main MainRootWin------------------------------'
MainRootWin = create_top_window(title='Scan Job for Keywords', geometry='', flag_topLevel=False)
# '-------------------------------initialization---------------------------'

# '-------------------------------frames---------------------------'
TopFramInRootWin = Frame(MainRootWin, height=25, bg='gray')
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
MainPageHelpText = '''
📖 Help Guide – Scan Job for Keywords

Purpose of the App
------------------
This application helps you compare your CV with a Job Description by scanning both texts 
and finding keyword matches. It shows how many times each keyword appears in the job description 
versus your CV, so you can optimize your resume before applying.

Main Sections
-------------
1. CV and Job Description Panels
   - CV (left): Paste or upload your CV text.
   - Job Description (right): Paste or upload the job posting text.
   - Use the "Upload" buttons below each panel to open a file/text upload page.

2. Scan Button (Center)
   - After inserting text into both panels, click "Scan".
   - The app will extract keywords from the Job Description and compare their frequency with your CV.
   - Results highlight which keywords are missing or underused in your CV.

3. Meta Data Section (Bottom)
   - Job Title: Enter the role you’re applying for.
   - Position Type: Choose from options like Entry-Level, Mid-Level, etc.
   - Company Name: Enter the Company of job description name.
   - Employer Name: Enter the employer’s name
   - Each entry may has a menu button on the right to help you select or autofill values.

   ✅ All metadata is stored in the database for future searches and record-keeping.

Workflow
--------
1. Upload or paste your CV text.
2. Upload or paste the Job Description text.
3. (Optional) Fill in Job Title, Position Type, and Company Name.
4. Press "Scan" to run keyword comparison.
5. Review the results and adjust your CV accordingly.
6. Save metadata for tracking your job applications.

Tips
----
- Clean up formatting before pasting your CV (plain text works best).
- Keywords matter: If a word appears often in the job posting but rarely in your CV, 
  consider adding it where relevant.
- Use the metadata fields to build your own application history database.
'''


# '-------------------------------list-box--------------------------'
# '-------------------------------labels & Entries & scrollbars---------------------------'

EntriesListInBottomBottomFramInRootWin = createLabelsEntriesScrulbarsIn_a_page(
    BottomBottomFramInRootWin,JobRelatedLabelsInMainPage,
['Data analyst','Entry-Level','Npower','Someone name: Alex'],startGridRow=0)

try:
    ListMenuBtnsAndMenuwidget = create_menuBtns_in_frount_of_EntryWidgets(BottomBottomFramInRootWin, EntriesListInBottomBottomFramInRootWin, MenuNamesInFrontEntries,
                                                  DictJobMetaData)
except NameError:
    pass
# '-------------------------------memu---------------------------'
Functions_menu_but, menu_Functions = create_menu_drop_down(TopFramInRootWin,
                                                        {'Search': (SearchPage,MenuNamesInFrontEntries),'Add Skill':(Add_SkillPage,hard_Skills,soft_Skills), },
                                                        text='Functions', column=0,fg='Blue')
# '-------------------------------buttons---------------------------'
Button(BottomFramInRootWin, text='Scan', font=('arial', 14),bg='green', command=lambda:ScanPage(MenuNamesInFrontEntries,EntriesListInBottomBottomFramInRootWin)).pack(side=BOTTOM)
Button(TopFramInRootWin, text='Main Page Help', font=('arial', 14),bg='green', command=lambda:showHelp(MainRootWin,MainPageHelpText)).grid(row=0,column=1,sticky='E')
# '-------------------------------text-boxs--------------------------'
resumeTextWidget = createTextAreaIn_a_RootWithLabel_and_button(LeftMiddelFramInRootWin, 'CV', 'Upload', UploadTextFile,'resumeTextWidget' )
jobDescriptionTextWidget = createTextAreaIn_a_RootWithLabel_and_button(RightMiddelFramInRootWin, 'Job Description',
                                                                       'Upload', UploadTextFile, 'jobDescriptionTextWidget')
# '-------------------------------binding---------------------------'
MainRootWin.bind('<Destroy>', win_destroy)
MainRootWin.mainloop()
