memo
* 数をあらわすときはnum、番号をあらわすときはno
* 賞金関連はprize
* 馬体重はweight、斤量はload

| 論理名 | 物理名 | テーブル | 型 | 必須 | バリデート | カテゴリ | 備考|
| ----: | ----: | ----: | ----: | ----: | ----: | ----: | ----: |
| レース開催日 | race_date |  | D | o |  |  |  |
| レース番号 | race_no |  | T | o |  |  |  |
| 競馬場コード | baba_code |  | T | o |  |  |  |
| レース名 | race_name |  | V | o |  |  |  |
| レース形態 | race_type |  | E | o |  |  |  |
| 馬場 | baba |  | E | o |  |  |  |
| 天候 | wheather |  | E | o |  |  |  |
| 馬場状態(芝) | glass_condition |  | E | - |  |  |  |
| 馬場状態(ダ) | dirt_condition |  | E | - |  |  |  |
| 距離 | distance |  | S | o |  |  |  |
| 回り | around |  | E | - |  |  |  |
| 使用コース | in_out |  | V | - |  |  |  |
| 発走時刻 | race_time |  | TIME | o |  |  |  |
| 開催回 | hold_no |  | T | o |  |  |  |
| 開催日 | hold_date |  | T | o |  |  |  |
| クラス | race_class |  |  | o |  |  |  |
| グレード | grade |  |  | - |  |  |  |
| 出走条件(馬齢) | require_age |  |  | o |  |  |  |
| 出走条件(性別) | require_gender |  |  | o |  |  |  |
| 九州産馬限定戦フラグ | require_kyushu |  |  |  | o |  |  |
| 見習騎手限定戦フラグ | require_beginner_jockey |  |  | o |  |  |  |
| 出走条件(国籍)| require_country |  |  | - |  |  |  |
| 出走条件(地方) | require_local |  |  | - |  |  |  |
| 斤量条件 | load_kind |  |  | o |  |  |  |
| 1着賞金 | first_prize |  |  | o |  |  |  |
| 2着賞金 | second_prize |  |  | o |  |  |  |
| 3着賞金 | third_prize |  |  | o |  |  |  |
| 4着賞金 | fourth_prize |  |  | o |  |  |  |
| 5着賞金 | fifth_prize |  |  | o |  |  |  |
| 出走頭数 | horse_num |  |  | o |  |  |  |
| 1コーナー通過順 | corner_rank1 |  |  | - |  |  |  |
| 2コーナー通過順 | corner_rank2 |  |  | - |  |  |  |
| 3コーナー通過順 | corner_rank3 |  |  | - |  |  |  |
| 4コーナー通過順 | corner_rank4 |  |  | - |  |  |  |
| ペース | pace |  |  | o |  |  |  |
| 枠番 | frame_no |  |  | o |  |  |  |
| 馬番 | horse_no |  |  | o |  |  |  |
| 馬名 | horse_name |  |  | o |  |  |  |
| 馬齢 | age |  |  | o |  |  |  |
| 性別 | gender |  |  | o |  |  |  |
| 斤量 | load |  |  | o |  |  |  |
| 騎手名 | jockey |  |  | o |  |  |  |
| 減量騎手 | jockey_handi |  |  | - |  |  |  |
| 単勝オッズ | win_odds |  |  | o |  |  |  |
| 人気 | popular |  |  | o |  |  |  |
| 馬体重 | weight |  |  | - |  |  |  |
| 馬体重増減 | weight_change |  |  | - |  |  |  |
| 調教師名 | trainer |  |  | o |  |  |  |
| 調教師所属 | trainer_belong |  |  | o |  |  |  |
| 馬主名 | owner |  |  | o |  |  |  |
| レース間隔 | blank |  |  | - |  |  |  |
| 父名 | father |  |  | o |  |  |  |
| 母名 | mother |  |  | o |  |  |  |
| 母父名 | groundfather |  |  | o |  |  |  |
| 脚質 | running_type |  |  | o |  |  |  |
| 国籍 | country |  |  | o |  |  |  |
| 所属 | belong |  |  | o |  |  |  |
| ブリンカー | blinker |  |  | o |  |  |  |
| 毛色 | haircolor |  |  | o |  |  |  |
| 着順 | rank |  |  | o |  |  |  |
| 走破タイム | goal_time |  |  | o |  |  |  |
| 着差 | diff |  |  | o |  |  |  |
| 1コーナー通過順 | pass_rank1 |  |  | - |  |  |  |
| 2コーナー通過順 | pass_rank2 |  |  | - |  |  |  |
| 3コーナー通過順 | pass_rank3 |  |  | - |  |  |  |
| 4コーナー通過順 | pass_rank4 |  |  | - |  |  |  |
| 上がり3F | agari |  |  | o |  |  |  |
| 賞金 | prize |  |  | o |  |  |  |
