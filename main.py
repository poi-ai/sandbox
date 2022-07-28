import lxml
import pandas as pd
from bs4 import BeautifulSoup

# 保存済みのHTML(ローカル内で完結するように疑似取得)
f = open('html.txt', 'r')
HTML = f.read()
f.close()


soup = BeautifulSoup(HTML, 'lxml')
table = pd.read_html(HTML) #table[0]...結果テーブル [4]...コーナー順位 [5]...ラップタイム

race_info = []

print(table[8])
