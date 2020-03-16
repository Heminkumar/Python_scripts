# Parse Cab GW log and filter,count based on keyword from output file 
######################################################################
from os import listdir
import csv
import configparser
import os
import time
import sys

stringToMatch = ['U-Boot','Sub1 keep alive failed','LTE keep alive failed','Application Terminated','CAB App Stopped','Reboot the system due to','SIM Not Present','No Operator Info', 'Status']

matchedLine = ''

start_time = time.time()

if len(sys.argv) < 2:
    print("You must provide log file path !!!")
    exit()
else:
    fn = sys.argv[1]

    list = os.listdir(fn)

    my_dict = {} 

    csv_columns = ['FileName'] + stringToMatch

    if os.path.exists(fn):
        fileNamePath = fn
        outputFileName = 'GW_output_log_file_'
    #outputSummary = 'GW_summary_'
 
    # Remove contents of output file
        dir_name = os.getcwd()
        test = os.listdir(dir_name)
        for item in test:
            if item.startswith("GW_output_log_file"):
                os.remove(os.path.join(dir_name, item))
    
        for item in test:
            if item.startswith("GW_summary_"):
                os.remove(os.path.join(dir_name, item))

    # Log file parser based on keywords and write to o/p file
        for i in list:
            fileName = fileNamePath+i
            outputfileName = outputFileName+i
        #outputSummary = 'GW_summary_'+i

            with open(fileName, 'r',encoding="ISO-8859-1") as file:
                for line in file:
                    for i in stringToMatch:
                        if i in line:
                            matchedLine = line
                            with open(outputfileName, 'a') as file:
                                file.write(matchedLine)
                            break

     # Print summary report on console from o/p file
            print("## Summary of I/P log file:-",fileName)
            print('##########################################################################')
            my_dict[fileName] = {} 
            for i in stringToMatch[:-1]:
                print(i,':',open(outputfileName, 'r').read().count(i))
            for i in stringToMatch:
                my_dict[fileName].update({i:open(outputfileName, 'r').read().count(i)})
            print('##########################################################################')
#print("dict:",my_dict)

    with open('summary.csv', 'w') as csvfile:  
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        if csvfile.tell() == 0:
            writer.writeheader()
        for file_name in my_dict:
            values = {}
            values[csv_columns[0]] = file_name
            for field in csv_columns[1:]:
                values[field] = my_dict[file_name][field]
        #print(values)
            values[csv_columns[-1]] = 'Fail' if (values[csv_columns[1]] > 2 or values[csv_columns[4]] >= 1 or values[csv_columns[6]] >= 1)  else 'Pass'
            writer.writerow(values) 

os.system('rm -rf GW_output_log_file*')

end_time = time.time()
print('Total execution time of script is:-',end_time-start_time)
