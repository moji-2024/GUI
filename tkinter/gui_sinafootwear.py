from tkinter import *
import pandas as pd
from datetime import datetime
from tkinter import messagebox as mb
from orm_db import sqlDB
from retail_package import print_comand,qrGenerator,QR_reader
from tkinter import filedialog as fd
import os
from functools import partial


# '-------------------------------bilding functions---------------------------'
def create_menu_drop_down(window_, dictionary, row=0, column=0, text='text', fg='black', bg='gray'):
    menu_button = Menubutton(window_, text=text, fg=fg, bg=bg, font='ariyal,13')
    menu_widget = Menu(menu_button, tearoff=0)
    for key, value in dictionary.items():
        menu_widget.add_command(label=key, background='black', foreground='red',
                                command=lambda: value())
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
                      flag_topLevel=True):
    if flag_topLevel == True:
        func_window_ = Toplevel(root_win)
        func_window_.grab_set()
    else:
        func_window_ = Tk()
    func_window_.title(title)
    func_window_.geometry(geometry)
    func_window_.resizable(width=width, height=height)
    return func_window_


def enter_newMenu_to_MenuButton(window_, menu_, name, func, database=sqlDB, tabel_name='product', db='sinafootwear'):
    if name != '':
        menu_.add_command(label=name, command=lambda: func(name))
        menu_.add_separator()
        database.insert4(tabel_name, db, name)
        window_.destroy()
    else:
        window_.destroy()


def delete_from_MenuButton(window_, menu_, str_var, database=sqlDB, tabel_name='product', db='sinafootwear',
                           column_for_pass_to_DB='category'):
    if str_var.get() != '' and str_var.get() != 'this fild must be fill out with correct value':
        result = delete_menu_command_by_label(menu_, str_var.get())
        if result == 'done':
            kwargs = {column_for_pass_to_DB: str_var.get()}
            database.delete4(tabel_name, db, **kwargs)
            window_.destroy()
            return
        try:
            num = menu_.index(str_var.get())
            if num == 0:
                window_.destroy()
                return
            label_name_ = menu_.entrycget(num + 1, 'label')
            kwargs = {column_for_pass_to_DB: label_name_}
            menu_.delete(num, num + 1)
            database.delete4(tabel_name, db, **kwargs)
            window_.destroy()
        except:
            str_var.set('this fild must be fill out with correct value')
    else:
        str_var.set('this fild must be fill out with correct value')


def create_dictionary_of_func(strVar, tabel_name='employees', db='sinafootwear'):
    d = {}
    for row in sqlDB.view4(table_name=tabel_name, db=db)[0]:
        name = row[1]
        d[name] = lambda: strVar.set('= ' + name)
    return d

def connect_scrollbar_to_widget(window_, widget, row_scr_vertical=0, column_scr_vertical=0, row_scr_horizontal=1,
                                column_scr_horizontal=1, scr_horizontal=True):
    vertical_scrollbar = Scrollbar(window_)
    widget.configure(yscrollcommand=vertical_scrollbar.set)
    vertical_scrollbar.configure(command=widget.yview)
    vertical_scrollbar.grid(row=row_scr_vertical, column=column_scr_vertical, sticky='ns')
    if scr_horizontal == True:
        horizontal_scrollbar = Scrollbar(window_, orient='horizontal')
        widget.configure(xscrollcommand=horizontal_scrollbar.set)
        horizontal_scrollbar.configure(command=widget.xview)
        horizontal_scrollbar.grid(row=row_scr_horizontal, column=column_scr_horizontal, sticky='we')
        return vertical_scrollbar, horizontal_scrollbar
    return vertical_scrollbar


