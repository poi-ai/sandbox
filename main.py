import lxml
import requests
import time
import pandas as pd
import re
from bs4 import BeautifulSoup

def url(type):
    # 馬柱
    if type == 'UMABASHIRA_URL':
        return f'https://race.netkeiba.com/race/shutuba_past.html?race_id={RACE_ID}'
    # リアルタイム レース結果
    elif type == 'RACE_RESULT_URL':
        return f'https://race.netkeiba.com/race/result.html?race_id={RACE_ID}'
    # DB レース結果
    elif type == 'DB_RESULT_URL':
        return f'https://db.netkeiba.com/race/{RACE_ID}'

    return False

    '''
    MEMO
    * レース前に実際に取れるのは馬柱のみなので、レース情報などは馬柱から取得する
    * 騎手減量がリアルタイム レース結果からしか取得できないので要検討
    '''
def main():
    global RACE_ID
    # 共通(PKになる)レースデータ
    common_info = CommonInfo()

    # TODO 開催日、実装時はインスタンス変数
    common_info.race_date = KAISAI_DATE
    common_info.race_no = RACE_ID[-2:]
    common_info.baba_code = RACE_ID[4:6]

    if not LOCAL and GET_FILE:
        id_list = get_race_id()

        for id in id_list:
            # レースIDをセット
            RACE_ID = str(id).replace('\n', '')

            # レース結果(DB)からデータ取得
            # horse_dict = get_result()

            # 馬柱からデータ取得
            get_umabashira()
    else:
        # レース結果(DB)からデータ取得
        horse_dict = get_result()

        # 馬柱からデータ取得
        get_umabashira()

def get_race_id():
    f = open('race_id.txt', 'r')
    id_list = [id for id in f]
    f.close()
    return id_list

def get_umabashira():
    # 馬柱からデータを取得
    if LOCAL:
        f = open('umabashira_sjis.txt', 'r')
        html = f.read()
        f.close()
        soup = BeautifulSoup(html, 'lxml')
    else:
        soup = Soup(url('UMABASHIRA_URL'))

    # レース情報格納用データクラス
    race_info = RaceInfo()

    try:
        # コース情報や状態を抽出
        race_data_01 = soup.find('div', class_ = 'RaceData01')
        race_data_list = rm(race_data_01.text).split('/')

        output(race_data_list, 'check1')
    except:
        output(str(RACE_ID) + ' 1', 'error')

    '''
    race_info.race_time = race_data_list[0].replace('発走', '')

    course = re.search('([芝|ダ])(\d+)m\((.*)\)', race_data_list[1])
    race_info.baba = course.groups()[0]
    race_info.distance = course.groups()[1]
    race_info.around = course.groups()[2]

    race_info.weather = race_data_list[2].replace('天候:', '')
    race_info.baba_condition = race_data_list[3].replace('馬場:', '')
    '''

    try:
    # 出走条件等の抽出
        race_data_02 = soup.find('div', class_ = 'RaceData02')
        race_data_list = race_data_02.text.split('\n')

        output(race_data_list, 'check2')
    except:
        output(str(RACE_ID) + ' 2', 'error')

    '''
    race_info.hold_no = race_data_list[1].replace('回', '')
    race_info.hold_date = race_data_list[3].replace('日目', '')
    race_info.require_age = half(race_data_list[4]).replace('サラ系', '')
    race_info.grade = half(race_data_list[5])

    for data in race_data_list:
        horse_num = re.search('(\d+)頭', data)
        if horse_num != None:
            race_info.horse_num = horse_num.groups()[0]
            continue

        prize = re.search('本賞金:(\d+),(\d+),(\d+),(\d+),(\d+)万円', data)
        if prize != None:
            race_info.first_prize = prize.groups()[0]
            race_info.second_prize = prize.groups()[1]
            race_info.third_prize = prize.groups()[2]
            race_info.fourth_prize = prize.groups()[3]
            race_info.fifth_prize = prize.groups()[4]
            continue

        # TODO 各出走条件によってフラグを立てたり
        pass
    '''

    try:
        #fc = soup.find('div', class_ = 'fc')
        fc = soup.select('div[class="fc"]')

        for fcc in fc:
            horseinfo = str(fcc).replace('\n', '')
            output(horseinfo, 'check3')
    except:
        output(str(RACE_ID) + ' 3', 'error')

