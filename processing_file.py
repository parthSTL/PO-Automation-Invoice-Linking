import re
import pandas as pd
from bs4 import BeautifulSoup
from requests_testadapter import Resp
import requests
import os

class Processing:
    def __init__(self,soup):
        self.soup=soup
    
    def make_df(self):

        lst=[]
        row=0
        col_index=0
        column_name=['order_type','order_no','revision_no','date','amendment of total price','previous total order price',
                     'revised/total order price','fsa_id','fsa_name','service_code','service_heading','quantity','UOM',
                     'service_rate','total_value','service_description','quantity_consume']
        df=pd.DataFrame(columns=column_name)
        col_index=0
        row+=1
        
        dv=self.soup.find_all('div')
        page_no_dv_index=0
        dvv= dv[page_no_dv_index].find_all('div')
        # print(dvv)
        flag=0  
        remember_inr=0 # for total order value
        fill_for_first_time=0 # to repeat orderno, order_type, etc every row
        revision_no=0 # 0 for nottaken no and 1 for taken
        for j in range(1,len(dvv)):
            # print(j)
            # print(dvv)
            string=dvv[j].get_text()
            # print(string)
            if flag==0:
                comp_str=string.replace(' ','')
                if comp_str.lower() == "workorder" or comp_str.lower() == "workchangeorder" or comp_str.lower() == "contractorder" or comp_str.lower() == "contractchangeorder":
                    type_order=string                    # Type Order Extract
                    flag+=1
                    df.loc[row,column_name[col_index]]=type_order
                    col_index+=1 # proceeding to next column
                    if comp_str.lower()=="workchangeorder" or comp_str.lower() == "contractchangeorder":
                        revision_no=1
                    # print(df)
                    continue
            
            # print(1)  
            if flag==1:
                check_slash=re.findall("[/]",string)
                if check_slash:
                  # print(string)
                    flag=2
                    order_no= re.split('/',string)[1]       # Order No extract
                    df.loc[row,column_name[col_index]]=order_no
                    col_index+=1
                    lst.append(order_no)
                    continue
            if revision_no==1 and flag==2:
                col_index=2
                extract_rev_no=re.findall(r'\d+',string)
                if len(extract_rev_no)>0:
                    # print(1)
                    rev_no=extract_rev_no[0]
                    df.loc[row,column_name[col_index]]=rev_no
                    col_index+=1
                    revision_no=0
                    continue
            if flag==2:
                col_index=3
                extract_date=re.findall(r'\d+',string)
                if len(extract_date)==3:
                    date=extract_date[0]+'.'+extract_date[1]+'.'+extract_date[2]
                    flag=3
                    df.loc[row,column_name[col_index]]=date
                    col_index+=1
                    continue
            if flag==3:
                if comp_str.lower()=='workorder':
                    col_index=5
                    if string=='TOTAL ORDER VALUE':
                        remember_inr=1
                    if remember_inr==1:
                        extract_value=re.findall(r'\d+',string)
                        if len(extract_value)>0:
                            df.loc[row,column_name[col_index]]=string
                            col_index+=1
                            flag+=1
                if comp_str.lower()=='contractorder':
                    col_index=5
                    if 'TOTAL ESTIMATED CONTRACT' in string:
                        remember_inr=1
                    if remember_inr==1:
                        extract_value=re.findall(r'\d+',string)
                        if len(extract_value)>0:
                            df.loc[row,column_name[col_index]]=string
                            col_index+=1
                            flag+=1
                if comp_str.lower()=='workchangeorder':
                    if 'Amendment' in string:
                        remember_inr=1
                    if remember_inr==1:
                        extract_value=re.findall(r'\d+',string)
                        if len(extract_value)>0:
                            df.loc[row,column_name[col_index]]=string
                            col_index+=1
                            remember_inr+=1
                            continue
                    if remember_inr==2:
                        extract_value=re.findall(r'\d+',string)
                        if len(extract_value)>0:
                            df.loc[row,column_name[col_index]]=string
                            col_index+=1
                            remember_inr+=1
                            continue
                    if remember_inr==3:
                        extract_value=re.findall(r'\d+',string)
                        if len(extract_value)>0:
                            df.loc[row,column_name[col_index]]=string
                            col_index+=1
                            remember_inr+=1
                            flag+=1
                if comp_str.lower()=='contractchangeorder':
                    if 'Amendment' in string:
                        remember_inr=1
                    if remember_inr==1:
                        extract_value=re.findall(r'\d+',string)
                        if len(extract_value)>0:
                            df.loc[row,column_name[col_index]]=string
                            col_index+=1
                            remember_inr+=1
                            continue
                    if remember_inr==2:
                        extract_value=re.findall(r'\d+',string)
                        if len(extract_value)>0:
                            df.loc[row,column_name[col_index]]=string
                            col_index+=1
                            remember_inr+=1
                            continue
                    if remember_inr==3:
                        extract_value=re.findall(r'\d+',string)
                        if len(extract_value)>0:
                            df.loc[row,column_name[col_index]]=string
                            col_index+=1
                            remember_inr+=1
                            flag+=1
        
        def check_for_service_code(dvv,j,string):
            sstring=dvv[j]['style']
            coord_list=re.findall(r'\d+',sstring)
            if len(coord_list)<2:
                return False
            else:
                if coord_list[0]=='62' and coord_list[1]=='40':
                    if len(re.findall(r'\d',string))==len(string):  # stringcodeno is only present alone
                        return True
                    
        def check_for_code_no(dvv,j,string):
            sstring=dvv[j]['style']
            coord_list=re.findall(r'\d+',sstring)
            if len(coord_list)<2:
                return False
            else:
                if coord_list[0]=='48' and coord_list[1]=='00':
                    if len(re.findall(r'\d',string))==len(string):  # stringcodeno is only present alone
                        return True
        
        get_item_code=False
        get_service_code=False
        get_fsa=False
        get_service_id=False
        get_service_name=False
        get_quant=False
        get_unit_rate=False
        get_total_value=False
        get_ser_desc=False
        new_page=False
        greater_hun=False
        summ=0
        # check_for_item_code=0  # If item code comes then it will become 1
        # check_for_fsa_id=0 #
        init_row=1 # Order no is in first row
        init_fsa_row=1
        df=df.reset_index(drop=True)  # This I am doing to avoid any corner case
        if flag>3:
            while(True):
                page_no_dv_index=1+len(dvv)+page_no_dv_index  # to find a particular div have start page
                # print(page_no_dv_index)
                new_page=True
                if page_no_dv_index>=len(dv):  # Avoid any corner case
                    break
                dvv=dv[page_no_dv_index].find_all('div') # Finding div in a page
                if comp_str.lower()=='workchangeorder' or comp_str.lower()=='workorder':  
                    for j in range(1,len(dvv)): # Workking on evey div
                        string=dvv[j].get_text()
        #                 summ+=1
                        if new_page:
                            compress_string=string.replace(' ','')
                            if compress_string.lower()=='amount(inr)':
                                new_page=False
                                continue
                        else:
                            if check_for_code_no(dvv,j,string):
                                if dvv[j+1].get_text()=='AU':
                                    continue
                                else:
                                    get_fsa=False
                                    continue
        #                     summ+=1
        #                     if get_item_code:         # Item Code
        #                         summ+=1
                            if not get_fsa:
                                id_no_lst=re.findall(r'\d+',string) 
                                if len(id_no_lst)<1:   # For corner case
                                    get_item_code=False
                                    continue
                                id_no_str=re.findall(r'\d+',string)[0]
                                if len(id_no_str)!=4:
                                    get_item_code=False
                                    continue
                                init_fsa_row=1
                                if init_row==1:
                                    row=len(df)-1
                                    df.loc[row,column_name[7]]=id_no_str    # Fsa id
                                    df.loc[row,column_name[8]]=string
                                    init_row=0
                                else:
                                    row=len(df)-1
                                    df2=df.loc[row,]
                                    df=df.append(df2,ignore_index=True)
                                    row=len(df)-1
                                    df.loc[row,column_name[7]]=id_no_str    # Fsa id
                                    df.loc[row,column_name[8]]=string
                                get_fsa=True
                                continue
                            else:
        #                            print(string)
        #                            summ+=1
                                if get_service_code:
                                    if not get_service_id:
                                        if not greater_hun:
                                            if init_fsa_row==1:
                                                row=len(df)-1
                                                df.loc[row,column_name[9]]=string
                                                init_fsa_row=0
                                                get_service_id=True
                                            else:
                                                row=len(df)-1
                                                df2=df.loc[row,]
                                                df=df.append(df2,ignore_index=True)
                                                row=len(df)-1
                                                df.loc[row,column_name[9]]=string
                                                get_service_id=True
                                                
                                        else:
                                            service_id=re.findall(r'\d+',string)[0]
                                            row=len(df)-1
                                            df2=df.loc[row,]
                                            df=df.append(df2,ignore_index=True)
                                            row=len(df)-1
                                            df.loc[row,column_name[9]]=service_id
                                            get_service_id=True
                                            df.loc[row,column_name[10]]=string[7:]
                                            get_service_name=True
                                        continue
                                        
                                    elif not get_service_name:
        #                                    print(string)
                                        row=len(df)-1
                                        df.loc[row,column_name[10]]=string
                                        get_service_name=True
                                        continue
                                    
                                    elif not get_quant:
                                        row=len(df)-1
                                        df.loc[row,column_name[11]]=re.findall(r'\d+',string)[0]
                                        get_quant =True
                                        s=re.findall(r'\d',string)
                                        if len(s)==len(string):
                                            df.loc[row,column_name[12]]=dvv[j+1].get_text()
                                        else: df.loc[row,column_name[12]]=string
                                        continue
                                        
                                    elif not get_unit_rate:
                                        if len(re.findall(r'\d+',string))>1:
                                            row=len(df)-1
                                            df.loc[row,column_name[13]]=string
                                            get_unit_rate=True
                                        continue
                                    elif not get_total_value:
                                        row=len(df)-1
                                        df.loc[row,column_name[14]]=string
                                        get_total_value=True
                                        continue
                                    elif not get_ser_desc:
                                        row=len(df)-1
                                        df.loc[row,column_name[15]]=string
                                        get_service_code=False
                                        get_service_id=False
                                        get_service_name=False
                                        get_quant=False
                                        get_unit_rate=False
                                        get_total_value=False
                                        get_ser_desc=False
                                        get_service_code=check_for_service_code(dvv,j,string)
                                        if get_service_code:
        #                                    print(string)
                                            service_code=int(string)
                                            if service_code>=100:
                                                greater_hun=True
                                            else:
                                                greater_hun=False
        #                                        print(service_code)

                                        continue
                                    
                                    pass
                                
                                
                                
                                else:
                                    get_service_code=check_for_service_code(dvv,j,string)
                                    if get_service_code:
        #                                    print(string)
                                        service_code=int(string)
                                        if service_code>=100:
                                            greater_hun=True
                                        else:
                                            greater_hun=False
        #                                    print(service_code)
                                    pass
                                continue
                                
                            
                            get_item_code=False
                            get_fsa=False
                            continue
                                    
        #                     else:
        #                         get_item_code=check_for_code_no(dvv,j,string)
        
        
        df['total_value'] = df['total_value'].apply(lambda x: x.replace(',', ''))
        df['service_rate'] = df['service_rate'].apply(lambda x: x.replace(',', ''))
        df['total_value'] = pd.to_numeric(df['total_value'], errors='coerce')
        df['service_rate'] = pd.to_numeric(df['service_rate'], errors='coerce')
        df['quantity']=df['total_value']/df['service_rate']
        return df