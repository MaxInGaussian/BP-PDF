import numpy as np
import pandas as pd
from os import walk
from pdftables import get_tables
import time

def extract_bp_records(filepath):
    pdffile = open(filepath, 'rb')
    result = get_tables(pdffile)
    columns = ['ID', 'gender', 'date of birth', 'time', 'T', 'SBP', 'DBP', 'pulse']
    bp_records = {col:[] for col in columns}
    patient_id, gender, date_str = None, 'M', None
    for page in result:
        for line in page:
            full_str = ''.join(line).lower()
            if('patient id' in full_str and 'start' in full_str and patient_id is None):
                ind1 = full_str.index('id')
                ind2 = full_str.index('start')
                if(ind2-ind1 == 16):
                    patient_id = full_str[ind1+4:ind2].upper()
            if('female' in full_str):
                gender = 'F'
            if('date of birth: ' in full_str and '/' in full_str and date_str is None): 
                ind1 = full_str.index('/')# in all cases, '/' apears after DOB
                ind2 = full_str[ind1+1:].index('/')
                if not(any(c.isalpha() for c in full_str[ind1-4:ind1+1+ind2+1+2])):
                    #check for alphabetic letters
                    date_str = full_str[ind1-4:ind1+1+ind2+1+2]
    for page in result:
        for line in page:
            f_line = []
            for txt in line:
                if(len(txt) > 0):
                    f_line.append(txt)
            if(len(f_line) < 2):
                continue
            if(':' in f_line[0] and len(f_line[0]) == 5 and\
                f_line[1] in ['A', 'E']):
                bp_records['time'].append(f_line[0])
                bp_records['T'].append(f_line[1])
                if(f_line[1] == 'A'):
                    try:
                        bp_records['SBP'].append(int(f_line[2]))
                        bp_records['DBP'].append(int(f_line[3]))
                        bp_records['pulse'].append(int(f_line[4]))
                    except:
                        bp_records['SBP'].append(np.nan)
                        bp_records['DBP'].append(np.nan)
                        bp_records['pulse'].append(np.nan)
                else:
                    bp_records['SBP'].append(np.nan)
                    bp_records['DBP'].append(np.nan)
                    bp_records['pulse'].append(np.nan)
                bp_records['ID'].append(patient_id)
                bp_records['gender'].append(gender)
                bp_records['date of birth'].append(date_str)
    df = pd.DataFrame.from_dict(bp_records)[columns]
    df = df.drop_duplicates().set_index(['time'])
    return df


pdf_paths = []
for (dirpath, dirnames, filenames) in walk('PDF'):
    pdf_paths.extend(filenames)
    print(filenames)
result_df = None
for pdf_path in pdf_paths:
    path = 'PDF/'+pdf_path
    if(result_df is None):
        result_df = extract_bp_records(path)
    else:
        result_df = result_df.append(extract_bp_records(path))
timestamp = time.strftime('_%Y%m%d_%H%M%S')
result_df.to_csv('BPRecords'+timestamp+'.csv')
print('Done extracting from subdirectory "PDF" !')
print('Generated new csv file "BPRecords'+timestamp+'.csv" !')