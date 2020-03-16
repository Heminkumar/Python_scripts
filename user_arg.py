'''
Purpose: Generate zip files based on user requirements (like zip file count, zip contains only error.json, zip contains both sysother and tpms)
Author: Hemin Patel
'''

# Run as:- python user_arg.py --FWversion=3.8.0.0 --zipRange=any int value --fileName1=tpmsData.csv --fileName2=sysOtherData.csv
# Run as:- python user_arg.py --FWversion=3.8.0.0 --zipRange=any int value --fileName1=error.json

import argparse
import sys
import os
from zipfile import ZipFile
import time
import logging

def generate(time_val):

    # Create file append format e.g "__CG_1583663261.zip"
    ext = str('.')+'zip'
    y = "{}{}".format(time_val,ext)
    return "{}{}".format('__CG_',y)

def main():
    parser = argparse.ArgumentParser()
   
    parser.add_argument('--FWversion',
        help="enter firmware version like 3.8.0.0",
        default='3.0.0.0',
    	required=True)

    parser.add_argument('--zipRange',
        help="How much zip files creation",
        type=int,
        default=1,
        required=True
    )

    parser.add_argument('--fileName1',
        help="fileName1 add to create the zip",
        type=str,
        default=1,
        required=True
    )

    parser.add_argument('--fileName2',
        help="fileName2 add to create the zip",
        type=str,
        default=0
        #required=false
    )

    args = parser.parse_args()

    version = args.FWversion
    #print(version)
    list1 = version.split('.')
    #print(list1)
    filename1 = args.fileName1
    #print(filename1)
    filename2 = args.fileName2
    zipRange = args.zipRange
      # take current time
    time_val = int(time.time())
        # take blank list and version format with first '0'
    pad_list = []
    for i in list1:
        s1 = '0'+i
        pad_list.append(s1)
        # filename blank list and append with zip file name    
    zip_filename = []
        # Generate 1500 zip files
    for i in range(0,zipRange):
        x = generate(time_val) 
        FN = 'R'+pad_list[0]+'_'+pad_list[1]+'_'+pad_list[2]+'_'+pad_list[3]+x
        zip_filename.append(FN)
        time_val = time_val + 900 # 15min = 15*60 = 900 sec
        # Zip file create for all fileName
    #print(zip_filename)
    if filename1 == 'error.json':
        print("enter for if and then for")
        for i in zip_filename:
            print('entering in if loop')
            #print(i)
            Rdiag(i,filename1)
    elif filename1 == 'sysOtherData.csv' and filename2 == 'tpmsData.csv':
     	print('entering in elif loop1')
     	for i in zip_filename:
            print('entering in elif loop for DataStorage')
            #print(i)
            DataStorage(i,filename1,filename2)
    elif filename2 == 'sysOtherData.csv' and filename1 == 'tpmsData.csv':
     	print('entering in elif loop2')
     	for i in zip_filename:
            print('entering in elif loop for DataStorage')
            #print(i)
            DataStorage(i,filename1,filename2)
    elif filename1 == 'sysOtherData.csv':
    	logging.error("Please enter both filenames tpmsData.csv and sysOtherData.csv...")
    elif filename1 == 'tpmsData.csv':
    	logging.error("Please enter both filenames tpmsData.csv and sysOtherData.csv...")	
    elif filename1 == 'error.json' and filename2 == 'tpmsData.csv':
        logging.error('Please enter only error.json as a filename1 or enter both filenames tpmsData.csv and sysOtherData.csv...')
    elif filename1 == 'tpmsData.csv' and filename2 == 'error.json':
        logging.error('Please enter only error.json as a filename1 or enter both filenames tpmsData.csv and sysOtherData.csv...')    
    elif filename1 == 'sysOtherData.csv' and filename2 == 'error.json':
     	logging.error('Please enter only error.json as a filename1 or enter both filenames tpmsData.csv and sysOtherData.csv...')
    elif filename1 == 'error.json' and filename2 == 'sysOtherData.csv':
     	logging.error('Please enter only error.json as a filename1 or enter both filenames tpmsData.csv and sysOtherData.csv...') 	
    elif filename1 == 'error.json' and filename2 == 'error.json':
     	logging.error('Please enter only error.json as a filename1 and remove filename2...')

def Rdiag(fileName,filename1):
    
    #create a ZipFile object
    zipObj = ZipFile(fileName,'w')
    # Add multiple files to the zip
    zipObj.write(filename1)

    # close the Zip File
    zipObj.close()

def DataStorage(fileName,filename1,filename2):
    print('Storage as zip file')
       #create a ZipFile object
    zipObj = ZipFile(fileName,'w')

    # Add multiple files to the zip
    zipObj.write(filename1)
    zipObj.write(filename2) 

    # close the Zip File
    zipObj.close()


def ZipFile_move():
    try:
        os.system("rm -rf zip*")
    except:
        print("Folder is not present...")
    finally:
        # zip folder create and move it to folder
        os.mkdir('zip_' + time.strftime("%Y_%m_%d-%H_%M_%S"))
        os.system('mv R0* zip*')

if __name__ == '__main__':
	main()
	ZipFile_move()