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

def total_duration(old):
    # Time length >=2 then calculate time duration
    if len(old) >= 2:
        START = min(old)
        END = max(old)
        D = time_duration(END,START)
        return D
    else:
        if len(old) == 1:
            return max(old)
        else:
            return 0

def list_len(x):
    if len(x) == 0:
        return '0:00:00'
    elif len(x) == 1:
        for i in x:
            y = i.split(' ')
            return y[0]
    else:
        a = total_duration(x)
        return a

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
    
    '''
    Filename take from list,open it and find GWID,FW version and timestamps and append to relevant dict,calculate file size in MB
    ''' 
    
    for NF in Name_File:
        print(NF)
        created = os.path.getctime(NF)
        
        print("Last modified: %s" % time.ctime(os.path.getmtime(NF)))
        #tm.append(time.ctime(os.path.getmtime(NF)))
        tm = time.ctime(os.path.getmtime(NF))
        print("tm:",tm)
        print(type(tm))
        creat_date = {'date':'00:00:00'}
        y = tm[4:]
        print(y)
        # for i in y:
        # find = re.findall('\d{2}:\d{2}:\d{2}',tm)
        # print("find",find)
        #new = [re.sub('\d{2}:\d{2}:\d{2}','', y)]
        #print(new)
        creat_date['date'] = y
        print("date:-",creat_date)


        # for i in tm:
        #     find = re.findall('\d{2}:\d{2}:\d{2}',i)
        #     #print("find",find)
        #     creat_date['date'] = find
        # creat_date = {k: str(v[0]) for k,v in creat_date.items()}
        #print("date:-",creat_date)

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
        Timestamp diff and sum calculation difference
        '''
        old = []
        latest = []
        other = []
        for i in TIME_l:
            if i.endswith('2000'):
                old.append(i)
            elif i.endswith('2020'):
                latest.append(i)
            elif i.endswith('2018'):
                other.append(i)
        
        Total = []
        old = list_len(old)

        latest = list_len(latest)

        other = list_len(other)

        Total.append(old)
        Total.append(latest)
        Total.append(other)
        
        def to_td(Total):
            ho, mi, se = Total.split(':')
            return timedelta(hours=int(ho), minutes=int(mi), seconds=int(se))
        total = str(sum(map(to_td, Total), timedelta()))

        duration = {'Time':''}
        duration['Time'] = total

        '''
        Append all separate dict to final dictionary key:value
        '''
        SN.update(creat_date)
        SN.update(FW)
        SN.update(GWid)
        SN.update(new_dict)
        SN.update(RB)
        SN.update(T_d)
        SN.update(File_size)
        
        print("Final dict:-",SN)
        
        '''
        Append final values of single GW on summary csv report
        '''
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
    main()
    end_time = time.time()
    time1 = end_time-start_time
    b = round(time1,2)
    print('Total execution time of script is:-',b)