import pandas as pd
import numpy as np

import requests
from tqdm import trange
import time
import re

url= f"https://news.seoul.go.kr/api/27/getCorona19Status/get_status_ajax.php?draw=1&start=0&length=100"
response = requests.get(url)
data_json = response.json()
records_total = data_json['recordsTotal']
if records_total%100 == 0:
    end_page = records_total//100
else:
    end_page = (records_total//100)+1
data = data_json['data']


def get_seoul_covid19(page_no):
    # 페이지가 100개 단위
    start_no = (page_no-1)*100
    url = f"https://news.seoul.go.kr/api/27/getCorona19Status/get_status_ajax.php?draw={page_no}&start={start_no}&length=100"
    response = requests.get(url)
    # print("page_no = ", page_no,"response = ",response)
    data_json = response.json()
    # print("data_json = ", data_json)
    return data_json

patient_list = []

for page_no in trange(1, end_page+1):
    one_page = get_seoul_covid19(page_no)
    # print("one_page = ",one_page)

    patient = pd.DataFrame(one_page['data'])
    # print("patient = ",patient)
    # print("="*100)

    patient_list.append(patient)

    # time.sleep(0.5)

df_all = pd.concat(patient_list)
# print('df_all = ',df_all)

df_all.columns = ["발생번호","환자번호","확진일","거주지","여행력","접촉력","퇴원현황"]
# print('df_all = ',df_all)


def extract_number(num_string):
    if type(num_string) == str:
        num_string = num_string.replace("corona19","")
        # num_string에서 [^0~9] (숫자가 아닌 데이터)를 검색해서 ""로 수정해서 리턴
        num = re.sub("[^0-9]","",num_string)
        num=int(num)
        return num
    else:
        return num_string


df_all["발생번호"] = df_all["발생번호"].map(extract_number)


def extract_hangeul(origin_text):
    subtract_text = re.sub("[^가-힣]", "", origin_text)
    return subtract_text


df_all["퇴원현황"] = df_all["퇴원현황"].map(extract_hangeul)
print('df_all = ',df_all)
df_all.to_csv("seoul_covid19.csv",index=False)