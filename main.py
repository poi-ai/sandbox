import requests
import lxml
import pandas as pd
import re
from bs4 import BeautifulSoup

def get_param():
    # レース結果(HTML全体)
    soup = Soup()
    # レース結果(結果テーブル)
    table = Table(0)

    # 箱用意{馬番:[HorseInfo, HorseResult]}
    horse_dict = {i: [HorseInfo(), HorseResult()] for i in table['馬番']}

    # 1着馬の馬番
    winner_horse_no = 0

    # 行ごとに切り出し
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
            horse_dict[no][0].weight = 0
            horse_dict[no][0].weight_flg = 0
            horse_dict[no][0].weight_change = 0
            horse_dict[no][0].weight_change_flg = 0
        else:
            horse_dict[no][0].weight = weight.groups()[0]
            horse_dict[no][0].weight_flg = 1
            horse_dict[no][0].weight_change = weight.groups()[1].replace('±', '').replace('+', '')
            horse_dict[no][0].weight_change_flg = 1
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
        if i == 0:
            winner_horse_no = no
        elif i == 1
            horse_dict[winner_horse_no][1].diff_distance = '-' + str(row['着差'])
            horse_dict[no][1].diff_distance = row['着差']
        else:
            horse_dict[no][1].diff_distance = row['着差']
        horse_dict[no][1].price = row['賞金(万円)']
    #print(df.loc[0]['着順'])

def html():
    # 保存済みのHTML(ローカル内で完結するように疑似取得)
    f = open('html.txt', 'r')
    html = f.read()
    f.close()
    return html

def Soup():
    URL = 'https://db.netkeiba.com/race/202204020206/'
    # 馬柱 https://race.netkeiba.com/race/shutuba.html?race_id=202204020206
    r = requests.get(URL)
    return BeautifulSoup(r.content, 'lxml')

def Table(no = 0):
    #table[0]...結果テーブル｜[4]...コーナー順位｜[5]...ラップタイム

    # read_htmlで抜けなくなる余分なタグを除去
    HTML = str(Soup()).replace('<diary_snap_cut>', '').replace('</diary_snap_cut>', '')
    return pd.read_html(HTML)[no]

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
        self.__baba = '' # 馬場
        self.__weather = '' # 天候
        self.__baba_status = '' # 馬場状態
        self.__distance = '' # 距離
        self.__around = '' # 回り(右/左)
        self.__in_out = '' # 回り(内/外)
        self.__race_time = '' # 発走時刻
        self.__hold_no = '' # 開催回
        self.__hold_date = '' # 開催日
        self.__grade = '' # 格・グレード
        self.__require_age = '' # 出走条件(年齢)
        self.__require_gender = '' # 出走条件(性別)
        self.__require_country = '' # 出走条件(国内/国際/混合)
        self.__require_local = '' # 出走条件(特別指定/指定/他)
        self.__load_kind = '' # 斤量条件(定量/賞金別定/重賞別定/ハンデ)
        self.__first_prize = '' # 1着賞金 TODO 同着時チェック
        self.__second_prize = '' # 2着賞金
        self.__third_prize = '' # 3着賞金
        self.__fourth_prize = '' # 4着賞金
        self.__fifth_prize = '' # 5着賞金
        self.__horse_num = '' # 出走頭数

    # getter
    @property
    def race_name(self): return self.__race_name
    @property
    def baba(self): return self.__baba
    @property
    def weather(self): return self.__weather
    @property
    def baba_status(self): return self.__baba_status
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
    @baba_status.setter
    def baba_status(self, baba_status): self.__baba_status = baba_status
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
        self.__weight_flg = '' # 馬体重フラグo
        self.__weight_change = '' # 馬体重増減o
        self.__weight_change_flg = '' # 馬体重増減フラグo
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
    def weight_flg(self): return self.__weight_flg
    @property
    def weight_change(self): return self.__weight_change
    @property
    def weight_change_flg(self): return self.__weight_change_flg
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
    @weight_flg.setter
    def weight(self, weight): self.__weight_flg = weight_flg
    @weight_change.setter
    def weight_change(self, weight_change): self.__weight_change = weight_change
    @weight_change_flg.setter
    def weight_change(self, weight_change_flg): self.__weight_change_flg = weight_change_flg
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
        self.__pass_rank = '' # 通過順
        self.__nobori_3f = '' # 上り3F
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
    def nobori_3f(self): return self.__nobori_3f
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
    def nobori_3f(self, pass_rank): self.__pass_rank = pass_rank
    @nobori_3f.setter
    def nobori_3f(self, nobori_3f): self.__nobori_3f = nobori_3f
    @price.setter
    def price(self, price): self.__price = price

if __name__ == '__main__':
    HTML = html()
    #print(Table(1))
    #exit()
    ci = CommonInfo()
    ri = RaceInfo()
    rr = RaceResult()
    hi = HorseInfo()
    hr = HorseResult()
    get_param()