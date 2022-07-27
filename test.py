import requests
import lxml
from bs4 import BeautifulSoup

URL = 'https://db.netkeiba.com/race/201908040309/'

r = requests.get(URL)
soup = BeautifulSoup(r.content, 'lxml')

f = open('html.txt', 'w')
f.writelines(str(soup))
f.close()

