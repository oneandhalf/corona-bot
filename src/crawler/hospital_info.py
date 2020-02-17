# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json

hosiptal = {}
# 전체 선별진료소
hosiptal_list = []
# 시군구 리스트
region_list = []

# retry get raw without timeout exception
def get_raw(url):
    while True:
        try:
            return requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        except:
            pass

# 검체채취가능 진료소
possible_hospital=[]

raw_hospital = get_raw("http://www.mohw.go.kr/react/popup_200128.html")
# print(raw_hospital.encoding)
# raw_hospital.encoding = None
html_hospital = BeautifulSoup(raw_hospital.content, 'html.parser', from_encoding='euc-kr')
hospitals = html_hospital.select("tbody.tb_center tr")

# 546
for h in hospitals:
    id = h.select_one("th").text
    city = h.select_one("td:nth-of-type(1)").text
    region = h.select_one("td:nth-of-type(2)").text
    selected = h.select_one("td:nth-of-type(3)").text.replace("	","").replace("(검체채취 가능)", "")
    number = h.select_one("td:nth-of-type(4)").text.replace(",","/")

    region_list.append(region)
    region_list = list(set(region_list))

    if "*" in selected:
        possible_hospital.append(selected)

    print(id,city,region,selected,number)
    hosiptal_list.append({"city":city, "region":region, "name":selected,"number":number})

hospital = {"all_hospital":hosiptal_list, "sampling_hospital":possible_hospital}
json_hospital = json.dumps(hospital, indent=4)
# print(json_hospital)
# print(type(json_hospital))
# print(possible_hospital)

print(region_list)
print(len(region_list))

with open('hospital.json', 'w', encoding="utf-8") as make_hosptial:
    json.dump(hospital, make_hosptial, ensure_ascii=False, indent="\t")