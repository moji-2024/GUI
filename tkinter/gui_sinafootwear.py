from tkinter import *
import dill
import pandas as pd
from datetime import datetime
from tkinter import messagebox as mb
from orm_db import sqlDB, models, manager
from retail_package import print_comand, qrGenerator, QR_reader
from tkinter import filedialog as fd
import os
from functools import partial
from datastracture import circle_list
import re
from typing import List
from tkinter import simpledialog
# ---------------------------------global variable-----------------------------------
list_StrVariable_for_entries = []
dict_to_dump_by_dill = {}
child_attr = []
# '-------------------------------building functions---------------------------'
import tkinter as tk

def remove_widgets(root):
    for widget in root.winfo_children():
        widget.destroy()
def create_label_ent_bind_to_func_and_canvas_connected_to_scurulbar_for_contain_Button(root_win,key_release_func=None,label_text='Enter Attr to search',canvas_grid=(1,1),canvas_size=(350,150)):
    Label(root_win, text=label_text).grid(row=0, column=0)
    if key_release_func != None:
        ent = create_entry_with_key_release_binding(root_win,key_release_func, loc=(0, 1))
    canvas = Canvas(root_win, width=canvas_size[0], height=canvas_size[1])
    canvas.grid(row=canvas_grid[0], column=canvas_grid[1])
    frame_inside_canvas = Frame(canvas)
    canvas.create_window((0, 0), window=frame_inside_canvas, anchor="nw")
    connect_scrollbar_to_widget(root_win, canvas, 1, 0, 2, 1)

    # Function to update the scroll region of the canvas
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Bind the configuration of the frame to the canvas
    frame_inside_canvas.bind("<Configure>", on_frame_configure)
    if key_release_func != None:
        return frame_inside_canvas, ent
    else:
        return frame_inside_canvas

def on_key_release(event):
    """
    Function to handle key release events.
    """
    print(f"Key released: {event.keysym}")
    # You can add any additional functionality you want here
    # For example, you can search the database or update a list


def create_entry_with_key_release_binding(root,key_release_func=None, loc=(0, 0)):
    """
    Function to create an Entry widget and bind the key release event.
    """
    entry = Entry(root)
    if loc:
        entry.grid(row=loc[0], column=loc[1])
    if key_release_func == None:
        entry.bind('<KeyRelease>', on_key_release)
    else:
        func = partial(key_release_func,entry)
        entry.bind('<KeyRelease>', func)
    return entry

def search_names_in_db(names_db: List[str], query: str) -> List[str]:
    """
    Search for names in the database that match the given query string.

    Parameters:
    names_db (List[str]): List of names in the database.
    query (str): Substring to search for in the names.

    Returns:
    List[str]: List of names that contain the query substring.
    """
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return [name for name in names_db if pattern.search(name)]

def get_menu_details(menu):
    menu_details = []
    for index in range(menu.index('end') + 1):
        try:
            item_type = menu.type(index)
            if item_type == 'command':
                label = menu.entrycget(index, 'label')
                command = menu.entrycget(index, 'command')
                menu_details.append((label, command))
            elif item_type == 'cascade':
                label = menu.entrycget(index, 'label')
                submenu = menu.nametowidget(menu.entrycget(index, 'menu'))
                menu_details.append((label, get_menu_details(submenu)))
        except TclError:
            continue
    return menu_details


def get_all_submenus(menu):
    submenus = []
    for index in range(menu.index('end') + 1):
        try:
            item_type = menu.type(index)
            if item_type == 'cascade':
                submenu = menu.entrycget(index, 'menu')
                submenus.append(submenu)
                submenus.extend(get_all_submenus(menu.nametowidget(submenu)))
        except TclError:
            continue
    return submenus


def create_Nested_menu_drop_down(Cascade_menu: dict[list[dict | tuple]], root):
    """
    Creates a nested menu drop-down in a Tkinter application.

    Args:
        Cascade_menu (dict[list[dict | tuple]]): A dictionary where keys are cascade labels and values are lists of dictionaries or tuples.
            Each dictionary represents a submenu, and each tuple represents a command.
            Tuples should be in the form (label, command, *args), where:
                - label (str): The text to display on the menu item.
                - command (callable): The function to call when the menu item is selected.
                - *args: Optional arguments to pass to the command.
        root (tk.Tk): The root window object for the Tkinter application.

    Returns:
        Menu: The main menu object created and configured with nested submenus and commands.
    """
    main_menu = Menu(root, font='(Arial,13)')
    root.config(menu=main_menu)

    def create_by_items_in_dict(Cascade_Menus, parent_menu):
        for cascade_label, submenu_or_command in Cascade_Menus.items():
            submenu = Menu(parent_menu, tearoff=0)
            parent_menu.add_cascade(label=cascade_label, menu=submenu)
            for element in submenu_or_command:
                if type(element) == dict:
                    create_by_items_in_dict(element, submenu)
                else:
                    label = element[0]
                    command = element[1]
                    args = element[2:]
                    func = partial(command, *args)
                    submenu.add_command(label=label, command=func, background='black', foreground='red', )
                    submenu.add_separator()

    create_by_items_in_dict(Cascade_menu, main_menu)
    return main_menu


def create_Nested_menu_drop_down_by_menu_button(Cascade_Menus: dict[list[dict | tuple]] | list | tuple, root,
                                                menu_button_name='menu button', menu_button_row=0,
                                                menu_button_col=0, menu_button_sticky='nw',unloc_menu_btn_flag=False,menu_btn_fg='blue',menu_btn_bg='black'):
    menu_button = Menubutton(root, text=menu_button_name, fg=menu_btn_fg, bg=menu_btn_bg, font='(Arial,13)')
    if unloc_menu_btn_flag == False:
        menu_button.grid(row=menu_button_row, column=menu_button_col, sticky=menu_button_sticky)
    main_menu = Menu(menu_button, tearoff=0)
    menu_button.config(menu=main_menu)

    def create_by_items_in_dict(Cascade_Menus, parent_menu):
        if type(Cascade_Menus) == list or type(Cascade_Menus) == tuple:
            for element in Cascade_Menus:
                label = element[0]
                command = element[1]
                args = element[2:]
                func = partial(command, *args)
                parent_menu.add_command(label=label, command=func, background='black', foreground='red', )
                parent_menu.add_separator()
        else:
            for cascade_label, submenu_or_command in Cascade_Menus.items():
                submenu = Menu(parent_menu, tearoff=0)
                parent_menu.add_cascade(label=cascade_label, menu=submenu)
                for element in submenu_or_command:
                    if type(element) == dict:
                        create_by_items_in_dict(element, submenu)
                    else:
                        label = element[0]
                        command = element[1]
                        args = element[2:]
                        func = partial(command, *args)
                        submenu.add_command(label=label, command=func, background='black', foreground='red', )
                        submenu.add_separator()

    create_by_items_in_dict(Cascade_Menus, main_menu)
    return menu_button, main_menu


def create_menu_drop_down_by_menuButton(root, dictionary_of_label_and_tuple_of_funcArgs, row=0, column=0, text='text',
                                        fg='black',
                                        bg='gray', sticky='nw', menu_button_font='(Arial,13)'):
    menu_button = Menubutton(root, text=text, fg=fg, bg=bg, font=menu_button_font)
    menu_widget = Menu(menu_button, tearoff=0)
    for label, func_arg in dictionary_of_label_and_tuple_of_funcArgs.items():
        args = func_arg[1:]
        func = partial(func_arg[0], *args)
        menu_widget.add_command(label=label, background='black', foreground='red',
                                command=func)
        menu_widget.add_separator()
    menu_button.config(menu=menu_widget)
    menu_button.grid(row=row, column=column, sticky=sticky)
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


