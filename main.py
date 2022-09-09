import output
import lxml
import numpy as np
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

            # 馬柱からデータ取得 TODO 引数はインスタンス変数に
            get_umabashira(horse_dict)
    else:
        # レース結果(DB)からデータ取得
        horse_dict = get_result()

        # 馬柱からデータ取得
        horse_dict, race_info = get_umabashira(horse_dict)

        # インスタンス変数確認用
        for dict in horse_dict:
            horse_info = vars(horse_dict[dict][0])
            df = pd.DataFrame.from_dict(horse_info, orient='index').T
            output.csv(df, 'horse_info')

            horse_result = vars(horse_dict[dict][1])
            df = pd.DataFrame.from_dict(horse_result, orient='index').T
            output.csv(df, 'horse_result')

        df = pd.DataFrame.from_dict(vars(race_info), orient='index').T
        output.csv(df, 'race_info')

def get_race_id():
    f = open('race_id.txt', 'r')
    id_list = [id for id in f]
    f.close()
    return id_list

def get_umabashira(horse_dict):
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

    course = re.search('([芝|ダ|障])(\d+)m\((.*)\)', race_data_list[1])
    race_info.distance = course.groups()[1]

    if course.groups()[0] == '障':
        race_info.race_type = '障'

        baba = course.groups()[2]
        if '芝' in baba:
            if 'ダート' in baba:
                race_info.baba = '芝ダ'
                race_info.glass_condition = race_data_list[3].replace('馬場:', '')
                if len(race_data_list) == 5:
                    race_info.dirt_condition = race_data_list[4].replace('馬場:', '')
            else:
                race_info.baba = '芝'
                race_info.glass_condition = race_data_list[3].replace('馬場:', '')
        else:
            race_info.baba = 'ダ'
            race_info.dirt_condition = race_data_list[3].replace('馬場:', '')

        around = re.sub(r'[芝ダート]', '', baba)
        if len(around) != 0:
            race_info.in_out = around

    else:
        race_info.race_type = '平'

        baba = course.groups()[0]
        race_info.baba = baba
        if baba == '芝':
            race_info.glass_condition = race_data_list[3].replace('馬場:', '')
        elif baba == 'ダ':
            race_info.dirt_condition = race_data_list[3].replace('馬場:', '')

        around = course.groups()[2]
        if around == '直線':
            race_info.around = '直'
        else:
            race_info.around = around[0]
            if len(around) != 1:
                race_info.in_out = around[1:]

    race_info.weather = race_data_list[2].replace('天候:', '')

    # 出走条件等の抽出
    race_data_02 = soup.find('div', class_ = 'RaceData02')
    race_data_list = race_data_02.text.split('\n')

    race_info.hold_no = race_data_list[1].replace('回', '')
    race_info.hold_date = race_data_list[3].replace('日目', '')
    race_info.require_age = half(race_data_list[4]).replace('サラ系', '').replace('障害', '')
    race_info.race_class = half(race_data_list[5])

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

    require = race_data_list[6]
    if '(国際)' in require:
        race_info.require_country = '国'
    elif '(混)' in require:
        race_info.require_country = '混'

    if '牡・牝' in require:
        race_info.require_gender = '牡牝'
    elif '牝' in require:
        race_info.require_gender = '牝'

    if '九州産馬' in require:
        race_info.require_local = '1'

    if '見習騎手' in require:
        race_info.require_beginner_jockey = '1'

    if '(指)' in require:
        race_info.require_local = 'マル指'
    elif '(特指)' in require:
        race_info.require_local = '特指'
    elif '指' in require:
        race_info.require_local = 'カク指'

    # TODO 別定/ハンデ戦はより詳細に分類できるかチェック
    race_info.load_kind = race_data_list[7]
    race_info.horse_num = race_data_list[8].replace('頭', '')

    prize = re.search('本賞金:(\d+),(\d+),(\d+),(\d+),(\d+)万円', race_data_list[10])
    race_info.first_prize = prize.groups()[0]
    race_info.second_prize = prize.groups()[1]
    race_info.third_prize = prize.groups()[2]
    race_info.fourth_prize = prize.groups()[3]
    race_info.fifth_prize = prize.groups()[4]

    # 各馬の情報(TODO レース結果で取得したものと合体)
    # horse_info = HorseInfo()

    fc = soup.select('div[class="fc"]')

    for info in fc:
        horse_info = ''

        horse_type = info.find('div', class_ = 'Horse02')

        # 馬番(キー)から設定するdictを選択
        for horse in horse_dict:
            if horse_dict[horse][0].horse_name == rm(horse_type.text):
                horse_info = horse_dict[horse][0]

        horse_info.father = info.find('div', class_ = 'Horse01').text

        # TODO マル/カクの違いはレース種別の違いだけなので、種類は地/外だけにするか要検討
        # TODO パラメータをbelongに統一するかも要検討
        if 'Icon_MaruChi' in str(horse_type):
            horse_info.belong = 'マル地'
        elif 'Icon_kakuChi' in str(horse_type):
            horse_info.belong = 'カク地'
        elif 'Icon_MaruGai' in str(horse_type):
            horse_info.country = 'マル外'
        elif 'Icon_KakuGai' in str(horse_type):
            horse_info.country = 'カク外'

        if '<span class="Mark">B</span>' in str(horse_type):
            horse_info.blinker = '1'

        horse_info.mother = info.find('div', class_ = 'Horse03').text
        horse_info.grandfather = info.find('div', class_ = 'Horse04').text.replace('(', '').replace(')', '')

        blank = info.find('div', class_ = 'Horse06').text
        if blank == '連闘':
            horse_info.blank = '0'
        else:
            blank_week = re.search('中(\d+)週', blank)
            # 初出走判定
            if blank_week == None:
                horse_info.blank = '-1'
            else:
                horse_info.blank = prize.groups()[0]

        running_type = str(info.find('div', class_ = 'Horse06'))
        if 'horse_race_type00' in running_type:
            horse_info.running_type = '未'
        elif 'horse_race_type01' in running_type:
            horse_info.running_type = '逃'
        elif 'horse_race_type02' in running_type:
            horse_info.running_type = '先'
        elif 'horse_race_type03' in running_type:
            horse_info.running_type = '差'
        elif 'horse_race_type04' in running_type:
            horse_info.running_type = '追'
        elif 'horse_race_type05' in running_type:
            horse_info.running_type = '自在'

    hair_colors = soup.find_all('span', class_ = 'Barei')
    for i, hair_color in enumerate(hair_colors):
        m = re.search('.\d(.+)', hair_color.text)
        # 別の箇所でも使われているクラスなので判定が必要
        if m == None:
            break
        else:
            horse_dict[i + 1][0].hair_color = m.groups()[0]

    # 実運用ではクラス化するため、返り値なしでインスタンス変数へ代入
    return horse_dict, race_info

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
        horse_dict[no][0].gender = row['性齢'][0]
        horse_dict[no][0].age = row['性齢'][1:]
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
            horse_dict[no][0].trainer_belong = '-'
            horse_dict[no][0].trainer = '-'
        else:
            horse_dict[no][0].trainer_belong = trainer.groups()[0]
            horse_dict[no][0].trainer = trainer.groups()[1]
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
            horse_dict[winner_horse_no][1].diff = '-' + str(row['着差'])
            horse_dict[no][1].diff = row['着差']
        else:
            horse_dict[no][1].diff = row['着差']
        horse_dict[no][1].pass_rank = row['通過']
        horse_dict[no][1].agari = row['上り']
        if not np.isnan(row['賞金(万円)']):
            horse_dict[no][1].prize = row['賞金(万円)']

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
        self.__race_name = '' # レース名o
        self.__race_type = '' # レース形態(平地/障害)o
        self.__baba = '' # 馬場(芝/ダート)o
        self.__weather = '' # 天候o
        self.__glass_condition = '' # 馬場状態(芝)o
        self.__dirt_condition = '' # 馬場状態(ダート)o
        self.__distance = '' # 距離o
        self.__around = '' # 回り(右/左)o
        self.__in_out = '' # 使用コース(内回り/外回り)o
        self.__race_time = '' # 発走時刻o
        self.__hold_no = '' # 開催回o
        self.__hold_date = '' # 開催日o
        self.__race_class = '' # クラスo
        self.__grade = '' # グレード TODO
        self.__require_age = '' # 出走条件(年齢)o
        self.__require_gender = '' # 出走条件(牝馬限定戦)o
        self.__require_kyushu = '0' # 出走条件(九州産馬限定戦)o
        self.__require_beginner_jockey = '0' # 出走条件(見習騎手限定戦)o
        self.__require_country = '' # 出走条件(国際/混合)o
        self.__require_local = '' # 出走条件(特別指定/指定)o
        self.__load_kind = '' # 斤量条件(定量/馬齢/別定/ハンデ)o
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

