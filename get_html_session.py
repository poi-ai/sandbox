from requests_html import HTMLSession
from bs4 import BeautifulSoup

RACE_ID = '202248090103'

session = HTMLSession()
r = session.get(f'https://nar.netkeiba.com/race/result.html?race_id={RACE_ID}')
r.html.render(sleep=1, keep_page=True)
soup = str(BeautifulSoup(r.content, 'lxml'))

filename = 'result'
f = open(f'{filename}_utf8.txt', 'w', encoding='UTF-8')
f.writelines(soup)
f = open(f'{filename}_sjis.txt', 'w', encoding='Shift-JIS', errors="ignore")
f.writelines(soup)
#print(soup)