# '-------------------------------main functions---------------------------'
def add_delete_category_manage_window():
    add_delete_cate_window = create_top_window(title='Enter Category')
    Entry(add_delete_cate_window, width=40, textvariable=category_ent_textVariable).grid(row=0, column=0)
    Button(add_delete_cate_window,
           text='Add',
           bg='white',
           fg='black',
           command=lambda: enter_newMenu_to_MenuButton(add_delete_cate_window, menu_category,
                                                       category_ent_textVariable.get(),
                                                       category_name_setter)).grid(row=1, column=0)
    Button(add_delete_cate_window,
           text='Delete',
           bg='white',
           fg='red',
           command=lambda: delete_from_MenuButton(add_delete_cate_window, menu_category,
                                                  category_ent_textVariable)).grid(row=1,
                                                                                   column=1)


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
        print(df.head(), '\n\n------')
    else:
        directoryOf_file = fd.askopenfilename(title='select file',
                                              filetypes=[('xml files', "*.xml"), ('exel files', "*.xlsx"),
                                                         ('exel files', "*.xls"), ])
        df = pd.read_excel(directoryOf_file)
        print(df.head(), '\n\n------')
    columns = df.columns
    for index, row in df.iterrows():
        update_dict = {}
        for column in columns:
            update_dict[column] = row[column]
        try:
            sqlDB.update('sinafootwear', 'storage', f'name_of_item = "{row["name_of_item"]}"', **update_dict)
        except:
            try:
                sqlDB.insert4('storage', 'sinafootwear', row['Category'], row['name_of_item'], row['Unit_price'], row['Size'],row['Quantity'])
            except:
                mb.showerror(title='Format Error', message='Format of file dose not match with DB format')
                return

def admin():
    pass

# '-----------------------setup------------------------------'
sqlDB.tabel_maker4('sunridge', 'sinafootwear', 'Category VARCHAR(60)', 'seller VARCHAR(60)', 'name_of_item VARCHAR(60)',
                'Unit_price float', 'Quantity Integer', 'Sum_price float', 'date_ date', 'time_ time', 'ctime time')
sqlDB.tabel_maker4('employees', 'sinafootwear', 'seller VARCHAR(60)')
sqlDB.tabel_maker4('product', 'sinafootwear', 'Category VARCHAR(60)')

# sqlDB.tabel_maker4('sunridge_storage', 'sinafootwear', 'Category VARCHAR(60)', 'Name_of_item VARCHAR(60)',
#                 'Unit_price integer', 'Color VARCHAR(60)','Size VARCHAR(10)','Quantity Integer')
#
# sqlDB.tabel_maker4('product_tag', 'sinafootwear','Tag VARCHAR(60)')
# '-----------------------create main window------------------------------'
window = create_top_window(title='Receipt', geometry='710x600+300+45', flag_topLevel=False)
# '-------------------------------initialization---------------------------'

# '-------------------------------frame---------------------------'
fram1 = Frame(window, width=690, height=25, bg='gray')
fram1.pack(side=TOP)
fram2 = Frame(window, width=690, height=25)
fram2.pack(side=TOP)
fram_mid = Frame(window, width=690, height=425)
fram_mid.pack(side=TOP)
fram_BOTTOM = Frame(window, width=690, height=25, bg='gray')
fram_BOTTOM.pack(side=TOP, fill='x')
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

# '-------------------------------memu---------------------------'
menu_but, menu_category = create_menu_drop_down(fram2, {'Add/Delete': lambda: add_delete_category_manage_window()},
                                                text='Category', )
menu_but2, menu_seller = create_menu_drop_down(fram1, {'Add/Delete': lambda: add_delete_seller_manage_window()},
                                               text='Seller', column=1)

# '-------------------------------buttons---------------------------'
Button(fram1, text='Admin', background='red', foreground='white', font=('ariyal', 11),
             command=lambda: admin()).grid(row=0, column=0)
btn = Button(fram1, text='Enter item', background='blue', foreground='white', font=('ariyal', 11),
             command=lambda: record_data_to_short_memory())
btn.grid(row=0, column=5)
btn2 = Button(fram1, text='summation', background='red', font=('ariyal', 11), command=lambda: printing())
btn2.grid(row=0, column=6)

btn3 = Button(fram_BOTTOM, text='extract files', background='green', font=('ariyal', 11),
              command=lambda: extract_files())