def get_result():
    # レース結果(HTML全体)
    if LOCAL:
        f = open('db_sjis.txt', 'r')
        html = f.read()
        f.close()
        soup = BeautifulSoup(html, 'lxml')
    else:
        soup = Soup(url('DB_RESULT_URL'))

    # レース結果(結果テーブル)
    tables = Table(soup)
    table = tables[0]

    # 箱用意{馬番:[HorseInfo, HorseResult]}
    horse_dict = {i: [HorseInfo(), HorseResult()] for i in table['馬番']}

    # 1着馬の馬番
    winner_horse_no = 0

    # 行ごとに切り出し
    # TODO 除外・取消馬の処理
    for i, index in enumerate(table.index):
        row = table.loc[index]

        # キーになる馬番を先に取得
        no = row['馬番']

        # 馬の情報の各項目を設定
        horse_dict[no][0].frame_no = row['枠番']
        horse_dict[no][0].horse_no = row['馬番']
        horse_dict[no][0].horse_name = row['馬名']
        # 頭1文字が性別、2文字目以降が年齢
        horse_dict[no][0].age = row['性齢'][0]
        horse_dict[no][0].gender = row['性齢'][1:]
        horse_dict[no][0].load = row['斤量']
        horse_dict[no][0].jockey = row['騎手']
        horse_dict[no][0].win_odds = row['単勝']
        horse_dict[no][0].popular = row['人気']
        # 括弧内が増減、外が馬体重
        weight = re.search('(\d+)\((.+)\)', row['馬体重'])
        # 馬体重不明チェック(新馬・前走計不時は増減は0と表記)
        if weight == None:
            horse_dict[no][0].weight = -1
            horse_dict[no][0].weight_change = -999
        else:
            horse_dict[no][0].weight = weight.groups()[0]
            horse_dict[no][0].weight_change = weight.groups()[1].replace('±', '').replace('+', '')
        # 調教師チェック[東]美浦、[西]栗東
        trainer = re.search('\[(.+)\] (.+)', row['調教師'])
        if trainer == None:
            horse_dict[no][0].trainer = '-'
            horse_dict[no][0].trainer_belong = '-'
        else:
            horse_dict[no][0].trainer = trainer.groups()[0]
            horse_dict[no][0].trainer_belong = trainer.groups()[1]
        horse_dict[no][0].horse_no = row['馬番']
        horse_dict[no][0].owner = row['馬主']

        # レース結果の各項目を設定
        horse_dict[no][1].horse_no = row['馬番']
        horse_dict[no][1].rank = row['着順']
        horse_dict[no][1].goal_time = row['タイム']
        # 着差、1着馬は2着との差をマイナスに
        if i == 0:
            winner_horse_no = no
        elif i == 1:
            horse_dict[winner_horse_no][1].diff_distance = '-' + str(row['着差'])
            horse_dict[no][1].diff_distance = row['着差']
        else:
            horse_dict[no][1].diff_distance = row['着差']
        horse_dict[no][1].pass_rank = row['通過']
        horse_dict[no][1].nobiri = row['上り']
        horse_dict[no][1].price = row['賞金(万円)']

    return horse_dict

def Soup(URL):
    # URL = 'https://db.netkeiba.com/race/202204020206/'
    # 馬柱 https://race.netkeiba.com/race/shutuba.html?race_id=202204020206
    r = requests.get(URL)
    time.sleep(3)
    return BeautifulSoup(r.content, 'lxml')

def Table(soup):
    #table[0]...結果テーブル｜[4]...コーナー順位｜[5]...ラップタイム

    # read_htmlで抜けなくなる余分なタグを除去
    HTML = str(soup).replace('<diary_snap_cut>', '').replace('</diary_snap_cut>', '')
    return pd.read_html(HTML)

