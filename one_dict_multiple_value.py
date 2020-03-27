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
    
    '''
    Read csv column from config.ini and split into Header
    '''
    csv_columns = parser1['Burn-in'] ['CSV_columns']
    Headers = csv_columns.split(',')

    '''
    Read error code key,value and append to dictionary
    '''
    data = parser1['Burn-in']['Error_code']
    dict_data = ast.literal_eval(data)
    
    '''
    Set Filename path and append to list
    '''
    for i in listFile:
        #print("Filename:-",i)

        Name_File.append(FilePaths+i)
    print("len of files:-",len(listFile))
    '''
    Filename take from list,open it and find GWID,FW version and timestamps and append to relevant dict,calculate file size in MB
    '''
    _data = {}
    d = {}

    for NF in Name_File:
        File_size = {'File_size':' '}
        size = os.path.getsize(NF)
        a = size/(1024*1024)
        b = round(a,2)
        
        File_size['File_size'] = b

        new_dict = {}
        
        SN = {'SN':0}
        
        sn = re.findall("[0-9]{0,6}$",NF)
        
        SN['SN'] = sn[0]        
        
        TIME_l = []
        FW = {'FW':''}

        with open(NF,'r',encoding="ISO-8859-1") as file:
            '''
            File open and search each error code and append to dict with key:value pair 
            '''
            contents = file.read()
            T_d = {'T_d':''}
            T_duration = re.findall('Sub1 Keep Alive Check...',contents)
            T_d['T_d'] = len(T_duration)
            Reboot = re.findall('Board: MX6ULL Volansys Gateway',contents)
            RB = {'RB':'0'}
            Rcount = 0
            for i in Reboot:
                if len(Reboot) > 1:
                    Rcount = len(Reboot) - 1
                else:
                    Rcount = 0
            RB['RB'] = Rcount

            GWID = re.findall('GwID : ([0-9 a-f A-F]{27})',contents)

            duration = re.findall('(\[.*(?:\:[0-9][0-9]){2}\ [0-9]{4}\]?)',contents)

            FW_version = re.findall('SW version : [0-9]{0,2}\.[0-9]{0,2}\.[0-9]{0,2}\.[0-9]{0,2}',contents)

            version = list(dict.fromkeys(FW_version))

            version1 = [s.strip('SW version : ') for s in version]

            if len(version1) == 0:
                FW['FW'] = 'NA'
            else:
                str1 = ''
                _Version = str1.join(version1)
                FW['FW'] = _Version

            DURATION = list(dict.fromkeys(duration))
            TIME = []
            for T in DURATION:
                time_d = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4}',T)
                TIME.append(time_d)
            
            TIME_u = sum(TIME, [])
            TIME_l = list(dict.fromkeys(TIME_u))
        
            GWid = {'GWID':0}
            if len(GWID) == 0:
                GWid['GWID'] = 'NA' 
            else:
                ID = list(dict.fromkeys(GWID))
                GWid['GWID'] = ID
                GWid = {k: str(v[0]) for k,v in GWid.items()}
        
        '''
        Error code parsing into open file and get into dict if pattern match
        ''' 
        for key,value in dict_data.items():
            # error code have two or more value
            if type(dict_data[key]) == list:
                count = 0
                for i in dict_data[key]:
                    y = re.findall(i,contents)
                    for i in y:
                        count = count + 1
                
                new_dict[key] = dict_data[key]
                
                new_dict[key] = count

            else:
            # error code have only one value
                count1 = 0
                y = re.findall(dict_data[key],contents)
                for k in y:
                    if k in y:
                        count1 += 1
                    else:
                        count1 = 1
                            
                new_dict[key] = dict_data[key]
                new_dict[key] = count1
        '''
        Append all separate dict to final dictionary key:value
        '''
        SN.update(FW)
        SN.update(GWid)
        SN.update(new_dict)
        SN.update(RB)
        SN.update(T_d)
        SN.update(File_size)
        #report(SN,Headers)
        #print("Final dict:-",SN)
        print("###########################")
        
        print("data dict:",_data)
        if _data:
            #print("if data dict not empty...")
            #print("_data:",_data)
            #print("SN:",SN)
            ds = [_data,SN]
            for k in _data.keys():
                d[k] = list(d[k] for d in ds)
            #print("$$$ if data",d)
            _data = d
        else:
            #print("else data dict empty...")
            _data = SN
    print("#############")
    print("data:-",d)
    print("len of files:-",len(listFile)-2)
    print("#############")
    for i in range(len(listFile)-2):
        list_values(d)
    #print("len of func execute:",d)
    return d

def list_values(d):
    for key in d:
        a = d[key]
        s = []
        for row in a:
            if type(row) == type([]):
                for item in row:
                    s += [item]
            else:
                s += [row]
        d[key] = s
    #print("csv_data",d)
    return d

def report(SN,Headers):
    with open('Summary.csv', 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=Headers)
        if csvfile.tell() == 0:
            writer.writeheader()
            w = csv.DictWriter(csvfile, SN.keys())
            w.writerow(SN)
        else:
            w = csv.DictWriter(csvfile, SN.keys())
            w.writerow(SN)

if __name__ == '__main__':
    start_time = time.time()
    Remove_existing_csv()
    csv_data = main()
    print("Data of CSV:-",csv_data)    
    end_time = time.time()
    time1 = end_time-start_time
    b = round(time1,2)
    print('Total execution time of script is:-',b)