btn3.grid(row=0, column=0)
btn4 = Button(fram_BOTTOM, text='del memory', background='dark red', font=('ariyal', 11), command=lambda: del_memory())
btn4.grid(row=0, column=1)
btn5 = Button(fram_BOTTOM, text='summery', background='navy blue', fg='white', font=('ariyal', 11),
              command=lambda: summeryDB())
btn5.grid(row=0, column=2)
btn6 = Button(fram_BOTTOM, text='search', background='navy blue', fg='white', font=('ariyal', 11),
              command=lambda: search_filter_window())
btn6.grid(row=0, column=3)
btn7 = Button(fram_BOTTOM, text='Update storage', background='navy blue', fg='white', font=('ariyal', 11),
              command=lambda: update_storage())
btn7.grid(row=0, column=4)
qr_btn = Button(fram1, textvariable=text_of_print_qr_btn, background='red', font=('ariyal', 11),
                command=lambda: handelPrintQR(qr_btn, qrFlag_print_IntVar))
qr_btn.grid(row=0, column=0)
# '-------------------------------list-box--------------------------'
list_box = Listbox(fram_mid, width=60, height=17, font=75, selectforeground='red')
list_box.grid(row=0, column=1)
# '-------------------------------Entries---------------------------'
textvariable_width_list = [(ent_name_of_product, 25), (ent_price, 17), (ent_quantity, 5), (ent_seller, 15)]
# for index_, text_var,width_ in enumerate(textvariable_width_list):
#     if index_<3:
#         Entry(fram2,textvariable=text_var, font=35, fg='blue',width=width_).grid(row=1, column=index_ + 1)
#     else:
#         Entry(fram2, textvariable=text_var, font=35, fg='blue', width=width_,state='disabled').grid(row=0, column=index_)

ent = Entry(fram2, textvariable=ent_name_of_product, font=35, fg='blue', width=25)
ent.grid(row=1, column=1)
ent2 = Entry(fram2, textvariable=ent_price, font=35, fg='blue', width=12)
ent2.grid(row=1, column=2)
ent3 = Entry(fram2, textvariable=ent_quantity, font=35, fg='blue', width=10)
ent3.grid(row=1, column=3)

ent4 = Entry(fram1, textvariable=ent_seller, font=35, fg='blue', width=15)
ent4.grid(row=0, column=4)
ent4.insert(END, 'Unselected')
ent4.configure(state='disabled')
ent5 = Entry(fram2, textvariable=ent_category, font=35, fg='blue', width=12)
ent5.grid(row=1, column=0, sticky='w')
ent5.configure(state='disabled')
# '-------------------------------labels---------------------------'
for index, label in enumerate(['Enter name', 'Enter price', 'Quantity']):
    Label(fram2, text=label, font=20, fg='red').grid(row=0, column=index + 1)
# '-------------------------------text-boxs--------------------------'
# txt2 = Text(window,width=100,height=9,state='disable')
# txt2.place(y=250,x=25)
# '-------------------------------scrollbar---------------------------'
vertical_scr, horizontal_scr = connect_scrollbar_to_widget(fram_mid, list_box)


# '-------------------------------main functions---------------------------'


def search_into_db(window_):
    try:
        result, column = sqlDB.search4(
            'sunridge',
            'sinafootwear',
            seller=seller_search_strVar.get(),
            category=catrgory_search_strVar.get(),
            name_of_item=product_name_search_strVar.get(),
            Unit_price=price_search_strVar.get()
        )
    except:
        pass
    window_.destroy()
    if result == []:
        mb.showerror(title='Empty result', message='DataBase is empty')
        return -1
    top_win_ = create_top_window(title='Informations', geometry='800x600+400+100')
    listBox_ = Listbox(top_win_, height=20, width=57, font=('arial', 18))
    listBox_.grid(row=0, column=1)
    connect_scrollbar_to_widget(top_win_, listBox_)
    for i, elem in enumerate(result):
        listBox_.insert(i, elem)


