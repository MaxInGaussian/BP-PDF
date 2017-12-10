import numpy as np
import pandas as pd
from os import walk
from pdftables import get_tables
import re
import time

def extract_bp_records(filepath):
    print(filepath)
    pdffile = open(filepath, 'rb')
    result = get_tables(pdffile)
    columns = ['File Name', 'Gender', 'Date of Birth', 'Time', 'T', 'SBP', 'DBP', 'Pulse']
    bp_records = {col:[] for col in columns}
    patient_id, gender, date_str = None, 'M', None
    for page in result:
        for line in page:
            full_str = ''.join(line)
            lower_str = full_str.lower()
            if('patient id' in lower_str and 'start' in lower_str and patient_id is None):
                ind1 = lower_str.index('id')
                ind2 = lower_str.index('start')
                if(ind2-ind1 == 16):
                    patient_id = lower_str[ind1+4:ind2].upper()
            if('female' in lower_str):
                gender = 'F'
            if('date of birth' in full_str and '/' in lower_str): 
                ind1 = lower_str.index('/')# in all cases, '/' apears after DOB
                ind2 = lower_str[ind1+1:].index('/')
                if not(any(c.isalpha() for c in lower_str[ind1-4:ind1+ind2+4])):
                    #check for alphabetic letters
                    date_str = lower_str[ind1-4:ind1+ind2+4]
    for page in result:
        for line in page:
            f_line = []
            for txt in line:
                if(len(txt) > 0):
                    f_line.append(txt)
            real_line = ''.join(f_line)
            digits = ''.join(re.findall('\d+', real_line))
            if('/' in real_line):
                continue
            if(10 < len(digits) < 14 or (len(digits)==4 and 'E' in real_line)):
                if(':' in f_line[0] and len(f_line[0]) == 5 and\
                    f_line[1] in ['A', 'E', 'M']):
                    bp_records['Time'].append(f_line[0])
                    bp_records['T'].append(f_line[1])
                    if(f_line[1] == 'A' or f_line[1] == 'M'):
                        try:
                            bp_records['SBP'].append(int(f_line[2]))
                            bp_records['DBP'].append(int(f_line[3]))
                            bp_records['Pulse'].append(int(f_line[4]))
                        except:
                            bp_records['SBP'].append(np.nan)
                            bp_records['DBP'].append(np.nan)
                            bp_records['Pulse'].append(np.nan)
                    else:
                        bp_records['SBP'].append(np.nan)
                        bp_records['DBP'].append(np.nan)
                        bp_records['Pulse'].append(np.nan)
                    bp_records['Gender'].append(gender)
                    bp_records['Date of Birth'].append(date_str)
                    bp_records['File Name'].append(filepath.split('/')[-1][:-4])
                else:
                    if(':' in real_line and ('A' in real_line or
                        'E' in real_line or 'M' in real_line)):
                        time_ind = real_line.index(':')
                        time = real_line[time_ind-2:time_ind+3]
                        bp_records['Time'].append(time)
                        bp_records['T'].append(real_line[time_ind+3])
                        if(real_line[time_ind+3] == 'A' or
                            real_line[time_ind+3] == 'M'):
                            if(time_ind-2 == 0):
                                sbp_dbp_pul = real_line[time_ind+4:].replace(' ', '')
                                sbp, dbp, pul = sbp_dbp_pul[:3],sbp_dbp_pul[3:5],sbp_dbp_pul[5:]
                                bp_records['SBP'].append(int(sbp))
                                bp_records['DBP'].append(int(dbp))
                                bp_records['Pulse'].append(int(pul))
                            else:
                                sbp = real_line[:time_ind-2]
                                dbp, pul = real_line[time_ind+5:].split(' ')
                                bp_records['SBP'].append(int(sbp))
                                bp_records['DBP'].append(int(dbp))
                                bp_records['Pulse'].append(int(pul))
                        else:
                            bp_records['SBP'].append(np.nan)
                            bp_records['DBP'].append(np.nan)
                            bp_records['Pulse'].append(np.nan)
                        bp_records['Gender'].append(gender)
                        bp_records['Date of Birth'].append(date_str)
                        bp_records['File Name'].append(filepath.split('/')[-1][:-4])
    df = pd.DataFrame.from_dict(bp_records)[columns]
    df = df.drop_duplicates().set_index(['File Name'])
    return df

def extract_sleep_records(filepath):
    print(filepath)
    pdffile = open(filepath, 'rb')
    result = get_tables(pdffile)
    columns = ['File Name', 'In Bed', 'Out Bed', 'Latency (min)', 'Efficiency',
        'Total Time in Bed (min)', 'Total Sleep Time (TST) (min)',
        'Wake After Sleep Onset (WASO)', '# of Awakenings', 'Avg Awakening (min)']
    bp_records = {col:[] for col in columns}
    patient_id, gender, date_str = None, 'M', None
    for page in result:
        for line in page:
            f_line = []
            for txt in line:
                if(len(txt) > 0):
                    f_line.append(txt)
            real_line = ''.join(f_line)
            digits = ''.join(re.findall('\d+', real_line))
    df = pd.DataFrame.from_dict(bp_records)[columns]
    df = df.drop_duplicates().set_index(['File Name'])
    return df

regenerate = False
pdf_paths = []
for (dirpath, dirnames, filenames) in walk('PDF'):
    pdf_paths.extend(filenames)
if(not regenerate):
    for (dirpath, dirnames, csv_filenames) in walk('CSV'):
        for csv_filename in csv_filenames:
            if(csv_filename[:-4]+'.pdf' in filenames):
                filenames.remove(csv_filename[:-4]+'.pdf')
for pdf_path in sorted(pdf_paths):
    if('040' not in pdf_path):
        continue
    path = 'PDF/'+pdf_path
    extract_bp_records(path).to_csv('CSV/'+pdf_path[:-4]+'.csv')
timestamp = time.strftime('_%Y%m%d_%H%M%S')
print('Done extracting from subdirectory "PDF" !')
print('Generated new csv files !')