'''
Purpose: To search defined pattern from gateway log file and prepare summary report based on SN,FW,GWID,Error codes,File_size
Date: 23rd March,2020
Author: Hemin Patel
'''

from configparser import ConfigParser
import ast
from argparse import ArgumentParser
import argparse
import os
import re
import csv , sys
import time
from datetime import datetime
from datetime import timedelta

def time_duration(MAX,MIN):
    #set the date and time format
    date_format = "%H:%M:%S %Y"
    
    #convert string to actual date and time
    time1  = datetime.strptime(MIN, date_format)
    time2  = datetime.strptime(MAX, date_format)
    
    #find the difference between two dates
    diff = time2 - time1
    
    value = list(str(diff).split(', '))
    
    if len(value) == 2:
        return str(value[1])
    else:
        return str(value[0])
    
def is_valid_file(parser,arg):
    # Check given path is exist or not
    if not os.path.exists(arg):
        parser.error("The file path %s does not exist!" % arg)
    else:
        return arg

def Remove_existing_csv():
    # Remove existing Summary.csv file
    dir_name = os.getcwd()
    
    test = os.listdir(dir_name)
    
    for item in test:
        if item == 'Summary.csv':
            os.remove(os.path.join(dir_name, item))
    test = os.listdir(dir_name)

def main():
    # given argument as directory path
    parser = argparse.ArgumentParser()
    parser = ArgumentParser(description="correct filepath")

    parser.add_argument('--FilePath',
        help="Enter FilePath like /home/admin/GW/log",
        default=' ',
        type=lambda x: is_valid_file(parser,x),
        required=True)
    
    # Grab path from argument
    Path = sys.argv[1].strip('--')
    FilePaths = Path[9:]
    args = parser.parse_args()
    
    # Get argument and store filepath into variable
    File_Name = args.FilePath
    dir_name = os.getcwd()
    
    # Get Filenames 
    listFile = os.listdir(File_Name)

    # Blank filename list
    Name_File = []

    # Read configuration file
    parser1 = ConfigParser()
    parser1.read('Config.ini')
    
    # Read csv column from config.ini and split into Header
    csv_columns = parser1['Burn-in'] ['CSV_columns']
    Headers = csv_columns.split(',')

    # Read error code key,value and append to dict_data dictionary
    data = parser1['Burn-in']['Error_code']
    dict_data = ast.literal_eval(data)
    
    # Set Filename path and append to list
    for _FileName in listFile:
        Name_File.append(FilePaths+_FileName)

    '''
    Filename take from list,open it and find GWID,FW version and timestamps and append to relevant dict,calculate file size in MB
    '''
    _data = {}
    _all_data = {}

    for Log_File in Name_File:

        # Get modified date of file and store to dict
        created = os.path.getctime(Log_File)
        _time = time.ctime(os.path.getmtime(Log_File))
        creat_date = {'Log File Creation Date & Time':''}
        _date_time = _time[4:]
        creat_date['Log File Creation Date & Time'] = _date_time

        # Get file size and store to dict
        File_size = {'Log file Size (In MB)':' '}
        size = os.path.getsize(Log_File)
        F_size = size/(1024*1024)
        _size = round(F_size,2)
        File_size['Log file Size (In MB)'] = _size

        # Empty dict to store error key:value from error code
        new_dict = {}
        
        # Serial num find dict for all files
        SN = {'SN':0}
        sn = re.findall("[0-9]{0,6}$",Log_File)
        SN['SN'] = sn[0]
        
        # Fw version dict for all files
        FW = {'FW':''}

        with open(Log_File,'r',encoding="ISO-8859-1") as file:
            '''
            File open and search each error code and append to dict with key:value pair 
            '''
            contents = file.read()

            # Duration calculation from "sub1" string and Give in Minutes data
            T_d = {'Total_Duration (In minutes)':''}
            T_duration = re.findall('Sub1 Keep Alive Check...',contents)
            T_d['Total_Duration (In minutes)'] = len(T_duration)

            # GW rebbot due to external event and count >1 then append to dict
            Reboot = re.findall('Board: MX6ULL Volansys Gateway',contents)
            RB= {'GW Reboot Due to External Event':'0'}
            Rcount = 0
            for i in Reboot:
                if len(Reboot) > 1:
                    Rcount = len(Reboot) - 1
                else:
                    Rcount = 0
            RB['GW Reboot Due to External Event'] = Rcount

            # GWID and FW version parse and store into empty dict
            GWID = re.findall('GwID : ([0-9 a-f A-F]{27})',contents)

            #duration = re.findall('(\[.*(?:\:[0-9][0-9]){2}\ [0-9]{4}\]?)',contents)

            FW_version = re.findall('SW version : [0-9]{0,2}\.[0-9]{0,2}\.[0-9]{0,2}\.[0-9]{0,2}',contents)

            _version = list(dict.fromkeys(FW_version))

            _version_1 = [s.strip('SW version : ') for s in _version]

            if len(_version_1) == 0:
                FW['FW'] = 'NA'
            else:
                str1 = ''
                FW_Version = str1.join(_version_1)
                FW['FW'] = FW_Version
        
            GWid = {'GWID':0}
            if len(GWID) == 0:
                GWid['GWID'] = 'NA'
            else:
                _ID = list(dict.fromkeys(GWID))
                GWid['GWID'] = _ID
                GWid = {k: str(v[0]) for k,v in GWid.items()}
        
        '''
        Error code parsing into open file and get into dict if pattern match
        ''' 
        for key,value in dict_data.items():
            # error code have two or more value
            if type(dict_data[key]) == list:
                count = 0
                for _key in dict_data[key]:
                    _match_value = re.findall(_key,contents)
                    for item in _match_value:
                        count = count + 1
                
                new_dict[key] = dict_data[key]
                
                new_dict[key] = count

            else:
            # error code have only one value
                _count = 0
                _match_value_1 = re.findall(dict_data[key],contents)
                for item in _match_value_1:
                    if item in _match_value_1:
                        _count += 1
                    else:
                        _count = 1
                            
                new_dict[key] = dict_data[key]
                new_dict[key] = _count
        
        '''
        Append all separate dict to one dictionary key:value
        '''
        SN.update(creat_date)
        SN.update(FW)
        SN.update(GWid)
        SN.update(new_dict)
        SN.update(RB)
        SN.update(T_d)
        SN.update(File_size)
        
        # Map all values to one key from all dict key:value
        if _data:
            _combine = [_data,SN]
            for k in _data.keys():
                _all_data[k] = list(_all_data[k] for _all_data in _combine)
            _data = _all_data
        else:
            _data = SN
    
    # d is collect all data into dictionary 
    for item in range(len(listFile)-2):
        list_values(_all_data)
    return _all_data

def list_values(data):
    for key in data:
        a = data[key]
        _str_l = []
        for row in a:
            if type(row) == type([]):
                for item in row:
                    _str_l += [item]
            else:
                _str_l += [row]
        data[key] = _str_l
    return data

def report(SN,Headers):
    file_csv = "Summary_" + time.strftime("%d_%B_%Y-%H_%M_%S")+".csv"
    with open(file_csv,'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(SN.keys())
        writer.writerows(zip(*SN.values()))

if __name__ == '__main__':
    start_time = time.time()
    
    parser1 = ConfigParser()
    parser1.read('Config.ini')
    csv_columns = parser1['Burn-in'] ['CSV_columns']
    Headers = csv_columns.split(',')
    
    csv_data = main()
    report(csv_data,Headers)
    
    end_time = time.time()
    time1 = end_time-start_time

    b = round(time1,2)
    print('Total execution time of script is:-',b)