def search_filter_window():
    search_adjust_win = create_top_window(title='Search', geometry='400x150+400+100')
    Label(search_adjust_win, text='seller:').grid(row=0, column=0)
    create_menu_drop_down(search_adjust_win, column=1, text='seller',
                          dictionary=create_dictionary_of_func(seller_search_strVar))
    Label(search_adjust_win, text='category:').grid(row=1, column=0)
    create_menu_drop_down(search_adjust_win, row=1, column=1, text='category',
                          dictionary=create_dictionary_of_func(catrgory_search_strVar, tabel_name='product'))
    Label(search_adjust_win, text='price:').grid(row=2, column=0)
    Entry(search_adjust_win, textvariable=price_search_strVar, width=40).grid(row=2, column=1)
    Label(search_adjust_win, text='Product Name:').grid(row=3, column=0)
    Entry(search_adjust_win, textvariable=product_name_search_strVar, width=40).grid(row=3, column=1)
    Button(search_adjust_win,
           text='Search',
           bg='white',
           fg='black',
           command=lambda: search_into_db(search_adjust_win)).grid(row=4, column=0)
    pass


def summeryDB():
    top_level = create_top_window(title='Get Summery from Data Bace', geometry='400x100+400+400')
    Label(top_level, text='Enter Date(YYYY-MM-DD)').grid(row=0, column=0)
    date_entry = Entry(top_level)
    date_entry.grid(row=0, column=1)
    btum_oky = Button(top_level, text='Oky', font=('ariyal', 14),
                      command=lambda: create_summery_files(date_entry.get()))
    btum_oky.grid(row=1, column=0, padx=40)

    def create_summery_files(input):
        if input == '':
            top_level.destroy()
            return -1
        data = sqlDB.view4('sunridge', 'sinafootwear')[0]
        try:
            if input.isdigit():
                if len(input) == 4:
                    input = input + '-01-01'
            date = datetime.fromisoformat(input)
        except:
            top_level.destroy()
            mb.showerror('Error', 'Unsupported Date')
            return -1
        directoryToPaste = fd.askdirectory(title='selected folder')
        save_summery_csv_and_txt_files_base_date(directoryToPaste, data, columns_name, date, 'category',
                                                 change_column=('Date', covert_strDate_to_date))
        top_level.destroy()
        mb.showinfo('Information', 'Done')


def covert_strDate_to_date(string):
    return datetime.fromisoformat(string)


def save_summery_csv_and_txt_files_base_date(path, data, columns_, date, groupby_splitor, change_column=None):
    group_df_obj = create_groupby_df(data, columns_, groupby_splitor, change_column=change_column)
    dict_data_summery = create_groupName_sumNum_sumPrice_meanPrice_from_groupby_df(group_df_obj, date)
    num_of_file = return_new_num_for_file_directory(path, set_directory=('summery',))
    df = pd.DataFrame(dict_data_summery)
    df.to_csv(f'{path}/summery_{num_of_file}.csv', index=False)
    df.to_string(f'{path}/summery_{num_of_file}.txt', index=False)


def create_groupName_sumNum_sumPrice_meanPrice_from_groupby_df(groupby_df, date_):
    dict_data = {'group': [], 'Sum_Item_numbers': [], 'Summation_price': [], 'Mean_price': []}
    for group in groupby_df:
        df_of_group = group[1]
        dict_data['group'].append(group[0])
        Item_numbers = df_of_group[df_of_group['Date'] >= date_].shape[0]
        dict_data['Sum_Item_numbers'].append(Item_numbers)
        Summation_price = df_of_group[df_of_group['Date'] >= date_]['Sum_price'].sum()
        dict_data['Summation_price'].append(Summation_price)
        Mean_price = df_of_group[df_of_group['Date'] >= date_]['Sum_price'].mean()
        dict_data['Mean_price'].append(Mean_price)
    return dict_data


