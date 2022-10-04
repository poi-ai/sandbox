import output
import lxml
import numpy as np
import requests
import time
import pandas as pd
import re
from bs4 import BeautifulSoup

ZERO_FIX = '0'

def url(type):
    # 馬柱
    if type == 'UMABASHIRA_URL':
        return f'https://nar.netkeiba.com/race/shutuba_past.html?race_id={RACE_ID}'
    # リアルタイム レース結果
    elif type == 'RACE_RESULT_URL':
        return f'https://nar.netkeiba.com/race/result.html?race_id={RACE_ID}'
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

    if not LOCAL and GET_FILE:
        id_list = get_race_id()

        for id in id_list:
            # レースIDをセット
            RACE_ID = str(id).replace('\n', '')

            # 馬柱からデータ取得
            horse_race_info_dict, race_info = get_umabashira()

            # レース結果(DB)からデータ取得
            horse_result_dict, race_progress_info = get_result(horse_race_info_dict, race_info)
    else:
        # 馬柱からデータ取得
        horse_race_info_dict, race_info = get_umabashira()

        # レース結果(DB)からデータ取得
        horse_result_dict, race_progress_info = get_result(horse_race_info_dict, race_info)

    # TODO 開催日、実装時はインスタンス変数
    race_date = KAISAI_DATE
    race_no = RACE_ID[-2:]
    baba_code = RACE_ID[4:6]

    # インスタンス変数確認用
    for index in horse_race_info_dict:
        horse_race_info = vars(horse_race_info_dict[index])
        df = pd.DataFrame.from_dict(horse_race_info, orient='index').T
        output.csv(df, 'horse_race_info')

    for index in horse_result_dict:
        horse_result = vars(horse_result_dict[index])
        df = pd.DataFrame.from_dict(horse_result, orient='index').T
        output.csv(df, 'horse_result')

    df = pd.DataFrame.from_dict(vars(race_info), orient='index').T
    output.csv(df, 'race_info')

def get_race_id():
    f = open('race_id.txt', 'r')
    id_list = [id for id in f]
    f.close()
    return id_list

