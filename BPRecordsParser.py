import numpy as np
import pandas as pd
from os import walk
from pdftables import get_tables

def extract_bp_records(filepath):
    pdffile = open(filepath, 'rb')
    result = get_tables(pdffile)
    columns = ['ID', 'gender', 'date of birth', 'time', 'T', 'SBP', 'DBP', 'pulse']
    bp_records = {col:[] for col in columns}
    patient_id, gender, date_str = None, 'M', None
    for page in result:
        for line in page:
            full_str = ''.join(line).lower()
            print(full_str)
            if('patient id' in full_str and 'date' in full_str and patient_id is None):
                ind1 = full_str.index('id')
                while(full_str[ind1].isalpha() == False): #never entered (?)
                    ind1 += 1
                    print('ind1 : ',ind1,' ',full_str[ind1])
                ind2 = full_str.index('date')
                print('ind2 : ',ind2,' ',full_str[ind2])
                print('ind2-ind1 : ',ind2-ind1)
                if(ind2-ind1 == 14): # look for perfect line
                    if(full_str[ind1+2:ind2].isalpha()==True):
                        patient_id = full_str[ind1+2:ind2].upper()
                        print('patient_id :',full_str[ind1+2:ind2])
            if('female' in full_str):
                gender = 'F'
            if('birth' in full_str and '/' in full_str and date_str is None): # tries first page only
                ind1 = full_str.index('/')
                ind2 = full_str[ind1+1:].index('/')
                ind3 = full_str[ind2+1:].index('/')
                date_str = full_str[ind1-4:ind3-4]
                print('date_str : ',date_str)
    #print(patient_id, gender, date_str)
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
    df = df.drop_duplicates().set_index(['ID', 'time'])
    return df

pdf_paths = []
for (dirpath, dirnames, filenames) in walk('PDF'):
    pdf_paths.extend(filenames)
result_df = None
for pdf_path in pdf_paths:
    path = 'PDF/'+pdf_path
    if(result_df is None):
        result_df = extract_bp_records(path)
    else:
        result_df.append(extract_bp_records(path))
