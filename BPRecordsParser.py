import numpy as np
import pandas as pd
from os import walk
from pdftables import get_tables
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
            if(len(f_line) < 2):
                continue
            if(':' in f_line[0] and len(f_line[0]) == 5 and\
                f_line[1] in ['A', 'E']):
                bp_records['Time'].append(f_line[0])
                bp_records['T'].append(f_line[1])
                if(f_line[1] == 'A'):
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
                # bp_records['ID'].append(patient_id)
                bp_records['Gender'].append(gender)
                bp_records['Date of Birth'].append(date_str)
                bp_records['File Name'].append(filepath.split('/')[-1][:-4])
    df = pd.DataFrame.from_dict(bp_records)[columns]
    df = df.drop_duplicates().set_index(['File Name'])
    return df


pdf_paths = []
for (dirpath, dirnames, filenames) in walk('PDF'):
    pdf_paths.extend(filenames)
result_df = None
for pdf_path in sorted(pdf_paths):
    if('BP' not in pdf_path):
        continue
    path = 'PDF/'+pdf_path
    if(result_df is None):
        result_df = extract_bp_records(path)
    else:
        result_df = result_df.append(extract_bp_records(path))
timestamp = time.strftime('_%Y%m%d_%H%M%S')
result_df.to_csv('BPRecords'+timestamp+'.csv')
print('Done extracting from subdirectory "PDF" !')
print('Generated new csv file "BPRecords'+timestamp+'.csv" !')