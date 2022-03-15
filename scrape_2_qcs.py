import re
import pandas as pd
import os
import numpy as np

from scrape_2_qcs_processing import Processing

df=pd.read_excel(r'C:\Users\parth.pandey\Desktop\Automation\Code\input\Invoice/TNDSUMMARYMP02.xlsx',sheet_name='QCS ')   # for others
# df1=pd.read_excel(r'C:\Users\parth.pandey\Desktop\Automation\Code\input\Invoice/TNDSUMMARYMP01.xlsx',sheet_name='Invoice')  # for fsa_id
# Invoice

df2=pd.read_excel(r'C:\Users\parth.pandey\Desktop\Automation\Code\output\Scraping_HTML/630098168_17-11-2021.xlsx')
# PO Excel
module=Processing(df,df2)
final_data_frame=module.make_final_df()
final_data_frame.to_excel(r'C:\Users\parth.pandey\Desktop\Automation\Code\output\After_Invoice/630098168_17-11-2021.xlsx')