def output(word, filename):
    f = open(f'{filename}.txt', 'a', encoding='utf-8')
    if type(word) is list:
        f.write(str(word).replace('[', '').replace(']', '').replace("'", ''))
    else:
        f.write(str(word))
    f.write('\n')
    f.close()

def rm(str):
    '''改行・空白を除去'''
    return str.replace('\n', '').replace(' ', '')

def half(str):
    '''全角を半角へ変換'''
    return str.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

class CommonInfo():
    '''レースを一意に定めるデータのデータクラス'''
    def __init__(self):
        self.__race_date = '' # レース開催日
        self.__race_no = '' # レース番号
        self.__baba_code = '' # 競馬場コード

    # getter
    @property
    def race_date(self): return self.__race_date
    @property
    def race_no(self): return self.__race_no
    @property
    def baba_code(self): return self.__baba_code

    # setter
    @race_date.setter
    def race_date(self, race_date): self.__race_date = race_date
    @race_no.setter
    def race_no(self, race_no): self.__race_no = race_no
    @baba_code.setter
    def baba_code(self, baba_code): self.__baba_code = baba_code

class RaceInfo():
    '''発走前のレースに関するデータのデータクラス'''
    def __init__(self):
        self.__race_name = '' # レース名
        self.__baba = '' # 馬場(芝/ダート)o
        self.__weather = '' # 天候o
        self.__baba_condition = '' # 馬場状態o
        self.__distance = '' # 距離o
        self.__around = '' # 回り(右/左)o
        self.__in_out = '' # 回り(内/外)
        self.__race_time = '' # 発走時刻o
        self.__hold_no = '' # 開催回o
        self.__hold_date = '' # 開催日o
        self.__grade = '' # 格・グレードo
        self.__require_age = '' # 出走条件(年齢)o
        self.__require_gender = '' # 出走条件(性別)
        self.__require_country = '' # 出走条件(国内/国際/混合)
        self.__require_local = '' # 出走条件(特別指定/指定/他)
        self.__load_kind = '' # 斤量条件(定量/賞金別定/重賞別定/ハンデ)
        self.__first_prize = '' # 1着賞金o
        self.__second_prize = '' # 2着賞金o
        self.__third_prize = '' # 3着賞金o
        self.__fourth_prize = '' # 4着賞金o
        self.__fifth_prize = '' # 5着賞金o
        self.__horse_num = '' # 出走頭数o

    # getter
    @property
    def race_name(self): return self.__race_name
    @property
    def baba(self): return self.__baba
    @property
    def weather(self): return self.__weather
    @property
    def baba_condition(self): return self.__baba_condition
    @property
    def distance(self): return self.__distance
    @property
    def around(self): return self.__around
    @property
    def in_out(self): return self.__in_out
    @property
    def race_time(self): return self.__race_time
    @property
    def hold_no(self): return self.__hold_no
    @property
    def hold_date(self): return self.__hold_date
    @property
    def grade(self): return self.__grade
    @property
    def require_age(self): return self.__require_age
    @property
    def require_gender(self): return self.__require_gender
    @property
    def require_country(self): return self.__require_country
    @property
    def require_local(self): return self.__require_local
    @property
    def load_kind(self): return self.__load_kind
    @property
    def first_prize(self): return self.__first_prize
    @property
    def second_prize(self): return self.__second_prize
    @property
    def third_prize(self): return self.__third_prize
    @property
    def fourth_prize(self): return self.__fourth_prize
    @property
    def fifth_prize(self): return self.__fifth_prize
    @property
    def horse_num(self): return self.__horse_num

    # setter
    @race_name.setter
    def race_name(self, race_name): self.__race_name = race_name
    @baba.setter
    def baba(self, baba): self.__baba = baba
    @weather.setter
    def weather(self, weather): self.__weather = weather
    @baba_condition.setter
    def baba_condition(self, baba_condition): self.__baba_condition = baba_condition
    @distance.setter
    def distance(self, distance): self.__distance = distance
    @around.setter
    def around(self, around): self.__around = around
    @in_out.setter
    def in_out(self, in_out): self.__in_out = in_out
    @race_time.setter
    def race_time(self, race_time): self.__race_time = race_time
    @hold_no.setter
    def hold_no(self, hold_no): self.__hold_no = hold_no
    @hold_date.setter
    def hold_date(self, hold_date): self.__hold_date = hold_date
    @grade.setter
    def grade(self, grade): self.__grade = grade
    @require_age.setter
    def require_age(self, require_age): self.__require_age = require_age
    @require_gender.setter
    def require_gender(self, require_gender): self.__require_gender = require_gender
    @require_country.setter
    def require_country(self, require_country): self.__require_country = require_country
    @require_local.setter
    def require_local(self, require_local): self.__require_local = require_local
    @load_kind.setter
    def load_kind(self, load_kind): self.__load_kind = load_kind
    @first_prize.setter
    def first_prize(self, first_prize): self.__first_prize = first_prize
    @second_prize.setter
    def second_prize(self, second_prize): self.__second_prize = second_prize
    @third_prize.setter
    def third_prize(self, third_prize): self.__third_prize = third_prize
    @fourth_prize.setter
    def fourth_prize(self, fourth_prize): self.__fourth_prize = fourth_prize
    @fifth_prize.setter
    def fifth_prize(self, fifth_prize): self.__fifth_prize = fifth_prize
    @horse_num.setter
    def horse_num(self, horse_num): self.__horse_num = horse_num