def add_delete_seller_manage_window():
    top_level = create_top_window()
    Entry(top_level, width=40, textvariable=seller_Variable_for_Delete_and_Add).grid(row=0, column=0)

    Button(top_level, text='Add',
           command=lambda: enter_newMenu_to_MenuButton(top_level, menu_seller, seller_Variable_for_Delete_and_Add.get(),
                                                       set_seller_name, tabel_name='employees')).grid(row=1, column=0)
    Button(top_level, text='Delete', fg='red',
           command=lambda: delete_from_MenuButton(top_level, menu_seller, seller_Variable_for_Delete_and_Add,
                                                  tabel_name='employees',
                                                  column_for_pass_to_DB='seller')).grid(row=1, column=2)


def set_seller_name(input):
    seller_name.set(input)
    ent_seller.set(input)


def category_name_setter(input):
    ent_category.set(input)


def basic_features():
    for row in sqlDB.view4('employees', 'sinafootwear')[0]:
        name = row[1]
        func = partial(set_seller_name, name)
        menu_seller.add_command(label=name, command=func)
        menu_seller.add_separator()
    first_cat = ''
    for row in sqlDB.view4('product', 'sinafootwear')[0]:
        name = row[1]
        if first_cat == '':
            first_cat += name
        func = partial(category_name_setter, name)
        menu_category.add_command(label=name, command=func)
        menu_category.add_separator()
    ent_category.set(first_cat)
    text_of_print_qr_btn.set('Print_QR: Off')
    qrFlag_print_IntVar.set(0)


basic_features()


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


def extract_files():
    if sqlDB.view4('sunridge', 'sinafootwear')[0] == []:
        mb.showinfo('Information', 'Memory is empty!')
        return
    directoryToPaste = fd.askdirectory(title='select folder')
    db_data = sqlDB.view4('sunridge', 'sinafootwear')[0]
    num_of_file = return_new_num_for_file_directory(directoryToPaste, db_data)
    try:
        save_csv_and_txt_files(directoryToPaste, db_data, columns_name, 'category', num_of_file)
        mb.showinfo('Information', 'Done!')
    except:
        mb.showerror(title='Error', message='Fail Operation: Please select a folder')
        return


def create_groupby_df(data, columns_, groupby_splitor, change_column=None):
    df = pd.DataFrame(data, columns=columns_)
    if change_column != None:
        df[change_column[0]] = df[change_column[0]].apply(change_column[1])
    return df.groupby(groupby_splitor)


def save_csv_and_txt_files(path, data, columns_, groupby_splitor, exsist_num, change_column=None):
    df2 = create_groupby_df(data, columns_, groupby_splitor)
    for group_info in df2:
        group_name = group_info[0]
        group_info[1].to_csv(f'{path}/{group_name}_{str(exsist_num)}.csv', index=False)
        group_info[1].to_string(f'{path}/{group_name}_{str(exsist_num)}.txt', index=False)


def record_data_to_short_memory():
    if ent_name_of_product.get() == '':
        ent_name_of_product.set('please put a value here')
    if ent_quantity.get() == '' or ent_quantity.get() == '0':
        ent_quantity.set('1')
    if ent_quantity.get().isnumeric() == False:
        ent_quantity.set('enter integer')
    try:
        Uprice = float(ent_price.get())
    except:
        ent_price.set('enter number')
        return

    if ent_name_of_product.get() != 'please put a vlue here':
        if ent3.get().isnumeric() == True:
            dic.setdefault(list_box.index(END),
                           [ent_name_of_product.get(), ent2.get(), ent3.get(), float(ent3.get()) * float(ent2.get()),
                            ent_category.get()])
            list_box.insert(END,
                            f'Name: {ent_name_of_product.get()} ,,, Unit price: ${ent2.get()} ,,, Quantity: {ent3.get()} ,,, Sum price: {float(ent3.get()) * float(ent2.get())} ,,, Category: {ent_category.get()}')

            if qrFlag_print_IntVar.get() == 1:
                try:
                    print('predone')
                    outputPath = qrGenerator.genrateQR(
                        {'Name_of_product': ent_name_of_product.get(), 'Unit_price': ent2.get()})
                    print_comand.print_img(outputPath)
                    print('done')
                except:
                    pass