class RaceResult():
    '''レース全体のレース結果を保持するデータクラス'''
    def __init__(self):
        self.__corner_rank = [] # コーナー通過順(馬番) TODO
        self.__pace = [] # 先頭馬のペース(秒) TODO

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
        self.__jockey_handi = '' # 騎手減量 TODO
        self.__win_odds = '' # 単勝オッズo
        self.__popular = '' # 人気o
        self.__weight = '' # 馬体重o
        self.__weight_change = '' # 馬体重増減o
        self.__trainer = '' # 調教師名o
        self.__trainer_belong = '' # 調教師所属(美浦/栗東)o
        self.__owner = '' # 馬主名o

        # 以下は馬柱から
        # TODO 不変データ(血統関係)は別クラスで切り出し、未出走時のみ入れるか検討
        # TODO ↑最古データが未出走でない場合は取得できないから一回ずつチェック入れる？
        self.__blank = '' # レース間隔o
        self.__father = '' # 父名o
        self.__mother = '' # 母名o
        self.__grandfather = '' # 母父名o
        self.__running_type = '' # 脚質(←netkeibaの主観データ？)o
        self.__country = '日' # 所属(外国馬か)o
        self.__belong = '非地' # 所属(地方馬か)o
        self.__blinker = '0' # ブリンカー(有/無)o
        self.__hair_color = '' # 毛色
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
    def mother(self): return self.__mother
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
    def hair_color(self): return self.__hair_color

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
    @mother.setter
    def mother(self, mother): self.__mother = mother
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
    @hair_color.setter
    def hair_color(self, hair_color): self.__hair_color = hair_color

