"""File generates Board labels for any project."""
import os
from ftplib import FTP
from flask import flash, url_for
import data_Structure

# from data_Structure import app
# TESTING = False

DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))
_LABEL_PATH = os.path.join(DATA_FOLDER, 'static/label.txt')
LABEL_PATH = os.path.join(DATA_FOLDER, 'static/')


def write_doc(text):
    """writes array "text" to file"""
    try:
        with open(_LABEL_PATH, 'w') as file:
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


def generate_label(code_number, code_url=None, text=None):
    """generates code for each line"""
    #print(code_url or code_number)
    if not text:
        text = ['m m\r\n']
    text.append('J\r\n')
    text.append('S l1;0,0,15,18,15,18,2;Board_Label\r\n')
    text.append('O R\r\n')
    text.append('T 1,13.5,0,5,2;'+code_number+'\r\n')
    text.append('B 1,0,0,QRCODE+MODEL2,0.4;'+(code_url or code_number)+'\r\n')
    text.append('A 2\r\n')
    
    return text


def print_label(address, text, user='root', passwd="0000", _flash=True):
    #print(address+' '+user+" "+str(passwd))
    if data_Structure.app.config["TESTING"]:
        return
    # if TESTING:
    #     print("TESTING")
    #     return
    try:
        with FTP(address, user=user, passwd=passwd) as ftp:
            ftp.cwd('/execute')
            path = os.path.join(LABEL_PATH, "{}.txt".format(hash(str(text)))) # https://stackoverflow.com/questions/7027199/hashing-arrays-in-python
            try:
                with open(path, 'w') as file:
                #print('Sending File')
                    # pass
                    file.writelines(text)
            except Exception as e:
                raise Exception("An Error occured in //print_label()//_0_\n{}\n{}".format(e, text))
                
            try:
                with open(path, 'rb') as file:
                    ftp.storbinary("STORE LABEL.txt", file, callback=None)
                    path = file.name
            except Exception as e:
                raise Exception("An Error occured in //print_label()//_1_\n{}".format(e))
                

            os.remove(path)
    except Exception as e:
        flash("Label could not be printed\n{}".format(e), 'warning')
        return
    if _flash:
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


def print_place_label(place):
    text = generate_label(str(place.id))
    print_label("printer_ip_address", text)


def print_container_label(container):
    text = generate_label("""container{}""".format(container.id))
    print_label("printer_ip_address", text)
  

def print_part_label(part):
    text = generate_label("""IDS{}""".format(part.ids))
    print_label("printer_ip_address", text)


def print_device_label(device):
    try:
        code_url = url_for('show_device', device_id=device.device_id, _external=True)
    except:
        pass
    label = board_labels.generate_label(device.device_name, code_url=code_url)
    print_label("printer_ip_address", label)


if __name__=='__main__':
    config = []
    try:
        with open('./config.ini', 'r') as file:
            config = file.readlines()
    except FileNotFoundError:
        print('init needed.')
    if not config:
        with open('./config.ini', 'w') as file:
            config = ['printer_ip_address\n']
            config.append('root\n')
            config.append('0000\n')
            file.writelines(config)
    main() 
    # print_label(config[0].strip('\n'),config[1].strip('\n'),config[2].strip('\n'))   