def get_umabashira():
    # 実運用のhorse_dictはインスタンス変数(self)から引っ張る

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

    # コース情報や状態を抽出
    race_data_01 = soup.find('div', class_ = 'RaceData01')
    race_data_list = rm(race_data_01.text).split('/')

    race_info.race_time = race_data_list[0].replace('発走', '')

    # TODO 地方はin_out除去

    # TODO レースIDからばんえい判定
    if re.compile('\d{4}65\d{6}').search(RACE_ID):
        race_info.baba = 'ば'
        race_info.distance = '200'
        # TODO ばんえいの馬場状態変数追加
    else:
        course = re.search('([芝|ダ])(\d+)m\((.*)\)', race_data_list[1])

        race_info.distance = course.groups()[1]

        baba = course.groups()[0]
        race_info.baba = baba
        if baba == '芝':
            race_info.glass_condition = race_data_list[3].replace('馬場:', '')
        elif baba == 'ダ':
            race_info.dirt_condition = race_data_list[3].replace('馬場:', '')

        race_info.around = course.groups()[2]

    # TODO ばんえいの場合どうかチェック
    race_info.weather = race_data_list[2].replace('天候:', '')

    # 出走条件等の抽出
    race_data_02 = soup.find('div', class_ = 'RaceData02')
    race_data_list = race_data_02.text.split('\n')

    race_info.hold_no = race_data_list[1].replace('回', '')
    race_info.hold_date = race_data_list[3].replace('日目', '')

    require_split = race_data_list[4].find(' ')
    race_info.require_age = half(race_data_list[4][:require_split]).replace('サラ系', '')
    race_info.race_class = half(race_data_list[4][require_split + 1:])

    race_name = soup.find('div', class_ = 'RaceName')
    race_info.race_name = race_name.text.replace('\n', '')

    # CSSからクラスチェック、13はWIN5
    if 'Icon_GradeType1"' in str(race_name):
        race_info.grade = 'GI'
    elif 'Icon_GradeType2' in str(race_name):
        race_info.grade = 'GII'
    elif 'Icon_GradeType3' in str(race_name):
        race_info.grade = 'GIII'
    elif 'Icon_GradeType4' in str(race_name):
        race_info.grade = '重賞'
    elif 'Icon_GradeType5' in str(race_name):
        race_info.grade = 'OP'
    elif 'Icon_GradeType6' in str(race_name):
        race_info.grade = '1600万下'
    elif 'Icon_GradeType7' in str(race_name):
        race_info.grade = '1000万下'
    elif 'Icon_GradeType8' in str(race_name):
        race_info.grade = '900万下'
    elif 'Icon_GradeType9' in str(race_name):
        race_info.grade = '500万下'
    elif 'Icon_GradeType10' in str(race_name):
        race_info.grade = 'JGI'
    elif 'Icon_GradeType11' in str(race_name):
        race_info.grade = 'JGII'
    elif 'Icon_GradeType12' in str(race_name):
        race_info.grade = 'JGIII'
    elif 'Icon_GradeType15' in str(race_name):
        race_info.grade = 'L'
    elif 'Icon_GradeType16' in str(race_name):
        race_info.grade = '3勝'
    elif 'Icon_GradeType17' in str(race_name):
        race_info.grade = '2勝'
    elif 'Icon_GradeType18' in str(race_name):
        race_info.grade = '1勝'

    # TODO 待選とは何か確認
    if 'Icon_GradeType14' in str(race_name):
        race_info.grade += '待選'

    race_info.horse_num = race_data_list[5].replace('頭', '')

    # TODO 年齢以外の出走条件取得

    prize = re.search('本賞金:(.+)、(.+)、(.+)、(.+)、(.+)万円', race_data_list[7])
    race_info.first_prize = prize.groups()[0]
    race_info.second_prize = prize.groups()[1]
    race_info.third_prize = prize.groups()[2]
    race_info.fourth_prize = prize.groups()[3]
    race_info.fifth_prize = prize.groups()[4]

    # 各馬情報の箱用意{馬番:HorseRaceInfo, 馬番:HorseRaceInfo,...}
    horse_race_info_dict = {}
    horse_char_info_dict = {}

    fc = soup.select('dl[class="fc"]')
    for i, info in enumerate(fc):
        horse_race_info = HorseRaceInfo()
        horse_char_info = HorseCharInfo()

        horse_char_info.father = info.find('dt', class_ = 'Horse01').text
        horse_type = info.find('dt', class_ = 'Horse02')
        # TODO マル/カクの違いはレース種別の違いだけなので、種類は地/外だけにするか要検討
        # TODO パラメータをbelongに統一するかも要検討
        if 'Icon_MaruChi' in str(horse_type):
            horse_race_info.belong = 'マル地'
        elif 'Icon_kakuChi' in str(horse_type):
            horse_race_info.belong = 'カク地'
        elif 'Icon_MaruGai' in str(horse_type):
            horse_race_info.country = 'マル外'
        elif 'Icon_KakuGai' in str(horse_type):
            horse_race_info.country = 'カク外'

        if '<span class="Mark">B</span>' in str(horse_type):
            horse_race_info.blinker = '1'

        m = re.search('db.netkeiba.com/horse/(\d+)/"', str(horse_type))
        if m != None:
            horse_race_info.horse_id = m.groups()[0]

        horse_char_info.horse_name = horse_type.text.replace('\n', '')

        horse_char_info.mother = info.find('dt', class_ = 'Horse03').text
        horse_char_info.grandfather = info.find('dt', class_ = 'Horse04').text.replace('(', '').replace(')', '')

        trainer = info.find('dt', class_ = 'Horse05').text.split('・')
        horse_race_info.trainer_belong = trainer[0]
        horse_race_info.trainer = trainer[1]

        trainer_id = re.search('db.netkeiba.com/trainer/(\d+)/', str(info))
        if trainer_id != None:
            horse_race_info.trainer_id = trainer_id.groups()[0]

        blank = info.find('dt', class_ = 'Horse06').text
        if blank == '連闘':
            horse_race_info.blank = '0'
        else:
            blank_week = re.search('中(\d+)週', blank)
            # 初出走判定
            if blank_week == None:
                horse_race_info.blank = '-1'
            else:
                horse_race_info.blank = blank_week.groups()[0]

        running_type = str(info.find('dt', class_ = 'Horse06'))
        if 'horse_race_type00' in running_type:
            horse_race_info.running_type = '未'
        elif 'horse_race_type01' in running_type:
            horse_race_info.running_type = '逃'
        elif 'horse_race_type02' in running_type:
            horse_race_info.running_type = '先'
        elif 'horse_race_type03' in running_type:
            horse_race_info.running_type = '差'
        elif 'horse_race_type04' in running_type:
            horse_race_info.running_type = '追'
        elif 'horse_race_type05' in running_type:
            horse_race_info.running_type = '自在'

        weight = re.search('(\d+)kg\((.+)\)', info.find('dt', class_ = 'Horse07').text)
        # TODO 計不対応
        if weight != None:
            horse_race_info.weight = weight.groups()[0]
            horse_race_info.weight_change = str(int(weight.groups()[1]))

        odds = re.search('(\d+\.\d)\((.+)人気\)', rm(info.find('dt', class_ = 'Horse07').text))
        # TODO 取消馬対応
        if odds != None:
            horse_race_info.popular = odds.groups()[0]
            horse_race_info.win_odds = odds.groups()[1]

        horse_race_info.horse_no = str(i + 1)

        horse_race_info.frame_no = frame_no_culc(race_info.horse_num, int(i + 1))

        horse_race_info_dict[str(i + 1)] = horse_race_info

    jockeys = soup.find_all('td', class_ = 'Jockey')
    for i, info in enumerate(jockeys):
        horse_race_info = horse_race_info_dict[str(i + 1)]

        m = re.search('([牡|牝|セ])(\d+)(.+)', info.find('span', class_ = 'Barei').text)
        if m != None:
            horse_race_info.gender = m.groups()[0]
            horse_race_info.age = m.groups()[1]
            horse_char_info.hair_color = m.groups()[2]

        jockey = re.search('db.netkeiba.com/jockey/(\d+)/">(.+)</a>', str(info))
        if jockey != None:
            horse_race_info.jockey_id = jockey.groups()[0]
            horse_race_info.jockey = jockey.groups()[1]

        load = re.search('<span>(\d+\d.\d+)</span>', str(info))
        if load != None:
            horse_race_info.load = load.groups()[0]

        horse_race_info_dict[str(i + 1)] = horse_race_info
        horse_char_info_dict[str(i + 1)] = horse_char_info

    return horse_race_info_dict, race_info

