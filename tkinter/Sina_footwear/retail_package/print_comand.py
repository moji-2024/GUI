# from win32 import win32print
import win32print
font1 = {'height':8}
def print2printer(text,printer_name=''):
    if printer_name == '':
        printer_name = win32print.GetDefaultPrinter()
    handler_printer = win32print.OpenPrinter(printer_name)
    try:
        handler_job = win32print.StartDocPrinter(handler_printer, 1, ("Print Job",None,'RAW'))
        win32print.StartPagePrinter(handler_printer)
        win32print.WritePrinter(handler_printer,text.encode())
        cut_comand = b'\x1b\x69'
        win32print.WritePrinter(handler_printer, cut_comand)
        win32print.EndPagePrinter(handler_printer)
    except win32print.error as e:
        print('printing error:',e)
    # except pywintypes.error:
    #     print(6, 'ClosePrinter', 'The handle is invalid.')
    # finally:
    #     win32print.ClosePrinter(handler_printer)
    win32print.ClosePrinter(handler_printer)
# print2printer('test')

from escpos.printer import Usb

def print_img(path,idVendor=0x0416,idProduct=0x5011):
    # Initialize the printer
    printer = Usb(idVendor, idProduct)  # Adjust the vendor and product ID for your printer

    # Print the image
    printer.image(path)
    printer.cut()