def create_top_window(root_win=None, title='Enter Name', geometry='300x50+400+100', width=False, height=False):
    if root_win != None:
        func_window_ = Toplevel(root_win)
        func_window_.grab_set()
    else:
        func_window_ = Tk()
    func_window_.title(title)
    func_window_.geometry(geometry)
    func_window_.resizable(width=width, height=height)
    return func_window_





def delete_from_Menu(root, menu, index1, index2=None):
    menu.delete(index1, index2)
    root.destroy()


def create_dictionary__by_dict_and_a_funcName(func, keys, *args, argByKey=False):
    dictionary_of_nameFuncArg = {}
    for name in keys:
        if args == ():
            if argByKey == True:
                dictionary_of_nameFuncArg[name] = (func, name)
            else:
                dictionary_of_nameFuncArg[name] = func
        else:
            dictionary_of_nameFuncArg[name] = (func, *args)
    return dictionary_of_nameFuncArg


def connect_scrollbar_to_widget(root, widget, row_scr_vertical=0, column_scr_vertical=0, row_scr_horizontal=1,
                                column_scr_horizontal=1, typeScr='both'):
    if typeScr == 'both':
        vertical_scrollbar = Scrollbar(root)
        widget.configure(yscrollcommand=vertical_scrollbar.set)
        vertical_scrollbar.configure(command=widget.yview)
        vertical_scrollbar.grid(row=row_scr_vertical, column=column_scr_vertical, sticky='ns')
        horizontal_scrollbar = Scrollbar(root, orient='horizontal')
        widget.configure(xscrollcommand=horizontal_scrollbar.set)
        horizontal_scrollbar.configure(command=widget.xview)
        horizontal_scrollbar.grid(row=row_scr_horizontal, column=column_scr_horizontal, sticky='we')
        return vertical_scrollbar, horizontal_scrollbar
    elif typeScr == 'horizontal':
        horizontal_scrollbar = Scrollbar(root, orient='horizontal')
        widget.configure(xscrollcommand=horizontal_scrollbar.set)
        horizontal_scrollbar.configure(command=widget.xview)
        horizontal_scrollbar.grid(row=row_scr_horizontal, column=column_scr_horizontal, sticky='we')
        return horizontal_scrollbar
    else:
        vertical_scrollbar = Scrollbar(root)
        widget.configure(yscrollcommand=vertical_scrollbar.set)
        vertical_scrollbar.configure(command=widget.yview)
        vertical_scrollbar.grid(row=row_scr_vertical, column=column_scr_vertical, sticky='ns')
        return vertical_scrollbar


# '-------------------------------main functions---------------------------'


def change_flag(falg_name, vlue):
    falg_name.set(vlue)


def change_color_widget(widget, bg, fg='black'):
    # Change the background color of the button
    widget.config(bg=bg)
    # Change the text color of the button
    widget.config(fg=fg)


def handelPrintQR(widget, falg_name):
    if text_of_print_qr_btn.get() == 'Print_QR: Off':
        text_of_print_qr_btn.set('Print_QR: ON')
        change_flag(qrFlag_print_IntVar, 1)
        change_color_widget(widget, bg='green')
    else:
        text_of_print_qr_btn.set('Print_QR: Off')
        change_flag(qrFlag_print_IntVar, 0)
        change_color_widget(widget, bg='red')


def update_storage():
    update_win = create_top_window(title='Update manager', geometry='260x100+300+45')
    Label(update_win, text='By CSV file:').grid(row=0, column=0)
    Label(update_win, text='By XML file:').grid(row=1, column=0)
    Label(update_win, text='Manual:').grid(row=2, column=0, sticky='w')
    Button(update_win,
           text='update_by_csv',
           bg='white',
           fg='black',
           command=lambda: update_by_csvORxml('csv')).grid(row=0, column=1)
    Button(update_win,
           text='update_by_xml',
           bg='white',
           fg='black',
           command=lambda: update_by_csvORxml('xml')).grid(row=1, column=1)
    Button(update_win,
           text='update manual',
           bg='white',
           fg='black',
           command=lambda: update_db_manually(update_win)).grid(row=2, column=1)
    pass


def update_db_manually(update_win):
    update_win.destroy()
    manual_update_win = create_top_window(title='Update manager', geometry='600x100+300+45')


def update_by_csvORxml(fileType_input):
    if fileType_input == 'csv':
        directoryOf_file = fd.askopenfilename(title='select file', filetypes=[('csv files', "*.csv")])
        df = pd.read_csv(directoryOf_file)
        # print(df.head(), '\n\n------')
    else:
        directoryOf_file = fd.askopenfilename(title='select file',
                                              filetypes=[('xml files', "*.xml"), ('exel files', "*.xlsx"),
                                                         ('exel files', "*.xls"), ])
        df = pd.read_excel(directoryOf_file)
        # print(df.head(), '\n\n------')
    columns = df.columns
    for index, row in df.iterrows():
        update_dict = {}
        for column in columns:
            update_dict[column] = row[column]
        try:
            sqlDB.update('sinafootwear', 'storage', f'name_of_item = "{row["name_of_item"]}"', **update_dict)
        except:
            try:
                sqlDB.insert4('storage', 'sinafootwear', row['Category'], row['name_of_item'], row['Unit_price'],
                              row['Size'], row['Quantity'])
            except:
                mb.showerror(title='Format Error', message='Format of file dose not match with DB format')
                return




def create_Frames(root, root_width=50, root_height=50, num_rows=3, num_columns=2, sticky='nw',
                  colors=('yellow', 'black', 'green', 'red', 'blue', 'pink')):
    frame_list = []
    cll = circle_list.CdlinkedList()
    cll.appends([color for color in colors])
    width = root_width // num_columns
    height = root_height // num_rows
    for row in range(num_rows):
        for column in range(num_columns):
            frame = Frame(root, width=width, height=height, bg=cll.next_value())
            frame.grid(row=row, column=column, sticky=sticky)
            frame_list.append(frame)
    return frame_list

def append_to_list_box(listBox,products):
    for obj in products:
        listBox.insert(END, {k: v for k, v in obj.__dict__.items() if type(v) == str or type(v) == float})
def add_newCommand_to_Menu(menu, label, func, *args):
    func = partial(func, *args)
    menu.add_command(label=label, command=func)
    menu.add_separator()
def add_new_subMenu_to_parent_menu(parent_menu,label):
    submenu = Menu(parent_menu, tearoff=0)
    parent_menu.add_cascade(label=label, menu=submenu)
    return submenu


def returnTuple_unique_from_dfColumn(data, index):
    list_unique = []
    for row in data:
        list_unique.append(row[index])
    return set(list_unique)
def return_new_num_for_file_directory(path, data=None, set_directory=None, index=1):
    if set_directory == None:
        set_directory = returnTuple_unique_from_dfColumn(data, index)
    num_of_file = 0
    break_flag = False
    while break_flag == False:
        for directory in set_directory:
            if os.path.exists(path + f'/{directory}_{str(num_of_file)}.csv'):
                num_of_file += 1
            elif os.path.exists(path + f'/{directory}_{str(num_of_file)}.txt'):
                num_of_file += 1
            else:
                break_flag = True
    return num_of_file