def get_result(horse_race_info_dict, race_info):
    # TODO owner, pass_rank, prizeが取れない
    # レース結果(HTML全体)
    if LOCAL:
        f = open('result_sjis.txt', 'r')
        html = f.read()
        f.close()
        soup = BeautifulSoup(html, 'lxml')
    else:
        soup = Soup(url('RACE_RESULT_URL'))

    # レース結果(結果テーブル)
    tables = Table(soup)
    table = tables[0]

    # 箱用意{馬番:HorseResult, 馬番:HorseResult, ...}
    horse_result_dict = {}

    # 1着馬の馬番
    winner_horse_no = 0

    # 列ごとに切り出し
    # TODO 除外・取消馬の処理
    for i, index in enumerate(table.index):
        horse_result = HorseResult()

        # 結果テーブルの列取得
        row = table.loc[index]

        # レース結果の各項目を設定
        horse_result.horse_no = row['馬番']
        horse_result.rank = row['着順']
        horse_result.goal_time = row['タイム']

        # 着差、1着馬は2着との差をマイナスに
        # TODO 同着時対応
        if i == 0:
            winner_horse_no = str(row['馬番'])
        elif i == 1:
            horse_result_dict[winner_horse_no].diff = '-' + str(row['着差'])
            horse_result.diff = row['着差']
        else:
            horse_result.diff = row['着差']

        # TODO 同着時計算
        if str(row['着順']) == '1':
            horse_result.prize = str(race_info.first_prize)
        elif str(row['着順']) == '2':
            horse_result.prize = str(race_info.second_prize)
        elif str(row['着順']) == '3':
            horse_result.prize = str(race_info.third_prize)
        elif str(row['着順']) == '4':
            horse_result.prize = str(race_info.fourth_prize)
        elif str(row['着順']) == '5':
            horse_result.prize = str(race_info.fifth_prize)

        horse_result.agari = row['後3F']

        horse_result.horse_id = horse_race_info_dict[str(row['馬番'])].horse_id

        horse_result_dict[str(row['馬番'])] = horse_result

    # レースの経過情報
    race_progress_info = RaceProgressInfo()

    race_progress_info.race_info = RACE_ID

    # コーナー通過順、read_htmlでは','が除去されるため抽出不可
    rank_table = soup.find('table', class_ = 'RaceCommon_Table Corner_Num').text.split('\n')
    for index in range(len(rank_table)):
        if rank_table[index] == '1コーナー':
            race_progress_info.corner1_rank = rank_table[index + 1].replace(',', '、')
        elif rank_table[index] == '2コーナー':
            race_progress_info.corner2_rank = rank_table[index + 1].replace(',', '、')
        elif rank_table[index] == '3コーナー':
            race_progress_info.corner3_rank = rank_table[index + 1].replace(',', '、')
        elif rank_table[index] == '4コーナー':
            race_progress_info.corner4_rank = rank_table[index + 1].replace(',', '、')

    # TODO ラップ抽出
    lap_table = soup.find('table', class_ = 'RaceCommon_Table Race_HaronTime')

    return horse_result_dict, race_progress_info