def printing():
    if list_box.get(0) == '':
        return
    try:
        confirm_win.destroy()
    except:
        pass
    if printing_flag.get() == 1:
        return
    printing_flag.set(1)
    # ------------------ time------------------
    now_time = str(datetime.now()).split('.')[0]
    # ------------------ make window------------------
    global pre_print_win
    pre_print_win = create_top_window(title='Show detail', geometry='500x500+100+100')
    # -------------------fram-----------------------
    p_fram = Frame(pre_print_win)
    p_fram.pack(side=TOP)
    p_fram3 = Frame(pre_print_win)
    p_fram3.pack(side=TOP)
    p_fram2 = Frame(pre_print_win, width=350)
    p_fram2.pack(side=TOP)
    # '------------------textbox---------------------'
    textbox = Text(p_fram2, width=40, height=25)
    textbox.tag_configure('bold', font='ariyal 18 bold')
    textbox.pack(side=RIGHT)
    # ------------------scrulbar--------------------
    scr = Scrollbar(p_fram2)
    scr.pack(side=LEFT, fill='y')
    textbox.configure(yscrollcommand=scr.set)
    scr.configure(command=textbox.yview)
    # ------------------button----------------------
    print_but = Button(p_fram, text='Print', foreground='red', command=lambda: handel_printing())
    print_but.pack(side=LEFT)
    ask_file_directory = Button(p_fram, text='Directory of printer',
                                command=lambda: fd.askopenfilename(title='selected file'))
    ask_file_directory.pack(side=LEFT)
    # ------------------label-----------------
    ent_label = Label(p_fram3, text="Set printer's name:")
    ent_label.pack(side=LEFT)
    # ------------------entry-----------------
    printer_entry = Entry(p_fram3, textvariable=name_of_printer)
    printer_entry.pack(side=LEFT)
    # ------------------text insert-----------------
    textbox.insert(END, f'Shoe Repair & Retail\n', 'bold')
    textbox.insert(END, f'        130-2525 36st NE Calgary\n'
                        f'Date: {now_time[:11]}__ Time: {now_time[11:]}\n---------------------------\n')
    subtotal = 0
    n = 0
    listOfstrs = ['Name:', 'Price:', 'Quantety:', 'sum price:']
    textbox.insert(END, 'Items:\n')
    for kay, values in dic.items():
        m = 0
        for value in values[:-1]:
            if m == 1 or m == 3:
                textbox.insert(END, f'{listOfstrs[m]} {value} \n')
            else:
                textbox.insert(END, f'{listOfstrs[m]} {value} ,,, ')
            m += 1
        textbox.insert(END, '-------\n')
        subtotal += float(values[-2])
        n += 1
    gst = round((subtotal * 0.05), 2)
    textbox.insert(END, f'Number of Items: {n}\n')
    textbox.insert(END, f'SUBTOTAL: ${subtotal}\n5% GST: {gst}\nTOTAL: {subtotal + gst}\n\n'
                        f'       Thank you for shopping with us\n'
                        f'       Phone: 403 288 2913\n'
                        f'       Website: www.sinafootwear.ca\n'
                        f'       Email: info@sinafootwear.ca\n\n\n\n')
    textbox.configure(state='disabled')

    def handel_printing():
        try:
            print_comand.print2printer(textbox.get(0.0, END), name_of_printer.get())
            print_comand.print2printer(textbox.get(0.0, END), name_of_printer.get())

            # ------------------ insert 2 sql------------------
            date = datetime.now()
            for value in dic.values():
                try:
                    sqlDB.insert4('sunridge', 'sinafootwear', value[4], seller_name.get(), value[0], value[1],
                               value[2], value[3], date.date(), date.strftime('%H:%M:%S'), date.ctime())
                except:
                    sqlDB.delete4('sunridge', 'sinafootwear')
                    sqlDB.insert4('sunridge', 'sinafootwear', value[4], seller_name.get(), value[0], value[1],
                               value[2], value[3], date.date(), date.strftime('%H:%M:%S'), date.ctime())
            else:
                dic.clear()
            list_box.delete(0, END)
            pre_print_win.destroy()
            printing_flag.set(0)
        except:
            mb.showerror(title='Error', message='Please ensure about printer connection.')
            pre_print_win.destroy()
            printing_flag.set(0)

    pre_print_win.bind('<Destroy>', make_normal_flag)

    pass


