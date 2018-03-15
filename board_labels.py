"""File generates Board labels for any project."""
import os
from ftplib import FTP
from flask import flash, url_for


DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))
LABEL_PATH = os.path.join(DATA_FOLDER, 'static/label.txt')


def write_doc(text):
    """writes array "text" to file"""
    try:
        with open(LABEL_PATH, 'w') as file:
            file.writelines(text)
    except PermissionError:
        print('could not open File!')
    except:
        print("Unexpected error, exiting...")
        exit()
def generate_code(code, number, text=None):
    """generates code for each line"""
    code_number = code+str(number)
    if not text:
        text = ['m m\r\n']
    text.append('J\r\n')
    text.append('S l1;0,0,15,18,15,18,2;Board_Label\r\n')
    text.append('O R\r\n')
    text.append('T 0.5,14,0,5,2;'+code_number+'\r\n')
    text.append('B 0.5,0,0,QRCODE+MODEL2,0.5;'+code_number+'\r\n')
    text.append('A 2\r\n')
    return text

def generate_label(code_number, code_url=None):
    """generates code for each line"""
    #print(code_url or code_number)
    text = ['m m\r\n']
    text.append('J\r\n')
    text.append('S l1;0,0,15,18,15,18,2;Board_Label\r\n')
    text.append('O R\r\n')
    text.append('T 1,13.5,0,5,2;'+code_number+'\r\n')
    text.append('B 1,0,0,QRCODE+MODEL2,0.4;'+(code_url or code_number)+'\r\n')
    text.append('A 2\r\n')
    
    return text

def print_label(address, user='anonymous', passwd=None):
    #print(address+' '+user+" "+str(passwd))
    try:
        with FTP(address, user='root', passwd='0000') as ftp:
            ftp.cwd('/execute')
            with open(LABEL_PATH, 'rb') as file:
                #print('Sending File')
                ftp.storbinary("STORE LABEL.txt", file, callback=None)
    except:
        flash("Label could not be printed", 'warning')
        return
        
    flash('check labelprinter for your label', "success")
    
def callback_():
    print(".")
        
def main():
    """creates Label and saves under label.txt"""
    name = input('Enter the short Board name (max 3 chars): ')
    while len(name)>3 and len(name) == 0:
        name = input('Please enter a name with max. 3 chars: ')
    min_value = input('Please enter the start value for the counter (default is 1): ')
    try:
        if min_value:
            min_value = int(min_value)
        else:
            min_value = 1
        number = int(input('Please enter the number of labels to be printed: '))
    except ValueError:
        print('Please enter an integer')
    i = min_value
    text = None
    while i < (min_value+number):
        text = generate_code(name, i, text)
        i+=1
    write_doc(text)


if __name__=='__main__':
    config = []
    try:
        with open('./config.ini', 'r') as file:
            config = file.readlines()
    except FileNotFoundError:
        print('init needed.')
    if not config:
        with open('./config.ini', 'w') as file:
            config = ['labelprinter01.internal.sdi.tools\n']
            config.append('root\n')
            config.append('0000\n')
            file.writelines(config)
    main() 
    print_label(config[0].strip('\n'),config[1].strip('\n'),config[2].strip('\n'))   