def Create_CSVfile_from_DB_and_del_DB_and_categories(call_from_stracture_error_flag=False):
    dict_tableName_and_columns = sqlDB.get_tableName_and_columnsFromDBmaster('map_db')
    if dict_tableName_and_columns != {}:
        if call_from_stracture_error_flag == True:
            for table in dict_tableName_and_columns.keys():
                sqlDB.drop_table('map_db', table)
            os.remove('dynamic_class.dill')
        else:
            try:
                directoryToPaste = fd.askdirectory(title='selected folder')
            except:
                return
            for table, col in dict_tableName_and_columns.items():
                all_rows , columns = sqlDB.view4(table,'map_db',)
                df = pd.DataFrame(all_rows,columns=columns)
                df.to_csv(f'{directoryToPaste}/{table}.csv', index=False)
                sqlDB.drop_table('map_db',table)
            os.remove('dynamic_class.dill')
            mb.showinfo(title='Operation System',message='Done')
    else:
        mb.showerror('Operation fail',message='There is not any table in Data Base')
def get_direct_class(dict_classes,class_name):
    if type(dict_classes[class_name]) == dict:
        return get_direct_class(dict_classes[class_name],class_name)
    return dict_classes[class_name]
def get_specific_attrs(direct_class):
    return {k: v for k, v in direct_class.__dict__.items() if not k.endswith('__')}
def check_attrValues(direct_class,func,inherit=None):
    specific_attrs = get_specific_attrs(direct_class)
    for attr, value in specific_attrs.items():
        if value.class_name == 'ForeignKey' or value.class_name == 'OneToOneField' or value.class_name == 'ManyToManyField':
            check_attrValues(value.to, func,inherit=attr)
        else:
            if inherit:
                func(inherit + '__' + attr,value.class_name)
            else:
                func(attr,value.class_name)
def return_DBobj_from_related_class(class_obj,attr_name,col,amount:str):
    direct_attr = getattr(class_obj,attr_name)
    the_class = direct_attr.to
    splited_amount = amount.split(',')
    if len(splited_amount) > 1:
        try:
            return the_class().objects.filter(**{col: splited_amount})
        except:
            list_created_obj = []
            for val in splited_amount:
                created_obj = the_class().objects.create(**{col: val})
                list_created_obj.append(created_obj)
            return list_created_obj
    try:
        return the_class().objects.get(**{col:amount})
    except:
        return the_class().objects.create(**{col: amount})

def updateDB_by_csv_files():
    with open('dynamic_class.dill', 'rb') as file:
        categories = dill.load(file)
    def update_by_csv():
        #check
        directoryOf_file = fd.askopenfilename(title='select file', filetypes=[('csv files', "*.csv")])
        file_name = os.path.basename(directoryOf_file)
        file_name = file_name[:file_name.rfind('.')]
        try:
            df = pd.read_csv(directoryOf_file)
            the_class = get_direct_class(categories, file_name)
            class_instance = the_class()
            for index, row in df.iterrows():
                dict_to_create = {}
                for col, val in row.items():
                    splited_col = col.split('__')
                    if len(splited_col) > 1:
                        obj = return_DBobj_from_related_class(the_class, splited_col[0], splited_col[1], val)
                        dict_to_create[splited_col[0]] = obj
                    else:
                        dict_to_create[col] = val
                class_instance.objects.create(**dict_to_create)
            win_update_db.destroy()
        except:
            mb.showerror(title='File Error',message='File is not match with Data Base') #
    def create_csv_templates():
        folder_path = fd.askdirectory()
        for category_name in categories.keys():
            direct_class = get_direct_class(categories, category_name)
            data_dict = {}
            def create_date_template(attr,class_name):
                if class_name == 'CharField':
                    data_dict[attr]=['string test']
                elif class_name == 'DecimalField':
                    data_dict[attr] = [1234]
                elif class_name == 'BolianField':
                    data_dict[attr] = [1]
            check_attrValues(direct_class, create_date_template, inherit=None)
            df = pd.DataFrame(data_dict)
            file_path = os.path.join(folder_path, f'{category_name}.csv')
            df.to_csv(file_path,index=False)
        mb.showinfo(title='Operation status',message='Done')
    win_update_db = create_top_window(window, title='Update data base window', geometry='400x50+400+100')
    Button(win_update_db, text='Create csv templates', command=create_csv_templates).grid(row=0,column=0,padx=10)
    Button(win_update_db, text='Update data base by csv', command=update_by_csv).grid(row=0,column=1)







def Categories_and_DB_manager(root, child_table_name='', root_category_name=[],update_mainTable_query_and_save_effect_from_attr_type=(), *args):
    win_handel_entries = create_top_window(root, title='handel entries', geometry='500x150+400+100')
    category_or_table_strVar = StringVar()
    dbEntryStrVar = StringVar()
    def insert2entry(input_str):
        field_str = entfields_Name.get()
        if field_str != '':
            if category_or_table_strVar.get() != '':
                if input_str == 'ForeignKey' or input_str == 'ManyToManyField' or input_str == 'OneToOneField':
                    open_tk_window_to_manage_related_class(win_handel_entries, field_str, input_str)
                else:
                    dbEntryStrVar.set(dbEntryStrVar.get() + field_str + ' ' + input_str + ',')
                    entfields_Name.delete(0, END)
            else:
                mb.showinfo(title='Fail function', message='Category name can not be empty')

    def open_tk_window_to_manage_related_class(root, field_str, input_str):
        child_table_name_strvar = StringVar()
        win_to_manage_related_class = create_top_window(root, title='handel entries', geometry='500x150+400+100')
        def add_ent_str_to_dbEntryStrVar():
            update_query_str = dbEntryStrVar.get() + field_str + ' ' + input_str + '_to_' + child_table_name_strvar.get() + ','
            entfields_Name.delete(0, END)
            list_categories = []
            list_categories.extend(root_category_name + [category_or_table_strVar.get()])
            Categories_and_DB_manager(win_handel_entries, child_table_name=child_table_name_strvar.get(),root_category_name=list_categories,update_mainTable_query_and_save_effect_from_attr_type=(dbEntryStrVar,update_query_str,input_str))
            win_to_manage_related_class.destroy()

        Label(win_to_manage_related_class, text='Write Category Name').grid(row=0, column=0, sticky='w')
        ent_class_table_name = Entry(win_to_manage_related_class, width=40, textvariable=child_table_name_strvar)
        ent_class_table_name.grid(row=0, column=1, sticky='w')
        Button(win_to_manage_related_class, text='execute', command=lambda: add_ent_str_to_dbEntryStrVar()).grid(row=5, column=0)

    replace_DB_tables_permitions_BooleanVar = BooleanVar()
    replace_DB_tables_permitions_BooleanVar.set(True)
    def replace_DB_tables_permitions():
        if replace_DB_tables_permitions_BooleanVar.get():
            change_color_widget(replace_flag_btn,bg='red')
            replace_DB_tables_permitions_BooleanVar.set(False)
        else:
            change_color_widget(replace_flag_btn, bg='green')
            replace_DB_tables_permitions_BooleanVar.set(True)

    Label(win_handel_entries, text='Write category Name').grid(row=0, column=0, sticky='w')
    entMain_keyName = Entry(win_handel_entries, width=40, textvariable=category_or_table_strVar)
    entMain_keyName.grid(row=0, column=1, sticky='w')
    if child_table_name != '':
        entMain_keyName.config(state='disabled')
        category_or_table_strVar.set(child_table_name)
    Label(win_handel_entries, text='Write fields Name').grid(row=1, column=0, sticky='w')
    entfields_Name = Entry(win_handel_entries, width=40)
    entfields_Name.grid(row=1, column=1)
    Label(win_handel_entries, text='Select fields type').grid(row=2, column=0, sticky='w')
    create_Nested_menu_drop_down_by_menu_button([
        ('CharField', insert2entry, 'CharField'),
        ('DecimalField', insert2entry, 'DecimalField'),
        # ('BooleanField', insert2entry, 'BLOB'),
        ('ForeignKey', insert2entry, 'ForeignKey'),
        ('ManyToManyField', insert2entry, 'ManyToManyField'),
        ('OneToOneField', insert2entry, 'OneToOneField'),
    ], win_handel_entries, 'type', 2, 1)
    Label(win_handel_entries, text='Attributes').grid(row=3, column=0, sticky='w')
    dbEntry = Entry(win_handel_entries, textvariable=dbEntryStrVar, width=60, state='disabled')
    dbEntry.grid(row=3, column=1, columnspan=2, sticky='we')
    connect_scrollbar_to_widget(win_handel_entries, dbEntry, row_scr_horizontal=4, column_scr_horizontal=1, typeScr='horizontal')
    replace_flag_btn = Button(win_handel_entries, text='Replace flag',bg='green', command=lambda: replace_DB_tables_permitions())
    replace_flag_btn.grid(row=5, column=2)
    Button(win_handel_entries, text='record',
           command=lambda: create_DictCategories_and_sql_db(win_handel_entries, category_or_table_strVar.get(), dbEntry.get(),root_category_name,replace_flag=replace_DB_tables_permitions_BooleanVar.get(),update_root_db_query_sand_save_parent_attrType=update_mainTable_query_and_save_effect_from_attr_type)).grid(row=5, column=1)
    Button(win_handel_entries, text='Clear attributes entry', command=lambda: dbEntryStrVar.set('')).grid(row=5, column=0)
    # win_handel_entries.protocol("WM_DELETE_WINDOW",
    #                                      lambda: on_closing_protocol_func(
    #                                          [win_handel_entries, parent_win]))
