import re
import pandas as pd
from bs4 import BeautifulSoup
from requests_testadapter import Resp
import requests
import os
from processing_file import Processing

class LocalFileAdapter(requests.adapters.HTTPAdapter):
    def build_response_from_file(self, request):
        file_path = request.url[7:]
        with open(file_path, 'rb') as file:
            buff = bytearray(os.path.getsize(file_path))
            file.readinto(buff)
            resp = Resp(buff)
            r = self.build_response(request, resp)

            return r

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):

        return self.build_response_from_file(request)


requests_session = requests.session()
requests_session.mount('file://', LocalFileAdapter())

r=requests_session.get(r'file://'+r'C:\Users\parth.pandey\Desktop\Automation\Code\input\WCOs/630098168.html')  
# Path to HTML file

soup = BeautifulSoup(r.content, 'html.parser')
module=Processing(soup)  #Processing of html to dataframe
data_frame_from_scrape=module.make_df()

data_frame_from_scrape.to_excel(r'C:\Users\parth.pandey\Desktop\Automation\Code\output\Scraping_HTML/630098168_17-11-2021.xlsx')

