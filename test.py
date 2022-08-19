import re
code = '''class CommonInfo():
    def __init__(self):
        self.__race_date = '' # レース開催日
        self.__race_num = '' # レース番号
        self.__baba_code = '' # 競馬場コード

# レース情報(発走前)
class RaceInfo():
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

class RaceResult():
    def __init__(self):
        self.__corner_rank = [] # コーナー通過順(馬番)
        self.__pace = [] # 先頭馬のペース(秒)

class HorseInfo():
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

class HorseResult():
    def __init__(self):
        self.__horse_num = '' # 馬番(複合PK)
        self.__rank = '' # 着順
        self.__goal_time = '' # タイム
        self.__diff_distance = '' # 着'''

code2 = code

while True:
    if not '\n' in code:
        break

    border = code.find('\n')
    cutout = code[: border+1]
    code = code[border +1:]
    m = re.search(r'self\.__(.+) =', cutout)
    if m != None:
        param = m.groups()[0]
        print(f'    @property\n    def {param}(self): return self.__{param}')

code = code2

while True:
    if not '\n' in code:
        break

    border = code.find('\n')
    cutout = code[: border+1]
    code = code[border +1:]
    m = re.search(r'self\.__(.+) =', cutout)
    if m != None:
        param = m.groups()[0]
        print(f'    @{param}.setter\n    def {param}(self, {param}): self.__{param} = {param}')