def create_DictCategories_and_sql_db(root, table_name: str, query: str,roots_category=[],replace_flag=True,update_root_db_query_sand_save_parent_attrType=()):
    if update_root_db_query_sand_save_parent_attrType != ():
        child_attr.append((table_name,query,roots_category,replace_flag))
        update_root_db_query_sand_save_parent_attrType[0].set(update_root_db_query_sand_save_parent_attrType[1])
        root.destroy()
        return
    else:
        if table_name == '':
            mb.showerror(title='Error', message='Category name can not be empty')
            return
        if query == '':
            mb.showerror(title='Error', message='Attr can not be empty')
            return
        dict_orm_classes = {}
        def create_DB_and_ORM_class_in_dict(tableName,TableQuery,root_categoryName=[],replace_flag=True):
            list_columns_str = TableQuery.split(',')
            dictForCreateClass = {}
            for col in list_columns_str:
                if col == '':
                    continue
                field, type_field_related_table = col.split()
                try:
                    type_field, related_table = type_field_related_table.split('_to_')
                except:
                    type_field = type_field_related_table
                if type_field == 'ManyToManyField':
                    dictForCreateClass.setdefault(field, models.ManyToManyField(dict_orm_classes[related_table]))
                elif type_field == 'ForeignKey':
                    dictForCreateClass.setdefault(field, models.ForeignKey(dict_orm_classes[related_table]))
                elif type_field == 'OneToOneField':
                    dictForCreateClass.setdefault(field, models.OneToOneField(dict_orm_classes[related_table]))
                elif type_field == 'CharField':
                    dictForCreateClass.setdefault(field, models.CharField(max_length=500))
                elif type_field == 'DecimalField':
                    dictForCreateClass.setdefault(field, models.DecimalField())
            class_for_create_table = type(tableName, (models.model,), dictForCreateClass)
            manager.manager.create_tables(replace_flag=replace_flag)
            dict_orm_classes.setdefault(tableName, class_for_create_table)
            if root_categoryName != []:
                previous_parent = ''
                for parent in root_categoryName:
                    try:
                        dict_to_dump_by_dill[previous_parent].setdefault(parent, {})
                    except:
                        dict_to_dump_by_dill.setdefault(parent, {})
                    previous_parent = parent
                child_dict = dict_to_dump_by_dill
                for parent in root_categoryName:
                    child_dict = child_dict[parent]
                try:
                    child_dict[tableName].setdefault(tableName, class_for_create_table)
                except:
                    child_dict.setdefault(tableName, class_for_create_table)
            else:
                try:
                    dict_to_dump_by_dill[tableName].setdefault(tableName, class_for_create_table)
                except:
                    dict_to_dump_by_dill.setdefault(tableName, {})
                    dict_to_dump_by_dill[tableName].setdefault(tableName, class_for_create_table)
            # Serialize and save to a file
            if replace_flag == True:
                with open('dynamic_class.dill', 'wb') as file:
                    dill.dump(dict_to_dump_by_dill, file)
            else:
                with open('dynamic_class.dill', 'rb') as file:
                    categories = dill.load(file)
                categories.update(dict_to_dump_by_dill)
                with open('dynamic_class.dill', 'wb') as file:
                    dill.dump(categories, file)
        for element in child_attr:
            create_DB_and_ORM_class_in_dict(element[0],element[1],element[2],element[3])
        child_attr.clear()
        if query.find('price') != -1:
            query = query.replace('price','base_price')
        elif query.find('base_price') != -1:
            pass
        else:
            query = query + 'base_price DecimalField,'
        create_DB_and_ORM_class_in_dict(table_name,query)
        root.destroy()
def append_new_checkButton_by_pack_to_win_and_save_BooleanVar_linked_to_a_list(list_objects,win):
    list_selected_checkVar = []
    for product in list_objects:
        dict_obj_of_short_info = {k: v for k, v in product.__dict__.items() if type(v) == str}
        checked_Var = BooleanVar()
        list_selected_checkVar.append(checked_Var)
        checkbutton = Checkbutton(win, text=f"{dict_obj_of_short_info}",
                                  variable=checked_Var)
        checkbutton.pack(anchor=W)
    return list_selected_checkVar
def create_listBox_binded_to_func(root_win,func,row_listBOx=0,column_listBox=1,height_listBox=10,width_listBox=80,):
    listbox_of_all_data = Listbox(root_win, height=height_listBox, width=width_listBox)
    listbox_of_all_data.grid(row=row_listBOx, column=column_listBox, sticky='w')
    connect_scrollbar_to_widget(root_win, listbox_of_all_data, row_listBOx, row_listBOx, column_listBox, column_listBox)

    def on_selection(event):
        tuple_selected_item_from_listbox = listbox_of_all_data.curselection()
        func(event)

    # Bind the selection event to the on_selection function
    listbox_of_all_data.bind("<<ListboxSelect>>", on_selection)
    return listbox_of_all_data