class RaceResult():
    '''レース全体のレース結果を保持するデータクラス'''
    def __init__(self):
        self.__corner_rank = [] # コーナー通過順(馬番)
        self.__pace = [] # 先頭馬のペース(秒)

    # getter
    @property
    def corner_rank(self): return self.__corner_rank
    @property
    def pace(self): return self.__pace

    # setter
    @corner_rank.setter
    def corner_rank(self, corner_rank): self.__corner_rank = corner_rank
    @pace.setter
    def pace(self, pace): self.__pace = pace

class HorseInfo():
    '''各馬の発走前のデータを保持するデータクラス'''
    def __init__(self):
        self.__frame_no = '' # 枠番o
        self.__horse_no = '' # 馬番(複合PK)o
        self.__horse_name = '' # 馬名o
        self.__age = '' # 馬齢o
        self.__gender = '' # 性別o
        self.__load = '' # 斤量o
        self.__jockey = '' # 騎手名o
        self.__jockey_handi = '' # 騎手減量
        self.__win_odds = '' # 単勝オッズo
        self.__popular = '' # 人気o
        self.__weight = '' # 馬体重o
        self.__weight_change = '' # 馬体重増減o
        self.__trainer = '' # 調教師名o
        self.__trainer_belong = '' # 調教師所属(美浦/栗東)o
        self.__owner = '' # 馬主名o

        # 以下は馬柱から
        self.__blank = '' # レース間隔
        self.__father = '' # 父名
        self.__monther = '' # 母名
        self.__grandfather = '' # 母父名
        self.__running_type = '' # 脚質(←netkeibaの主観データ？)
        self.__country = '' # 所属(国内/国外)
        self.__belong = '' # 所属(中央/地方)
        self.__blinker = '' # ブリンカー(有/無)
        self.__haircolor = '' # 毛色

    # getter
    @property
    def frame_no(self): return self.__frame_no
    @property
    def horse_no(self): return self.__horse_no
    @property
    def horse_name(self): return self.__horse_name
    @property
    def age(self): return self.__age
    @property
    def gender(self): return self.__gender
    @property
    def load(self): return self.__load
    @property
    def jockey(self): return self.__jockey
    @property
    def jockey_handi(self): return self.__jockey_handi
    @property
    def win_odds(self): return self.__win_odds
    @property
    def popular(self): return self.__popular
    @property
    def weight(self): return self.__weight
    @property
    def weight_change(self): return self.__weight_change
    @property
    def trainer(self): return self.__trainer
    @property
    def trainer_belong(self): return self.__trainer_belong
    @property
    def owner(self): return self.__owner
    @property
    def blank(self): return self.__blank
    @property
    def father(self): return self.__father
    @property
    def monther(self): return self.__monther
    @property
    def grandfather(self): return self.__grandfather
    @property
    def running_type(self): return self.__running_type
    @property
    def country(self): return self.__country
    @property
    def belong(self): return self.__belong
    @property
    def blinker(self): return self.__blinker
    @property
    def haircolor(self): return self.__haircolor

    # setter
    @frame_no.setter
    def frame_no(self, frame_no): self.__frame_no = frame_no
    @horse_no.setter
    def horse_no(self, horse_no): self.__horse_no = horse_no
    @horse_name.setter
    def horse_name(self, horse_name): self.__horse_name = horse_name
    @age.setter
    def age(self, age): self.__age = age
    @gender.setter
    def gender(self, gender): self.__gender = gender
    @load.setter
    def load(self, load): self.__load = load
    @jockey.setter
    def jockey(self, jockey): self.__jockey = jockey
    @jockey_handi.setter
    def jockey_handi(self, jockey_handi): self.__jockey_handi = jockey_handi
    @win_odds.setter
    def win_odds(self, win_odds): self.__win_odds = win_odds
    @popular.setter
    def popular(self, popular): self.__popular = popular
    @weight.setter
    def weight(self, weight): self.__weight = weight
    @weight_change.setter
    def weight_change(self, weight_change): self.__weight_change = weight_change
    @trainer.setter
    def trainer(self, trainer): self.__trainer = trainer
    @trainer_belong.setter
    def trainer_belong(self, trainer_belong): self.__trainer_belong = trainer_belong
    @owner.setter
    def owner(self, owner): self.__owner = owner
    @blank.setter
    def blank(self, blank): self.__blank = blank
    @father.setter
    def father(self, father): self.__father = father
    @monther.setter
    def monther(self, monther): self.__monther = monther
    @grandfather.setter
    def grandfather(self, grandfather): self.__grandfather = grandfather
    @running_type.setter
    def running_type(self, running_type): self.__running_type = running_type
    @country.setter
    def country(self, country): self.__country = country
    @belong.setter
    def belong(self, belong): self.__belong = belong
    @blinker.setter
    def blinker(self, blinker): self.__blinker = blinker
    @haircolor.setter
    def haircolor(self, haircolor): self.__haircolor = haircolor

