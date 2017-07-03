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
            #p
            #print(full_str)
            #p
            if('patient id' in full_str and 'start' in full_str and patient_id is None):
                ind1 = full_str.index('id')
                #while(full_str[ind1].isalpha() == False): #never entered (?)
                    #ind1 += 1
                    #p
                    #print('ind1 : ',ind1,' ',full_str[ind1])
                    #p
                ind2 = full_str.index('start')
                #p
                #print('ind2 : ',ind2,' ',full_str[ind2])
                #print('ind2-ind1 : ',ind2-ind1,' ',full_str[ind1+2:ind2])
                #print('isalpha? : ',full_str[ind1+2:ind2].isalpha())
                #p
                if(ind2-ind1 == 16): # look for perfect line
                    #p
                    #print('ind2-ind1 = 16')
                    #p
                    #if(' ' not in full_str[ind1+2:ind2] and ':' not in full_str[ind1+2:ind2]):
                    patient_id = full_str[ind1+4:ind2].upper()
                    #p
                    #print('patient_id :',full_str[ind1+4:ind2],' !')
                    #p
            if('female' in full_str):
                gender = 'F'
            if('date of birth: ' in full_str and '/' in full_str and date_str is None): 
                ind1 = full_str.index('/')# in all cases, '/' apears after DOB
                # print('##################################################')
                # print('##################################################')
                
                # print(full_str)
                # print('ind1 : ',ind1)
                # print('@lnstart>ind1 : ',full_str[:ind1])
                # print('ind1>@endln : ',full_str[ind1:])
                
                indx2 = full_str[ind1+1:].index('/')
                # print('indx2 : ',indx2)
                # print('@lnstart>(ind1+1+indx2) : ',full_str[:ind1+1+indx2])
                # print('(ind1+1+indx2)>@endln : ',full_str[ind1+1+indx2:])
                
                # indy2 = full_str[ind1+2:].index('/')
                # print('indy2 : ',indy2)
                # print('@lnstart>(ind1+2+indy2) : ',full_str[:ind1+2+indy2])
                # print('(ind1+2+indy2)>@endln : ',full_str[ind1+2+indy2:])
                # 
                # indz2 = full_str[ind1+3:].index('/')
                # print('indz2 : ',indz2)
                # print('@lnstart>(ind1+3+indz2) : ',full_str[:ind1+3+indz2])
                # print('(ind1+3+indz2)>@endln : ',full_str[ind1+3+indz2:])
                # 
                # print('>>> (ind1-4:ind1+/+indx2+/+2) ::',full_str[ind1-4:ind1+1+indx2+1+2])
                
                if not(any(c.isalpha() for c in full_str[ind1-4:ind1+1+indx2+1+2])):
                    #check for alphabetic letters
                    date_str = full_str[ind1-4:ind1+1+indx2+1+2]
                
                # print('##################################################')
                # print('##################################################')
                
                # ind2 = full_str[ind1+1:].index('/')
                # print('ind2 : ',ind2,' ind1>ind2 : ',full_str[ind1:ind2])
                # ind3 = full_str[ind2+1:].index('/')
                # print('ind3 : ',ind3,' ind2>ind3 : ',full_str[ind2:ind3])
                #     date_str = full_str[ind1-4:ind1+4]
                #     print('ind1-4:ind1+4 :: ',full_str[ind1-4:ind1+4])
                # p
                #     print('date_str : ',date_str,' !')
                # p
    # print(patient_id, gender, date_str)
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
    #print('@afterExtract : ',len(df.index))
    return df

pdf_paths = []
for (dirpath, dirnames, filenames) in walk('PDF'):
    pdf_paths.extend(filenames)
    print(filenames)
result_df = None
for pdf_path in pdf_paths:
    path = 'PDF/'+pdf_path
    if(result_df is None):
        #print('@start')
        #print('@firstPDF : ',path)
        result_df = extract_bp_records(path)
        #print('@afterAppend : ',len(result_df.index))
    else:
        #print('@nextPDF : ', path)
        result_df = result_df.append(extract_bp_records(path))
        #print('@afterAppend : ',len(result_df.index))
#print('@end : ',len(result_df.index))
timestamp = time.strftime('_%Y%m%d_%H%M%S')
result_df.to_csv('BPRecords'+timestamp+'.csv')
print('Done extracting from subdirectory "PDF" !')
print('Generated new csv file "BPRecords'+timestamp+'.csv" !')