def manage_db_dynamically():
    try:
        with open('dynamic_class.dill', 'rb') as file:
            categories = dill.load(file)
            print(categories)
    except:
        mb.showinfo(title='No data to return', message='Create Category First')
        return False


    def open_page_to_edit_each_selected_obj_or_add_new_one(title: str, root,loaded_dict_of_classes):
        gotten_class_by_title_as_key = loaded_dict_of_classes[title]
        titled_instance = gotten_class_by_title_as_key()
        all_obj_return_from_titled_class = titled_instance.objects.all()
        def filter_objs_bind_to_ent(ent,event,):
            listbox_of_all_data.delete(0,END)
            filtered_products = search_into_DB_by_each_attr_and_value_of_class(gotten_class_by_title_as_key, gotten_class_by_title_as_key,
                                                                               ent.get(), )

            append_to_list_box(listbox_of_all_data, filtered_products)

        top_win_for_manage_classes = create_top_window(root, title=title, geometry='')

        def handel_data_in_directed_class(class_name, selected_obj=None, root_win=None, root_class_name=''):
            def start_handel_data_in_directed_class_by_current_class_name_into_btn(root_func, root_window, **kwargs):
                start_handel_data_in_directed_class_by_current_class_name = partial(root_func, **kwargs)
                btn =Button(root_window, text='+',
                       command=start_handel_data_in_directed_class_by_current_class_name)
                return btn

            top_win_for_handel_data = create_top_window(root, title='Manage data', geometry='500x400+400+100')
            frame_inside_canvas_of_Manage_data_page = create_label_ent_bind_to_func_and_canvas_connected_to_scurulbar_for_contain_Button(top_win_for_handel_data, label_text='Manage data',canvas_size=(400,335))
            related_class = loaded_dict_of_classes[class_name]
            try:
                instance = related_class()
            except:
                if type(related_class) == dict:
                    related_class = related_class[class_name]
                    instance = related_class()
            dict_variable_to_return = {}
            dict_keys_and_rules_in_related_class = {k: v for k, v in related_class.__dict__.items() if
                                                    not k.endswith('__')}

            def save_data():
                dict_data_to_save_with_actual_value = {}
                if selected_obj != None:
                    for attr, obj_rule in dict_keys_and_rules_in_related_class.items():
                        if obj_rule.class_name == 'ManyToManyField':
                            checkbutton_vars = dict_variable_to_return[attr][1]
                            list_selected_obj_index = [i for i, var in enumerate(checkbutton_vars) if var.get()]
                            ManyToManyField_obj = getattr(selected_obj, attr)
                            #delete objects which already related to selected_obj
                            list_all_objs_related_to_selected_obj = ManyToManyField_obj.all()
                            for already_obj in list_all_objs_related_to_selected_obj:
                                ManyToManyField_obj.pop(already_obj)
                            # connect objects by selected index to selected_obj
                            for index in list_selected_obj_index:
                                ManyToManyField_obj.add(dict_variable_to_return[attr][0][index])
                        elif obj_rule.class_name == 'ForeignKey':
                            index_obj = dict_variable_to_return[attr][1].get()
                            ForeignKey_obj_to_save = getattr(selected_obj, attr)
                            ForeignKey_obj_to_save.update(dict_variable_to_return[attr][0][index_obj])
                        elif obj_rule.class_name == 'CharField':
                            if dict_variable_to_return[attr].get() != '':
                                setattr(selected_obj, attr, dict_variable_to_return[attr].get().upper())
                        elif obj_rule.class_name == 'DecimalField':
                            if dict_variable_to_return[attr].get() != '':
                                try:
                                    decimal = float(dict_variable_to_return[attr].get())
                                    setattr(selected_obj, attr, decimal)
                                except:
                                    mb.showerror(title='DecimalField Error',message='DecimalField Error in selected_obj')
                    selected_obj.save()
                else:
                    for attr, obj_rule in dict_keys_and_rules_in_related_class.items():
                        if obj_rule.class_name == 'ManyToManyField':
                            checkbutton_vars = dict_variable_to_return[attr][1]
                            whole_objs_came_from_ManyToManyField = dict_variable_to_return[attr][0]
                            list_selected_obj_index = [whole_objs_came_from_ManyToManyField[i] for i, var in
                                                       enumerate(checkbutton_vars) if var.get()]
                            dict_data_to_save_with_actual_value[attr] = list_selected_obj_index
                        elif obj_rule.class_name == 'ForeignKey':
                            selected_var = dict_variable_to_return[attr][1]
                            whole_obj_came_from_ForeignKey = dict_variable_to_return[attr][0]
                            dict_data_to_save_with_actual_value[attr] = whole_obj_came_from_ForeignKey[
                                selected_var.get()]
                        elif obj_rule.class_name == 'CharField':
                            dict_data_to_save_with_actual_value[attr] = dict_variable_to_return[attr].get().upper()
                        elif obj_rule.class_name == 'DecimalField':
                            try:
                                desimal = float(dict_variable_to_return[attr].get())
                                dict_data_to_save_with_actual_value[attr] = desimal
                            except:
                                mb.showerror(title='DecimalField Error')
                    try:
                        instance.objects.create(**dict_data_to_save_with_actual_value)
                    except:
                        mb.showerror(title='setting of create db is wrong')
                        Manage_data_page_top_level.destroy()
                        Create_CSVfile_from_DB_and_del_DB_and_categories(call_from_stracture_error_flag=True)
                        return
                if root_win != None:
                    root_win.destroy()
                    handel_data_in_directed_class(class_name=root_class_name, selected_obj=selected_obj)
                else:
                    top_win_for_manage_classes.destroy()
                    open_page_to_edit_each_selected_obj_or_add_new_one(title, root,loaded_dict_of_classes)
                top_win_for_handel_data.destroy()

            def delete_data():
                selected_obj.delete()
                top_win_for_handel_data.destroy()
                top_win_for_manage_classes.destroy()
                open_page_to_edit_each_selected_obj_or_add_new_one(title, root,loaded_dict_of_classes)

            selected_option = IntVar()
            list_selected_check_item = []
            def insert_btn_to_win(products,selectedObj_key,type_opration):
                if type_opration == 'ManyToManyField':
                    list_selected_check_item.clear()
                    for index, obj in enumerate(products):
                        dict_obj_of_short_info = {k: v for k, v in obj.__dict__.items() if type(v) == str}
                        checked_item = BooleanVar()
                        list_selected_check_item.append(checked_item)
                        created_btn = Checkbutton(frame_inside_canvas_for_ManyToManyField,
                                                  text=f"{dict_obj_of_short_info}",
                                                  variable=checked_item)
                        created_btn.pack(anchor=W)
                        if selected_obj != None:
                            gotten_attr_obj = getattr(selected_obj, selectedObj_key)
                            list_gotten_objs_from_ManyToManyField_obj = gotten_attr_obj.all()
                            for gotten_obj_from_ManyToManyField_obj in list_gotten_objs_from_ManyToManyField_obj:
                                if {k: v for k, v in gotten_obj_from_ManyToManyField_obj.__dict__.items() if
                                    type(v) == str} == dict_obj_of_short_info:
                                    checked_item.set(True)
                    dict_variable_to_return[selectedObj_key] = (products, list_selected_check_item)
                elif type_opration == 'ForeignKey':
                    selected_option.set(0)
                    for index, obj in enumerate(products):
                        dict_obj_of_short_info = {k: v for k, v in obj.__dict__.items() if type(v) == str}
                        created_btn = Radiobutton(frame_inside_canvas_for_ForeignKey, text=f"{dict_obj_of_short_info}",
                                                  variable=selected_option, value=index)
                        created_btn.pack(anchor=W)
                        if selected_obj != None:
                            gotten_attr_obj = getattr(selected_obj, selectedObj_key)
                            gotten_obj_from_ForeignKey_obj = gotten_attr_obj.get()
                            if {k: v for k, v in gotten_obj_from_ForeignKey_obj.__dict__.items() if
                                        type(v) == str} == dict_obj_of_short_info:
                                        selected_option.set(index)
                    dict_variable_to_return[selectedObj_key] = (products, selected_option)

            def edit_btn_in_win_bind_to_ent(filterClass,dictClass,selectedObj_key,type_opration,ent,event,):
                if type_opration == 'ManyToManyField':
                    remove_widgets(frame_inside_canvas_for_ManyToManyField)
                elif type_opration == 'ForeignKey':
                    remove_widgets(frame_inside_canvas_for_ForeignKey)
                if ent.get() != '':
                    products = search_into_DB_by_each_attr_and_value_of_class(filterClass,dictClass,ent.get())
                else:
                    products = filterClass().objects.all()
                insert_btn_to_win(products, selectedObj_key,type_opration)


            rows_num = len(dict_keys_and_rules_in_related_class.keys())
            frames = create_Frames(frame_inside_canvas_of_Manage_data_page, 150, 50, num_rows=rows_num)
            frame_index = 0
            for attr, obj_rule in dict_keys_and_rules_in_related_class.items():
                Label(frames[frame_index], text=attr).pack(side=TOP, anchor=W)
                if obj_rule.class_name == 'ManyToManyField':
                    search_func = partial(edit_btn_in_win_bind_to_ent,obj_rule.to,obj_rule.to,attr,'ManyToManyField')
                    frame_inside_canvas_for_ManyToManyField, ManyToManyField_ent = create_label_ent_bind_to_func_and_canvas_connected_to_scurulbar_for_contain_Button(frames[frame_index + 1],search_func,label_text='Search')
                    all_obj_came_from_ManyToManyField = obj_rule.to().objects.all()
                    insert_btn_to_win(all_obj_came_from_ManyToManyField, attr,'ManyToManyField')

                    plus_btn = start_handel_data_in_directed_class_by_current_class_name_into_btn(handel_data_in_directed_class,frames[frame_index + 1],class_name=obj_rule.to.__name__,root_win=top_win_for_handel_data,root_class_name=class_name)
                    plus_btn.grid(row=1, column=2)


                elif obj_rule.class_name == 'ForeignKey':
                    search_func2 = partial(edit_btn_in_win_bind_to_ent, obj_rule.to, obj_rule.to, attr,'ForeignKey')
                    frame_inside_canvas_for_ForeignKey, ForeignKey_ent = create_label_ent_bind_to_func_and_canvas_connected_to_scurulbar_for_contain_Button(frames[frame_index + 1],search_func2,label_text='Search')

                    all_obj_came_from_ForeignKey = obj_rule.to().objects.all()
                    insert_btn_to_win(all_obj_came_from_ForeignKey, attr,'ForeignKey')
                    plus_btn = start_handel_data_in_directed_class_by_current_class_name_into_btn(
                        handel_data_in_directed_class, frames[frame_index + 1], class_name=obj_rule.to.__name__,
                        root_win=top_win_for_handel_data, root_class_name=class_name)
                    plus_btn.grid(row=1, column=2)
                else:
                    str_var_for_ent = StringVar()
                    Entry(frames[frame_index + 1], textvariable=str_var_for_ent).pack(side=TOP, anchor=W)
                    if selected_obj != None:
                        value_of_attr = getattr(selected_obj, attr)
                        str_var_for_ent.set(value_of_attr)
                    dict_variable_to_return[attr] = str_var_for_ent

                frame_index += 2

            # create button to save or delete when from listbox an item selected or new data button selected
            Button(top_win_for_handel_data, text='Save', command=lambda: save_data()).grid(row=rows_num + 1, column=0)
            if selected_obj != None:
                Button(top_win_for_handel_data, text='Delete', command=delete_data).grid(row=rows_num + 1, column=1)

        Label(top_win_for_manage_classes, text='Choose each item from below list to edit').grid(row=0, column=0,
                                                                                                padx=10, pady=10)
        Label(top_win_for_manage_classes, text='Search').grid(row=2, column=0, padx=3)
        ent_to_search = create_entry_with_key_release_binding(top_win_for_manage_classes,filter_objs_bind_to_ent, loc=(2, 1))
        Button(top_win_for_manage_classes, text='Add new data',
               command=lambda: handel_data_in_directed_class(class_name=title)).grid(row=0, column=1)
        frame_for_listbox = Frame(top_win_for_manage_classes, background='blue')
        frame_for_listbox.grid(row=1, column=0, columnspan=2)

        def on_selection(event):
            tuple_selected_item_from_listbox = listbox_of_all_data.curselection()
            try:
                selected_obj = all_obj_return_from_titled_class[tuple_selected_item_from_listbox[0]]
                handel_data_in_directed_class(class_name=title, selected_obj=selected_obj)
            except:
                pass
        listbox_of_all_data = create_listBox_binded_to_func(frame_for_listbox, on_selection, row_listBOx=0, column_listBox=1, height_listBox=10,
                                      width_listBox=80)
        append_to_list_box(listbox_of_all_data, all_obj_return_from_titled_class)


    # create main page with Menus
    Manage_data_page_top_level = create_top_window(window, title='Manage data page', geometry='', width=True)
    Label(Manage_data_page_top_level, text='                               Manager data page                         ',
          fg='red').pack(side=TOP, anchor=W)
    menu_btn, main_menu = create_Nested_menu_drop_down_by_menu_button({},Manage_data_page_top_level,menu_button_name='All categories',unloc_menu_btn_flag=True)
    menu_btn.pack(side=TOP, anchor=W)
    def add_sub_menu_add_newCommand_to_Menu(root_menu,main_dict):
        for name,dict_or_class in main_dict.items():
            if type(dict_or_class) == dict:
                sub_menu = add_new_subMenu_to_parent_menu(root_menu,'Category of ' + name)
                add_sub_menu_add_newCommand_to_Menu(sub_menu,dict_or_class)
            else:
                func = partial(open_page_to_edit_each_selected_obj_or_add_new_one, name, Manage_data_page_top_level,main_dict)
                add_newCommand_to_Menu(root_menu,name,func)
    add_sub_menu_add_newCommand_to_Menu(main_menu,categories)

    # Manage_data_page_top_level.protocol("WM_DELETE_WINDOW", lambda: on_closing_protocol_func(Manage_data_page_top_level))