class HorseResult():
    '''各馬のレース結果のデータクラス'''
    def __init__(self):
        self.__horse_no = '' # 馬番(複合PK)o
        self.__rank = '' # 着順o
        self.__goal_time = '' # タイムo
        self.__diff = '' # 着差o
        self.__pass_rank = '' # 通過順o
        self.__agari = '' # 上り3Fo
        self.__prize = '0' # 賞金o

    # getter
    @property
    def horse_no(self): return self.__horse_no
    @property
    def rank(self): return self.__rank
    @property
    def goal_time(self): return self.__goal_time
    @property
    def diff(self): return self.__diff
    @property
    def pass_rank(self): return self.__pass_rank
    @property
    def agari(self): return self.__agari
    @property
    def prize(self): return self.__prize

    # setter
    @horse_no.setter
    def horse_no(self, horse_no): self.__horse_no = horse_no
    @rank.setter
    def rank(self, rank): self.__rank = rank
    @goal_time.setter
    def goal_time(self, goal_time): self.__goal_time = goal_time
    @diff.setter
    def diff(self, diff): self.__diff = diff
    @pass_rank.setter
    def pass_rank(self, pass_rank): self.__pass_rank = pass_rank
    @agari.setter
    def agari(self, agari): self.__agari = agari
    @prize.setter
    def prize(self, prize): self.__prize = prize

if __name__ == '__main__':
    RACE_ID = '202204020206'
    # 開催日(組み込み時はインスタンス変数)
    KAISAI_DATE = '20220724'
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