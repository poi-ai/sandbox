import lxml
import requests
from bs4 import BeautifulSoup

RACE_ID = '202204020206'
r = requests.get(f'https://db.netkeiba.com/race/{RACE_ID}')
soup = str(BeautifulSoup(r.content, 'lxml'))

filename = 'db'
f = open(f'{filename}_utf8.txt', 'w', encoding='UTF-8')
f.writelines(soup)
f = open(f'{filename}_sjis.txt', 'w', encoding='Shift-JIS', errors="ignore")
f.writelines(soup)
#print(soup)