def frame_no_culc(horse_num, horse_no):
    horse_no = int(horse_no)
    horse_num = int(horse_num)

    if horse_no == 1:
        return str(1)

    if horse_num <= 8 or horse_no < horse_num * -1 + 18:
        return str(horse_no)
    elif horse_num <= 16:
        if horse_no <= 8:
            return str(min(8, horse_no) - int((horse_no - (horse_num * -1 + 16)) / 2))
        else:
            return str(int(8 - (horse_num - horse_no - 1) / 2))
    else:
        if horse_no >= 17:
            return str(8)
        elif horse_num == 18 and horse_no == 15:
            return str(7)
        else:
            return frame_no_culc(16, horse_no)

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

def rm(str):
    '''改行・空白を除去'''
    return str.replace('\n', '').replace(' ', '')

def half(str):
    '''全角を半角へ変換'''
    return str.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

class RaceInfo():
    '''発走前のレースに関するデータのデータクラス'''
    def __init__(self):
        self.__race_id = '' # レースID(netkeiba準拠、PK)
        self.__race_date = '' # レース開催日
        self.__race_no = '' # レース番号
        self.__baba_code = '' # 競馬場コード
        self.__race_name = '' # レース名o
        self.__race_type = '平' # レース形態(平地/障害/ばんえい)
        self.__baba = '' # 馬場(芝/ダート)o
        self.__weather = '' # 天候△
        self.__glass_condition = '' # 馬場状態(芝)o
        self.__dirt_condition = '' # 馬場状態(ダート)o
        self.__distance = '' # 距離o
        self.__around = '' # 回り(右/左)o
        self.__in_out = ZERO_FIX # 使用コース(内回り/外回り)[地方はないため0固定]
        self.__race_time = '' # 発走時刻o
        self.__hold_no = '' # 開催回o
        self.__hold_date = '' # 開催日o
        self.__race_class = '' # クラスo
        self.__grade = '' # グレードo TODO
        self.__require_age = '' # 出走条件(年齢)o
        self.__require_gender = '' # 出走条件(牝馬限定戦) TODO
        self.__require_kyushu = ZERO_FIX # 出走条件(九州産馬限定戦) TODO
        self.__require_beginner_jockey = ZERO_FIX # 出走条件(見習騎手限定戦) TODO
        self.__require_country = '' # 出走条件(国際/混合) TODO
        self.__require_local = '' # 出走条件(特別指定/指定) TODO
        self.__load_kind = '' # 斤量条件(定量/馬齢/別定/ハンデ) TODO
        self.__first_prize = '' # 1着賞金o
        self.__second_prize = '' # 2着賞金o
        self.__third_prize = '' # 3着賞金o
        self.__fourth_prize = '' # 4着賞金o
        self.__fifth_prize = '' # 5着賞金o
        self.__horse_num = '' # 出走頭数o

    # getter
    @property
    def race_id(self): return self.__race_id
    @property
    def race_date(self): return self.__race_date
    @property
    def race_no(self): return self.__race_no
    @property
    def baba_code(self): return self.__baba_code
    @property
    def race_name(self): return self.__race_name
    @property
    def race_type(self): return self.__race_type
    @property
    def baba(self): return self.__baba
    @property
    def weather(self): return self.__weather
    @property
    def glass_condition(self): return self.__glass_condition
    @property
    def dirt_condition(self): return self.__dirt_condition
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
    def race_class(self): return self.__race_class
    @property
    def grade(self): return self.__grade
    @property
    def require_age(self): return self.__require_age
    @property
    def require_gender(self): return self.__require_gender
    @property
    def require_kyushu(self): return self.__require_kyushu
    @property
    def require_beginner_jockey(self): return self.__require_beginner_jockey
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
    @race_id.setter
    def race_id(self, race_id): self.__race_id = race_id
    @race_date.setter
    def race_date(self, race_date): self.__race_date = race_date
    @race_no.setter
    def race_no(self, race_no): self.__race_no = race_no
    @baba_code.setter
    def baba_code(self, baba_code): self.__baba_code = baba_code
    @race_name.setter
    def race_name(self, race_name): self.__race_name = race_name
    @race_type.setter
    def race_type(self, race_type): self.__race_type = race_type
    @baba.setter
    def baba(self, baba): self.__baba = baba
    @weather.setter
    def weather(self, weather): self.__weather = weather
    @glass_condition.setter
    def glass_condition(self, glass_condition): self.__glass_condition = glass_condition
    @dirt_condition.setter
    def dirt_condition(self, dirt_condition): self.__dirt_condition = dirt_condition
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
    @race_class.setter
    def race_class(self, race_class): self.__race_class = race_class
    @grade.setter
    def grade(self, grade): self.__grade = grade
    @require_age.setter
    def require_age(self, require_age): self.__require_age = require_age
    @require_gender.setter
    def require_gender(self, require_gender): self.__require_gender = require_gender
    @require_kyushu.setter
    def require_kyushu(self, require_kyushu): self.__require_kyushu = require_kyushu
    @require_beginner_jockey.setter
    def require_beginner_jockey(self, require_beginner_jockey): self.__require_beginner_jockey = require_beginner_jockey
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

