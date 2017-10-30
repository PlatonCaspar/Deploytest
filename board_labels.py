"""File generates Board labels for any project."""
from ftplib import FTP
from flask import flash


def write_doc(text):
    """writes array "text" to file"""
    try:
        with open('./static/label.txt', 'w') as file:
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
    text.append('S 0,0,19,42,100\r\n')
    text.append('O R\r\n')
    text.append('T 3,15,0,5,3;'+code_number+'\r\n')
    text.append('B 2,3,0,QRCODE+MODEL1,0.3;'+code_number+'\r\n')
    text.append('A 1\r\n')
    return text

def generate_label(code_number):
    """generates code for each line"""
    text = ['m m\r\n']
    text.append('J\r\n')
    text.append('S 0,0,19,42,100\r\n')
    text.append('O R\r\n')
    text.append('T 3,15,0,5,3;'+code_number+'\r\n')
    text.append('B 2,3,0,QRCODE+MODEL1,0.3;'+code_number+'\r\n')
    text.append('A 1\r\n')
    return text

def print_label(adress, user='anonymous', passwd=None):
    #print(adress+' '+user+" "+passwd)
    try:
        with FTP(adress, user='root', passwd='0000') as ftp:
            ftp.cwd('/execute')
            with open('./static/label.txt', 'rb') as file:
                print('Sending File')
                ftp.storbinary("STORE LABEL.txt", file, callback=None)
    except:
        flash("Label could not be printed", 'warning')
    

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
            config = ['10.11.5.2\n']
            config.append('root\n')
            config.append('0000\n')
            file.writelines(config)
    main() 
    print_label(config[0].strip('\n'),config[1].strip('\n'),config[2].strip('\n'))   