class HorseResult():
    '''各馬のレース結果のデータクラス'''
    def __init__(self):
        self.__horse_no = '' # 馬番(複合PK)o
        self.__rank = '' # 着順o
        self.__goal_time = '' # タイムo
        self.__diff_distance = '' # 着差o
        self.__pass_rank = '' # 通過順o
        self.__nobori = '' # 上り3Fo
        self.__price = '' # 賞金o

    # getter
    @property
    def horse_no(self): return self.__horse_no
    @property
    def rank(self): return self.__rank
    @property
    def goal_time(self): return self.__goal_time
    @property
    def diff_distance(self): return self.__diff_distance
    @property
    def pass_rank(self): return self.__pass_rank
    @property
    def nobori(self): return self.__nobori
    @property
    def price(self): return self.__price

    # setter
    @horse_no.setter
    def horse_no(self, horse_no): self.__horse_no = horse_no
    @rank.setter
    def rank(self, rank): self.__rank = rank
    @goal_time.setter
    def goal_time(self, goal_time): self.__goal_time = goal_time
    @diff_distance.setter
    def diff_distance(self, diff_distance): self.__diff_distance = diff_distance
    @pass_rank.setter
    def pass_rank(self, pass_rank): self.__pass_rank = pass_rank
    @nobori.setter
    def nobori(self, nobori): self.__nobori = nobori
    @price.setter
    def price(self, price): self.__price = price

if __name__ == '__main__':
    RACE_ID = '202204020206'
    # 開催日(組み込み時はインスタンス変数)
    KAISAI_DATE = '20220724'
    # PC内で完結か
    LOCAL = False
    # レースIDをファイルから取得するか
    GET_FILE = True

    #for i in range(202202010201, 202202010213):
    #   RACE_ID = str(i)
    main()