class RaceProgressInfo():
    '''レース全体のレース結果を保持するデータクラス'''
    def __init__(self):
        self.__race_id = '' # レースID(netkeiba準拠、PK)o
        self.__corner1_rank = '' # 第1コーナー通過順(馬番)o
        self.__corner2_rank = '' # 第2コーナー通過順(馬番)o
        self.__corner3_rank = '' # 第3コーナー通過順(馬番)o
        self.__corner4_rank = '' # 第4コーナー通過順(馬番)o
        self.__pace = [] # 先頭馬のペース(秒) TODO

    # getter
    @property
    def race_id(self): return self.__race_id
    @property
    def corner1_rank(self): return self.__corner1_rank
    @property
    def corner2_rank(self): return self.__corner2_rank
    @property
    def corner3_rank(self): return self.__corner3_rank
    @property
    def corner4_rank(self): return self.__corner4_rank
    @property
    def pace(self): return self.__pace

    # setter
    @race_id.setter
    def race_id(self, race_id): self.__race_id = race_id
    @corner1_rank.setter
    def corner1_rank(self, corner1_rank): self.__corner1_rank = corner1_rank
    @corner2_rank.setter
    def corner2_rank(self, corner2_rank): self.__corner2_rank = corner2_rank
    @corner3_rank.setter
    def corner3_rank(self, corner3_rank): self.__corner3_rank = corner3_rank
    @corner4_rank.setter
    def corner4_rank(self, corner4_rank): self.__corner4_rank = corner4_rank
    @pace.setter
    def pace(self, pace): self.__pace = pace

class HorseRaceInfo():
    '''各馬の発走前のデータを保持するデータクラス'''
    def __init__(self):
        self.__horse_id = '' # 競走馬ID(netkeiba準拠、複合PK)o
        self.__frame_no = '' # 枠番 o
        self.__horse_no = '' # 馬番o
        self.__age = '' # 馬齢o
        self.__gender = '' # 性別o
        self.__load = '' # 斤量o
        self.__jockey_id = '' # 騎手IDo
        self.__jockey = '' # 騎手名o
        self.__jockey_handi = '' # 騎手減量 TODO
        self.__win_odds = '' # 単勝オッズo
        self.__popular = '' # 人気o
        self.__weight = '' # 馬体重o
        self.__weight_change = '' # 馬体重増減o
        self.__trainer_id = '' # 調教師IDo
        self.__trainer = '' # 調教師名o
        self.__trainer_belong = '' # 調教師所属(美浦/栗東)o
        self.__owner = '' # 馬主名 TODO
        self.__blank = '' # レース間隔o
        self.__running_type = '' # 脚質(←netkeibaの主観データ？)o
        self.__country = '' # 所属(外国馬か)o
        self.__belong = '' # 所属(地方馬か)o
        self.__blinker = '0' # ブリンカー(有/無)o

    # getter
    @property
    def horse_id(self): return self.__horse_id
    @property
    def frame_no(self): return self.__frame_no
    @property
    def horse_no(self): return self.__horse_no
    @property
    def age(self): return self.__age
    @property
    def gender(self): return self.__gender
    @property
    def load(self): return self.__load
    @property
    def jockey_id(self): return self.__jockey_id
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
    def trainer_id(self): return self.__trainer_id
    @property
    def trainer(self): return self.__trainer
    @property
    def trainer_belong(self): return self.__trainer_belong
    @property
    def owner(self): return self.__owner
    @property
    def blank(self): return self.__blank
    @property
    def running_type(self): return self.__running_type
    @property
    def country(self): return self.__country
    @property
    def belong(self): return self.__belong
    @property
    def blinker(self): return self.__blinker

    # setter
    @horse_id.setter
    def horse_id(self, horse_id): self.__horse_id = horse_id
    @frame_no.setter
    def frame_no(self, frame_no): self.__frame_no = frame_no
    @horse_no.setter
    def horse_no(self, horse_no): self.__horse_no = horse_no
    @age.setter
    def age(self, age): self.__age = age
    @gender.setter
    def gender(self, gender): self.__gender = gender
    @load.setter
    def load(self, load): self.__load = load
    @jockey_id.setter
    def jockey_id(self, jockey_id): self.__jockey_id = jockey_id
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
    @trainer_id.setter
    def trainer_id(self, trainer_id): self.__trainer_id = trainer_id
    @trainer.setter
    def trainer(self, trainer): self.__trainer = trainer
    @trainer_belong.setter
    def trainer_belong(self, trainer_belong): self.__trainer_belong = trainer_belong
    @owner.setter
    def owner(self, owner): self.__owner = owner
    @blank.setter
    def blank(self, blank): self.__blank = blank
    @running_type.setter
    def running_type(self, running_type): self.__running_type = running_type
    @country.setter
    def country(self, country): self.__country = country
    @belong.setter
    def belong(self, belong): self.__belong = belong
    @blinker.setter
    def blinker(self, blinker): self.__blinker = blinker


