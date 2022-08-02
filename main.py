import lxml
import pandas as pd
from bs4 import BeautifulSoup

def get_param():
    # レース結果(HTML全体)
    soup = Soup()
    # レース結果(結果テーブル)
    table = Table(0)

    # 箱用意{馬番:[HorseInfo, HorseResult]}
    horse_dict = {i: [HorseInfo(), HorseResult()] for i in table['馬番']}

    # 行ごとに切り出し
    for index in table.index:
        row = table.loc[index]
        # キーになる馬番を取得
        no = row['馬番']
        horse_dict[no][1].horse_num = row['馬番']
    #print(df.loc[0]['着順'])

def html():
    # 保存済みのHTML(ローカル内で完結するように疑似取得)
    f = open('html.txt', 'r')
    html = f.read()
    f.close()
    return html

def Soup():
    return BeautifulSoup(HTML, 'lxml')

def Table(no = 0):
    #table[0]...結果テーブル｜[4]...コーナー順位｜[5]...ラップタイム
    return pd.read_html(HTML)[no]

class CommonInfo():
    '''レースを一意に定めるデータのデータクラス'''
    def __init__(self):
        self.__race_date = '' # レース開催日
        self.__race_num = '' # レース番号
        self.__baba_code = '' # 競馬場コード

    # getter
    @property
    def race_date(self): return self.__race_date
    @property
    def race_num(self): return self.__race_num
    @property
    def baba_code(self): return self.__baba_code

    # setter
    @race_date.setter
    def race_date(self, race_date): self.__race_date = race_date
    @race_num.setter
    def race_num(self, race_num): self.__race_num = race_num
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
        self.__hold_num = '' # 開催回
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
    def hold_num(self): return self.__hold_num
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
    @hold_num.setter
    def hold_num(self, hold_num): self.__hold_num = hold_num
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
        self.__frame_num = '' # 枠番
        self.__horse_num = '' # 馬番(複合PK)
        self.__horse_name = '' # 馬名
        self.__age = '' # 馬齢
        self.__gender = '' # 性別
        self.__load = '' # 斤量
        self.__jockey = '' # 騎手名
        self.__jockey_handi = '' # 騎手減量
        self.__win_odds = '' # 単勝
        self.__popular = '' # 人気
        self.__weight = '' # 馬体重
        self.__weight_change = '' # 馬体重増減
        self.__trainer = '' # 調教師名
        self.__trainer_belong = '' # 調教師所属(美浦/栗東)
        self.__owner = '' # 馬主名

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
    def frame_num(self): return self.__frame_num
    @property
    def horse_num(self): return self.__horse_num
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
    @frame_num.setter
    def frame_num(self, frame_num): self.__frame_num = frame_num
    @horse_num.setter
    def horse_num(self, horse_num): self.__horse_num = horse_num
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
        self.__horse_num = '' # 馬番(複合PK)
        self.__rank = '' # 着順
        self.__goal_time = '' # タイム
        self.__diff_distance = '' # 着差

    # getter
    @property
    def horse_num(self): return self.__horse_num
    @property
    def rank(self): return self.__rank
    @property
    def goal_time(self): return self.__goal_time
    @property
    def diff_distance(self): return self.__diff_distance

    # setter
    @horse_num.setter
    def horse_num(self, horse_num): self.__horse_num = horse_num
    @rank.setter
    def rank(self, rank): self.__rank = rank
    @goal_time.setter
    def goal_time(self, goal_time): self.__goal_time = goal_time
    @diff_distance.setter
    def diff_distance(self, diff_distance): self.__diff_distance = diff_distance

if __name__ == '__main__':
    HTML = html()
    print(Table(1))
    exit()
    ci = CommonInfo()
    ri = RaceInfo()
    rr = RaceResult()
    hi = HorseInfo()
    hr = HorseResult()
    get_param()