def open_sell_page():
    try:
        with open('dynamic_class.dill', 'rb') as file:
            categories = dill.load(file)
            print(categories)

    except:
        mb.showinfo(title='No data to return', message='Create Category First')
        return False
    win_sell_page = create_top_window(window, title='Search Inventory window', geometry='', width=True)
    all_products_in_list_box_in_checkOut_part = []

    def _preparation_page_for_discount():
        # descount_variables
        discount_intVAR = IntVar()
        discount_ent_floatVAR = DoubleVar()
        win_of_selected_item_from_listbox_in_checkOut_page = create_top_window(win_sell_page, title='Selected item',
                                                                               geometry='')

        def change_state_of_ent_by_Radiobutton_click(widgets: list):
            for index, widget in enumerate(widgets):
                if index == 0:
                    widget.config(state='normal')
                else:
                    widget.config(state='disabled')

        Label(win_of_selected_item_from_listbox_in_checkOut_page, text='Discount').grid(row=0, column=0)
        Radiobutton(win_of_selected_item_from_listbox_in_checkOut_page, text="Apply by percentage",
                    variable=discount_intVAR, value=1,
                    command=lambda: change_state_of_ent_by_Radiobutton_click([percentage_Entry, amount_Entry])).grid(
            row=0,
            column=1)
        Radiobutton(win_of_selected_item_from_listbox_in_checkOut_page, text="Apply by amount",
                    variable=discount_intVAR,
                    value=0,
                    command=lambda: change_state_of_ent_by_Radiobutton_click([amount_Entry, percentage_Entry])).grid(
            row=0, column=2)

        percentage_Entry = Entry(win_of_selected_item_from_listbox_in_checkOut_page, textvariable=discount_ent_floatVAR,
                                 state='disabled')
        percentage_Entry.grid(row=1, column=1)
        amount_Entry = Entry(win_of_selected_item_from_listbox_in_checkOut_page, textvariable=discount_ent_floatVAR)
        amount_Entry.grid(row=1, column=2)
        return win_of_selected_item_from_listbox_in_checkOut_page, discount_intVAR, discount_ent_floatVAR
    def win_selected_item_from_listBox_in_checkOut_part(event):
        tuple_selected_item_from_listbox = list_box_in_checkOut_part.curselection()
        if tuple_selected_item_from_listbox == ():
            return
        win_of_selected_item_from_listbox_in_checkOut_page, discount_intVAR, discount_ent_floatVAR = _preparation_page_for_discount()

        def Yes_delete():
            list_box_in_checkOut_part.delete(tuple_selected_item_from_listbox[0])
            all_products_in_list_box_in_checkOut_part.pop(tuple_selected_item_from_listbox[0])
            win_of_selected_item_from_listbox_in_checkOut_page.destroy()
        def save():
            got_selected = list_box_in_checkOut_part.get(tuple_selected_item_from_listbox)
            list_box_in_checkOut_part.delete(tuple_selected_item_from_listbox)
            item_price = all_products_in_list_box_in_checkOut_part[tuple_selected_item_from_listbox[0]].price
            if discount_intVAR.get() == 0:
                discounted_price = item_price - discount_ent_floatVAR.get()
            else:
                discounted_price = (item_price * (100 - discount_ent_floatVAR.get()) / 100)
                discounted_price = round(discounted_price,2)
            all_products_in_list_box_in_checkOut_part[tuple_selected_item_from_listbox[0]].price = discounted_price
            list_box_in_checkOut_part.insert(tuple_selected_item_from_listbox,got_selected[:got_selected.rfind('->')] + f'-> item price = ${discounted_price}')
            win_of_selected_item_from_listbox_in_checkOut_page.destroy()
        Button(win_of_selected_item_from_listbox_in_checkOut_page,text='Save',command=save).grid(row=2,column=0)
        Button(win_of_selected_item_from_listbox_in_checkOut_page, text='Remove item',command=Yes_delete).grid(row=2,column=1)
    final_list_selected_checkVar = []
    final_filtered_products = []
    def create_check_btn_inside_win_by_dict_of_categories_of_dict_classes(ent,event):
        final_filtered_products.clear()
        final_list_selected_checkVar.clear()
        remove_widgets(frame_inside_canvas)
        for category in categories.keys():
            if ent_of_search.get() == '':
                break
            dict_category = categories[category]
            main_class = dict_category[category]
            filtered_products = search_into_DB_by_each_attr_and_value_of_class(main_class,main_class,ent_of_search.get(),)
            final_filtered_products.extend(filtered_products)
            list_selected_checkVar = append_new_checkButton_by_pack_to_win_and_save_BooleanVar_linked_to_a_list(
                filtered_products, frame_inside_canvas)
            final_list_selected_checkVar.extend(list_selected_checkVar)

    def Add_selected_product_from_search_page__to_listBox_in_check_out_page():
        list_objs_from_selected_check_btn = [final_filtered_products[index] for index, BooleanVar in enumerate(final_list_selected_checkVar) if BooleanVar.get() ]
        all_products_in_list_box_in_checkOut_part.extend(list_objs_from_selected_check_btn)
        def return_dict_of_obj_from_value_of_foriegnKeyAttr(foriegnKey_obj):
            got_obj = foriegnKey_obj.get()
            return {key:value for key, value in got_obj.__dict__.items() if (type(value) == str and key != 'class_name') or type(value) == float}

        for obj in list_objs_from_selected_check_btn:
            item_info = ''
            for attr,v in obj.__dict__.items():
                if attr == 'class_name' or attr == 'price' or attr == 'base_price':
                    continue
                if type(v) == str or type(v) == float:
                    item_info += attr + ': ' + str(v) + ', '
                elif type(v) == int:
                    try:
                        foriegnKey_obj = getattr(obj,attr[:-3])
                        dict_to_insert_in_listBox = return_dict_of_obj_from_value_of_foriegnKeyAttr(foriegnKey_obj)
                        item_info += attr[:-3] + ': ' + str(dict_to_insert_in_listBox) + ', '
                    except:
                        pass
            price = obj.price
            list_box_in_checkOut_part.insert(END, item_info + '-> item price = $'+ str(price))
    def Open_page_to_Add_item_to_check_Out():
        def Add_item_to_check_out():
            class temporary_obj:
                pre_price = price_FloatVar.get()
                Title = title_strVar.get()
                item_number = numVar.get()
                price = pre_price * item_number

            if price_FloatVar.get() != 0.0:
                all_products_in_list_box_in_checkOut_part.append(temporary_obj)
                list_box_in_checkOut_part.insert(END,f'Title: {title_strVar.get()}, item_number: {numVar.get()} -> price = ${temporary_obj.total_price}')
                win_Add_item_to_check_Out_manually.destroy()

        title_strVar = StringVar()
        price_FloatVar = DoubleVar()
        numVar = IntVar()
        numVar.set(1)
        win_Add_item_to_check_Out_manually = create_top_window(win_sell_page,title='Create item(s)',geometry='')
        Label(win_Add_item_to_check_Out_manually,text='Title').grid(row=0,column=0)
        Entry(win_Add_item_to_check_Out_manually,textvariable=title_strVar).grid(row=0,column=1)
        Label(win_Add_item_to_check_Out_manually, text='price').grid(row=1, column=0)
        Entry(win_Add_item_to_check_Out_manually, textvariable=price_FloatVar).grid(row=1, column=1)
        Label(win_Add_item_to_check_Out_manually, text='Number of item(s)').grid(row=2, column=0)
        Entry(win_Add_item_to_check_Out_manually, textvariable=numVar).grid(row=2, column=1)
        Button(win_Add_item_to_check_Out_manually,text='Add to check out',command=Add_item_to_check_out).grid(row=3, column=0)

    def Choose_payment_method():
        def Cash():
            pass
        def Credit():
            pass
        def Debit():
            pass
        window_of_all_payment_method = create_top_window(win_sell_page, title='window of all payment method', geometry='')
        Label(window_of_all_payment_method, text='Payment method: ').grid(row=0, column=0)
        Button(window_of_all_payment_method, text='BY Cash', command=Cash).grid(row=0,column=1)
        Label(window_of_all_payment_method, text='Payment method: ').grid(row=0, column=0)
        Button(window_of_all_payment_method, text='BY Credit Card', command=Credit).grid(row=0, column=1)
        Label(window_of_all_payment_method, text='Payment method: ').grid(row=0, column=0)
        Button(window_of_all_payment_method, text='BY Debit Card', command=Debit).grid(row=0, column=1)

    def set_base_price_variable():
        new_value = simpledialog.askstring("Input", "Enter new value:")
        if new_value is not None:
            base_price = new_value
    def Apply_discount_to_all_items_in_checkOut_part():
        win_of_selected_item_from_listbox_in_checkOut_page, discount_intVAR, discount_ent_floatVAR = _preparation_page_for_discount()
        def save():
            for index, item in enumerate(list_box_in_checkOut_part.get(0,END)):
                list_box_in_checkOut_part.delete(index)
                item_price = all_products_in_list_box_in_checkOut_part[index].price
                if discount_intVAR.get() == 0:
                    discounted_price = item_price - discount_ent_floatVAR.get()
                else:
                    discounted_price = (item_price * (100 - discount_ent_floatVAR.get()) / 100)
                    discounted_price = round(discounted_price,2)
                all_products_in_list_box_in_checkOut_part[index].price = discounted_price
                list_box_in_checkOut_part.insert(index,item[:item.rfind('->')] + f'-> item price = ${discounted_price}')
            win_of_selected_item_from_listbox_in_checkOut_page.destroy()
        Button(win_of_selected_item_from_listbox_in_checkOut_page, text='Save', command=save).grid(row=2, column=0)
    frames = create_Frames(win_sell_page,num_rows=1,num_columns=2)
    frame_inside_canvas, ent_of_search = create_label_ent_bind_to_func_and_canvas_connected_to_scurulbar_for_contain_Button(frames[0],create_check_btn_inside_win_by_dict_of_categories_of_dict_classes,'Search')
    Button(frames[0],text='Add to check out',command=Add_selected_product_from_search_page__to_listBox_in_check_out_page).grid(row=3,column=0)
    Button(frames[0], text='Open page to Add item to check Out', command=Open_page_to_Add_item_to_check_Out).grid(row=3,column=1)

    list_box_in_checkOut_part = create_listBox_binded_to_func(frames[1],win_selected_item_from_listBox_in_checkOut_part)
    Button(frames[1], text='Choose payment method',command=Choose_payment_method).grid(row=3,column=1)
    # Button(frames[1], text='Set base price on variable', command=set_base_price_variable).grid(row=3, column=1,sticky='w')
    Button(frames[1], text='Apply discount to all items', command=Apply_discount_to_all_items_in_checkOut_part).grid(row=3, column=1,
                                                                                               sticky='E')

