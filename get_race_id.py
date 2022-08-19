import time
import requests
import re
from bs4 import BeautifulSoup

def main(oldest_date = '20070728', latest_date = '20220731'):
    dates = get_dates(oldest_date, latest_date)

    for date in dates:
        race_ids = get_race_id(date)
        output(race_ids)

def get_race_id(date):
    '''指定した日に開催される競馬場のURLを取得する'''
    # HTMLタグ取得
    html = get_soup(f'https://db.netkeiba.com/race/list/{date}')

    # レース一覧記載枠の箇所を抽出
    race_frame = html.find('div', class_ = 'race_kaisai_info')

    # レースへのリンクをすべて取得
    races = re.finditer(r'/race/(\d+)/', str(race_frame))

    # リストに変換して返す
    return [m.groups()[0] for m in races]

def output(id_list):
    f = open(f'race_id.txt', 'a')
    for id in id_list:
        f.write(str(id))
        f.write('\n')
    f.close()

def get_dates(oldest_date, latest_date):
    '''取得対象日の取得を行う'''

    # 対象日格納用
    target_dates = []

    # 対象最新日の月から順に検索していく
    month = latest_date[:6]

    # 対象最古日より前の月になるまでループ
    while month >= oldest_date[:6]:

        # HTMLタグ取得
        html = get_soup(f'https://db.netkeiba.com/race/list/{month}01')

        # 開催カレンダーの取得
        calendar = html.find('table')

        # 開催日のリンクがある日付を抽出
        dates = re.finditer(r'/race/list/(\d+)/', str(calendar))

        # 降順にするためリストに変換
        date_list = [m.groups()[0] for m in dates]
        date_list.reverse()

        # 期間内だったらリストに追加
        for date in date_list:
            if oldest_date <= date <= latest_date:
                target_dates.append(date)

        # 月をひとつ前に戻す
        if month[4:] == '01':
            month = str(int(month) - 89)
        else:
            month = str(int(month) - 1)

    return target_dates

def get_soup(URL):
    '''指定したURLからHTMLタグをスクレイピングするメソッド。
       間隔をあけずに高頻度でアクセスしてしまうのを防ぐために
       必ずこのメソッドを経由してアクセスを行う

    Args:
        URL(str):抽出対象のURL

    Retuens:
        soup(bs4.BeautifulSoup):抽出したHTMLタグ

    '''
    time.sleep(2)
    r = requests.get(URL)
    return BeautifulSoup(r.content, 'lxml')

if __name__ == '__main__':
    #output(['aaa','iii'])
    main('20220729', '20220731')