def hendel_entrys(event):
    if event.widget == ent:
        ent.delete(0, END)
    elif event.widget == ent2:
        ent2.delete(0, END)
    elif event.widget == ent3:
        ent3.delete(0, END)
    pass


def win_destroy(event):
    # print(event.widget)
    # print(event.type)
    if event.widget == list_box:
        try:
            pre_print_win.destroy()
            confirm_win.destroy()
        except:
            try:
                confirm_win.destroy()
            except:
                pass


def select_listBox(event):
    if list_box.get(0, END) == ():
        return
    if select_listBox_flag.get() == 1:
        return
    select_listBox_flag.set(1)
    curSelected = list_box.curselection()
    global confirm_win
    confirm_win = create_top_window(title='Confirmation', geometry='300x80+400+100')

    # -------------------fram-----------------------
    conf_fram = Frame(confirm_win)
    conf_fram.pack(side=TOP)
    conf_fram2 = Frame(confirm_win)
    conf_fram2.pack(side=TOP)
    # ------------------button----------------------
    yes = Button(conf_fram2, text='yes', foreground='red', font=('ariyal', 14), command=lambda: yes_command())
    yes.pack(side=LEFT)
    no = Button(conf_fram2, text='no', font=('ariyal', 14), command=lambda: no_command())
    no.pack(side=LEFT)
    # ------------------label-----------------
    ent_label = Label(conf_fram, text="Do you want to delete item:", font=('ariyal', 17))
    ent_label.pack(side=TOP)

    def yes_command():
        list_box.delete(curSelected[0])
        dic.pop(curSelected[0])
        confirm_win.destroy()

        # select_listBox_flag.set(0)

    def no_command():
        confirm_win.destroy()
        # select_listBox_flag.set(0)

    confirm_win.bind('<Destroy>', make_normal_flag)
    # confirm_win.mainloop()


def make_normal_flag(event):
    try:
        if event.widget == pre_print_win.winfo_toplevel():
            printing_flag.set(0)
        elif event.widget == confirm_win.winfo_toplevel():
            select_listBox_flag.set(0)
    except:
        try:
            if event.widget == confirm_win.winfo_toplevel():
                select_listBox_flag.set(0)
            # elif event.widget == pre_print_win.winfo_toplevel():
            #     printing_flag.set(0)
        except:
            pass


def del_memory():
    top_level = Toplevel(window)
    top_level.geometry('300x100+400+400')
    top_level.resizable(False, False)
    top_level.title('Delete memory')
    top_level.grab_set()
    label_entry = Label(top_level, text='Enter password')
    label_entry.grid(row=0, column=0)

    pass_entry = Entry(top_level)
    pass_entry.grid(row=0, column=1)

    btum_yes = Button(top_level, text='Yes', font=('ariyal', 14), command=lambda: yes_func())
    btum_yes.grid(row=1, column=0, padx=40)
    btum_no = Button(top_level, text='No', font=('ariyal', 14), command=lambda: top_level.destroy())
    btum_no.grid(row=1, column=1, sticky='E')

    def yes_func():
        if pass_entry.get() == 'password_try1':
            sqlDB.delete4('sunridge', 'sinafootwear')
            mb.showinfo('Information', 'Done!')
        top_level.destroy()

    pass


# '-------------------------------binding---------------------------'
list_box.bind('<<ListboxSelect>>', select_listBox)
ent.bind('<FocusIn>', hendel_entrys)
ent2.bind('<FocusIn>', hendel_entrys)
ent3.bind('<FocusIn>', hendel_entrys)
# ent.bind('<FocusOut>',hendel_entrys)
window.bind('<Destroy>', win_destroy)
window.mainloop()