def search_into_DB_by_each_attr_and_value_of_class(class_for_filter_intoDB_obj,class_for_get_dict_attrs_values,search_str,root_attr=''):
    final_list_filtered_products = []
    effective_k_v_in_target_class = {k: v for k, v in class_for_get_dict_attrs_values.__dict__.items() if not k.endswith('__')}
    for attr, value_related_to_attr in effective_k_v_in_target_class.items():
        if value_related_to_attr.class_name == 'ManyToManyField':
            if final_list_filtered_products == []:
                related_class = value_related_to_attr.to
                filtered_products = search_into_DB_by_each_attr_and_value_of_class(class_for_filter_intoDB_obj,related_class,search_str,attr + '__')
                fixed_filtered_products = models.deep_copy_of_attrs_because_of_their_safety(filtered_products)
                final_list_filtered_products.extend(fixed_filtered_products)
        elif value_related_to_attr.class_name == 'ForeignKey':
            if final_list_filtered_products == []:
                related_class = value_related_to_attr.to
                filtered_products = search_into_DB_by_each_attr_and_value_of_class(class_for_filter_intoDB_obj,related_class,search_str,attr + '__')
                fixed_filtered_products = models.deep_copy_of_attrs_because_of_their_safety(filtered_products)
                final_list_filtered_products.extend(fixed_filtered_products)
        else:
            if final_list_filtered_products == []:
                filtered_products = class_for_filter_intoDB_obj().objects.filter(**{root_attr + attr + '__contains': search_str.upper()})
                fixed_filtered_products = models.deep_copy_of_attrs_because_of_their_safety(filtered_products)
                final_list_filtered_products.extend(fixed_filtered_products)
            # else:
            #     print(attr,final_list_filtered_products)

    return final_list_filtered_products


