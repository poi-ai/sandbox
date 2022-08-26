import pandas as pd
import re

df = pd.read_html('https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETsiR001Control&_DataStoreID=DSWPLETsiR001Control&_PageID=WPLETsiR001Idtl10&_ActionID=getInfoOfCurrentMarket&s_rkbn=&i_stock_sec=&i_dom_flg=1&i_exchange_code=&i_output_type=&stock_sec_code_mul=9318&exchange_code=PTS&ref_from=1&ref_to=20&s_btype=&wstm4130_sort_id=&wstm4130_sort_kbn=&qr_keyword=&qr_suggest=&qr_sort=')

data = []
for i in range(4):
    m = re.search('(.+)\((.+)\)',df[0]['取引所株価（東証）  取引所・PTS株価比較.1'][i])
    data.append(re.sub(r'[↑↓ ]', '', m.groups()[0]).replace('\xa0',''))
    data.append(re.sub(r'[↑↓ ]', '', m.groups()[1]).replace('\xa0',''))
print(data)