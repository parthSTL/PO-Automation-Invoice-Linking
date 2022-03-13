import re
import pandas as pd
import os
import numpy as np

class Processing:
    def __init__(self,df,df1,df2):
        self.df=df
        self.df1=df1
        self.df2=df2
    def make_final_df(self):
        df=self.df
        df1=self.df1
        df2=self.df2

        df2[['order_no','fsa_id','service_code']]=df2[['order_no','fsa_id','service_code']].astype(str)
        df2['quantity_consume']=0  # this to be done when 1st time adding work order
        for i in range(len(df2)):
            if len(df2.loc[i,'fsa_id'])<4:
                s=df2.loc[i,'fsa_id']
                s='0'+s
                df2.loc[i,'fsa_id']=s
        df2=df2.rename(columns={'Unnamed: 0':'index'})
        
        find_inv_no=False
        find_fsa=False
        column_list=list(df1.columns)
        for i in range(len(df1)):
            for col in column_list:
                if pd.isna(df1.loc[i,col]):
                    continue
                string=df1.loc[i,col]
                if type(string)!=str:
                    continue
                if not find_inv_no:
                    if 'Invoice No' in string:
                        find_inv_no=True
                        continue
                elif len(re.findall(r'\d+',string))>1:
                    l=re.findall(r'\d+',string)
                    if len(l[1])==4:
                        fsa=str(l[1])
                        df3=df2[df2['fsa_id']==fsa]
        #                 print(l[1])  # fsa_id
                        fsa=l[1]
                        find_fsa=True
            if find_fsa and find_inv_no:
                break
        # print(fsa)
        # column_name=[]
        column_list=list(df.columns)
        column_list
        find_order_no=False
        find_service=False
        find_qty=False
        find_milestone=False
        for i in range(len(df)):
            for col in column_list:
                
                if pd.isna(df.loc[i,col]):    #checking null
                    continue
                string=df.loc[i,col]
                if not find_order_no:
                    
                    l=re.findall(r'\d+',string)
                    if len(l)==2 and len(l[1])==9:
                        order=str(l[1])
                        df3=df3[df3['order_no']==order]
        #                 print(l[1])  # order_no
                        order=l[1]
                        find_order_no=True
                        continue
                elif not find_service:    # Find service
                    if type(string)==str:
                        if string=='Service Code':
        #                     print(string)
                            find_service=True
                            col_ser_id=col
                        continue
                elif not find_qty:
                    if type(string)==str:
                        if string=='Qty':
        #                     print(string)
                            find_qty=True
                            col_qty=col
                        continue
                elif col==col_ser_id:
                    if type(df.loc[i,col])!=int and type(df.loc[i,col])!=float:
                        break
                    else:
                        service_id=str(string)
                        df4=df3[df3['service_code']==service_id]
        #                 print(string)  # service_id
                elif col==col_qty:
                    if type(df.loc[i,col])!=int and type(df.loc[i,col])!=float:
                        break
                    else:
        #                 k=df2.query("fsa_id== {fsa} and service_code== {service_id} and order_no=={order}")
                        if len(df4)!=1:
                            continue
                        else:
                            ind=df4['index']
                            df2.loc[ind,'quantity_consume']+=int(string)
        #                 print(string)  #  quantity_consume
        return df2