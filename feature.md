memo
* 数をあらわすときはnum、番号をあらわすときはno
* 賞金関連はprize
* 馬体重はweight、斤量はload

| 論理名 | 物理名 | テーブル | 型 | 必須 | バリデート | カテゴリ | 備考|
| ----: | ----: | ----: | ----: | ----: | ----: | ----: | ----: |
| レース開催日 | race_date |  | DATE | o |  |  |  |
| レース番号 | race_no |  | TINYINT | o |  |  |  |
| 競馬場コード | baba_code |  | TINYINT | o |  |  |  |
| レース名 | race_name |  | VARCHAR | o |  |  |  |
| レース形態 | race_type |  | ENUM | o | - | 平：平地<br>障：障害 |  |
| 馬場 | baba |  | ENUM | o | - | 芝：芝<br>ダ：ダート<br>芝ダ：芝&ダート | 芝ダは障害のみ |
| 天候 | wheather |  | ENUM | o | - | 晴：晴れ<br>曇：曇り<br>小雨：小雨<br>雨：雨<br>小雪：小雪<br>雪：雪 |  |
| 馬場状態(芝) | glass_condition |  | ENUM | - | - | 良：良<br>稍：稍重<br>重：重<br>不：不良 |  |
| 馬場状態(ダ) | dirt_condition |  | ENUM | - | - | 良：良<br>稍：稍重<br>重：重<br>不：不良 |  |
| 距離 | distance |  | SMALLINT | o | ? | - |  |
| 回り | around |  | ENUM | - |  |  |  |
| 使用コース | in_out |  | VARCHAR | - |  |  |  |
| 発走時刻 | race_time |  | TIME | o |  |  |  |
| 開催回 | hold_no |  | TINYINT | o |  |  |  |
| 開催日 | hold_date |  | TINYINT | o |  |  |  |
| クラス | race_class |  | ENUM | o | - | 新馬<br>未勝利<br>500万下<br>1000万下<br>1600万下<br>1勝<br>2勝<br>3勝<br>オープン |  |
| グレード | grade |  | VARCHAR | - | - | GI<br>GII<br>GIII<br>重賞<br>OP<br>1600万下<br>1000万下<br>900万下<br>500万下<br>JGI<br>JGII<br>JGIII<br>L<br>3勝<br>2勝<br>1勝 | 新馬・未勝利はNULL |
| 出走条件(馬齢) | require_age |  | ENUM | o | - | 2歳<br>3歳<br>3歳以上<br>4歳以上 |  |
| 出走条件(性別) | require_gender |  | ENUM | - | - | NULL：制限なし<br>牝：牝馬限定<br>牡牝：騙馬以外 |  |
| 九州産馬限定戦フラグ | require_kyushu |  | BOOL | o | - | - |  |
| 見習騎手限定戦フラグ | require_beginner_jockey |  | BOOL | o | - | - |  |
| 出走条件(国籍)| require_country |  |  | - |  |  |  |
| 出走条件(地方) | require_local |  |  | - |  |  |  |
| 斤量条件 | load_kind |  | ENUM | o | - | 定量<br>馬齢<br>別定<br>ハンデ |  |
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