class HorseCharInfo():
    def __init__(self):
        self.__horse_id = '' # 競走馬ID(netkeiba準拠、複合PK)o
        self.__horse_name = '' # 馬名
        self.__father = '' # 父名
        self.__mother = '' # 母名
        self.__grandfather = '' # 母父名
        self.__hair_color = '' # 毛色

    # getter
    @property
    def horse_id(self): return self.__horse_id
    @property
    def horse_name(self): return self.__horse_name
    @property
    def father(self): return self.__father
    @property
    def mother(self): return self.__mother
    @property
    def grandfather(self): return self.__grandfather
    @property
    def hair_color(self): return self.__hair_color

    # setter
    @horse_id.setter
    def horse_id(self, horse_id): self.__horse_id = horse_id
    @horse_name.setter
    def horse_name(self, horse_name): self.__horse_name = horse_name
    @father.setter
    def father(self, father): self.__father = father
    @mother.setter
    def mother(self, mother): self.__mother = mother
    @grandfather.setter
    def grandfather(self, grandfather): self.__grandfather = grandfather
    @hair_color.setter
    def hair_color(self, hair_color): self.__hair_color = hair_color

class HorseResult():
    '''各馬のレース結果のデータクラス'''
    def __init__(self):
        self.__horse_id = '' # 競走馬ID(netkeiba準拠、複合PK)
        self.__horse_no = '' # 馬番o
        self.__rank = '' # 着順o
        self.__goal_time = '' # タイムo
        self.__diff = '' # 着差o
        self.__agari = '' # 上り3Fo
        self.__prize = '0' # 賞金o

    # getter
    @property
    def horse_id(self): return self.__horse_id
    @property
    def horse_no(self): return self.__horse_no
    @property
    def rank(self): return self.__rank
    @property
    def goal_time(self): return self.__goal_time
    @property
    def diff(self): return self.__diff
    @property
    def agari(self): return self.__agari
    @property
    def prize(self): return self.__prize

    # setter
    @horse_id.setter
    def horse_id(self, horse_id): self.__horse_id = horse_id
    @horse_no.setter
    def horse_no(self, horse_no): self.__horse_no = horse_no
    @rank.setter
    def rank(self, rank): self.__rank = rank
    @goal_time.setter
    def goal_time(self, goal_time): self.__goal_time = goal_time
    @diff.setter
    def diff(self, diff): self.__diff = diff
    @agari.setter
    def agari(self, agari): self.__agari = agari
    @prize.setter
    def prize(self, prize): self.__prize = prize

if __name__ == '__main__':
    RACE_ID = '202248090103'
    # 開催日(組み込み時はインスタンス変数)
    KAISAI_DATE = '20220901'
    # PC内で完結か
    LOCAL = True
    #LOCAL = False
    # レースIDをファイルから取得するか
    #GET_FILE = True
    GET_FILE = False

    #for i in range(202202010201, 202202010213):
    #   RACE_ID = str(i)
    main()
    #print(get_result())