def basic_features():
    try:
        old_tables_columns = sqlDB.get_tableNameFromDBmaster('sinafootwear')
        tables_columns = {}
        for table in old_tables_columns.keys():
            tables_columns[table[table.rfind('_') + 1:]] = old_tables_columns[table]
    except:
        tables_columns = []
    listOfColumns = tuple(tables_columns.values())[0]
    print(listOfColumns)

    dictionary = create_dictionary__by_dict_and_a_funcName(create_label_entry, tables_columns.keys(),
                                                           (fram_midLeft, fram_midRight), listOfColumns)
    menu_but_category, menu_category = create_menu_drop_down_by_menuButton(fram_topLeft, dictionary, text='Category',
                                                                           column=1)
    return menu_but_category, menu_category


def on_closing_protocol_func(roots:list):
    print('close page')
    for root in roots:
        root.destroy()


def create_label_entry(roots=tuple, *columns):
    print(roots)
    print(columns)
    num_row = 1
    idx_root = 0
    cll = circle_list.CdlinkedList()
    cll.appends([0, 1])
    for i, field in enumerate(columns[0][1:]):
        num_column = i % 2
        if i % 2 == 0:
            idx_root = cll.next_value()
        if i % 4 == 0 and i != 0:
            num_row += 1
        # Create label and entry
        Strvariable = StringVar()
        label = Label(roots[idx_root], text=field, font=('times', 12))
        entry = Entry(roots[idx_root], textvariable=Strvariable, font=('times', 12))

        # Place label and entry in the grid
        label.grid(row=num_row, column=num_column * 2, padx=3, pady=3, sticky='w')
        entry.grid(row=num_row, column=num_column * 2 + 1, padx=3, pady=3, sticky='w')

        list_StrVariable_for_entries.append((Strvariable, field))
    return list_StrVariable_for_entries


def record_data_to_short_memory():
    class test(models.model):
        def __init__(self):
            for str_var, field in list_StrVariable_for_entries:
                setattr(self, field, str_var.get())

    for str_var, field in list_StrVariable_for_entries:
        print(str_var.get())
    return test
    pass


def sendData2printer():
    pass


# '-----------------------setup------------------------------'

# '-----------------------create main window------------------------------'
main_width, main_height = 870, 600
global window
window = create_top_window(title='Receipt', geometry=f'{main_width}x{main_height}+300+45')
# '-------------------------------variables---------------------------'
dic = {}
columns_name = ['id', 'category', 'seller_name', 'Name', 'Price', 'Quantity', 'Sum_price', 'Date',
                'time', 'cTime']
text_of_print_qr_btn = StringVar()
seller_Variable_for_Delete_and_Add = StringVar()
ent_name_of_product = StringVar()
ent_price = StringVar()
ent_quantity = StringVar()
ent_seller = StringVar()
ent_category = StringVar()
category_ent_textVariable = StringVar()
seller_name = StringVar()
name_of_printer = StringVar()
select_listBox_flag = IntVar()
qrFlag_print_IntVar = IntVar()
printing_flag = IntVar()
# search variables
product_name_search_strVar = StringVar()
price_search_strVar = StringVar()
seller_search_strVar = StringVar()
catrgory_search_strVar = StringVar()
# '-------------------------------initialization---------------------------'


# '-------------------------------frame---------------------------'
fram_topLeft, fram_topRight, fram_midLeft, fram_midRight, fram_BOTTOMLeft, fram_BOTTOMright = create_Frames(window,
                                                                                                            main_width,
                                                                                                            main_height,
                                                                                                            num_rows=3,
                                                                                                            num_columns=2)

# '-------------------------------memu---------------------------'

# menu_btnFile, menu_File = create_menu_drop_down_by_menuButton(fram_topLeft, {'Admin': (admin,)}, text='File')
# menu_but_category, menu_category = basic_features()
create_Nested_menu_drop_down({'file': [
    {'Admin': [('Create cateories structures', Categories_and_DB_manager, window),('Delete Data Base', Create_CSVfile_from_DB_and_del_DB_and_categories), {'Manage Data base':[('Manualy', manage_db_dynamically,),('Update data base by CSV file',updateDB_by_csv_files)]}, ]},
    ('Open sell page', open_sell_page,)],
    'Edit': [('print edit1 func', print, 'edit1')]}, window)
# '-------------------------------buttons---------------------------'
btn = Button(fram_topRight, text='Enter item', background='blue', foreground='white', font=('ariyal', 11),
             command=lambda: record_data_to_short_memory())
btn.grid(row=0, column=0)
btn2 = Button(fram_topRight, text='summation', background='red', font=('ariyal', 11),
              command=lambda: sendData2printer())
btn2.grid(row=0, column=1)

# Create a button to print the geometry
# button = tk.Button(root, text="Print Geometry", command=print_geometry)


window.mainloop()
