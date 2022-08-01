import pandas as pd
import package
import re
import json
import sys
import time
import traceback
from common import babacodechange, logger, jst, output, soup, line
from datetime import datetime
from tqdm import tqdm

class SearchRace():
    '''netkeibaのサイトから地方競馬のレース情報を取得する
    Instance Parameter:
        latest_date(str) : 取得対象の最も新しい日付(yyyyMMdd)
                          デフォルト : システム稼働日前日
        oldest_date(str) : 取得対象の最も古い日付(yyyyMMdd)
                          デフォルト : 20070728(閲覧可能な最古の日付)
        date(list<str>) : 取得対象の日付(yyyyMMdd)
        url(URL) : netkeibaサイト内のURL一覧
        output_type(str) : 出力ファイルを分割
                           m : 月ごと(デフォルト)、y : 年ごと、a : 全ファイルまとめて
    '''

    def __init__(self, oldest_date = '20070728', latest_date = jst.yesterday(), output_type = 'm'):
        self.__latest_date = latest_date
        self.__oldest_date = oldest_date
        self.validation_check()
        self.__url = URL()
        self.__output_type = output_type
        logger.info(f'取得対象最古日:{jst.change_format(self.oldest_date, "%Y%m%d", "%Y/%m/%d")}')
        logger.info(f'取得対象最新日:{jst.change_format(self.latest_date, "%Y%m%d", "%Y/%m/%d")} で処理を行います')
        print(f'取得対象最古日:{jst.change_format(self.oldest_date, "%Y%m%d", "%Y/%m/%d")}')
        print(f'取得対象最新日:{jst.change_format(self.latest_date, "%Y%m%d", "%Y/%m/%d")} で処理を行います')

    @property
    def latest_date(self): return self.__latest_date
    @property
    def oldest_date(self): return self.__oldest_date
    @property
    def url(self): return self.__url
    @property
    def output_type(self): return self.__output_type
    @latest_date.setter
    def latest_date(self, latest_date): self.__latest_date = latest_date
    @oldest_date.setter
    def oldest_date(self, oldest_date): self.__oldest_date = oldest_date

    def validation_check(self):
        '''日付の妥当性チェックを行う'''
        logger.info('日付のバリデーションチェック開始')

        # 日付フォーマットチェック
        try:
            tmp = datetime.strptime(self.oldest_date, '%Y%m%d')
        except:
            logger.warning('取得対象最古日の値が不正です')
            logger.warning(f'取得対象最古日:{self.oldest_date}→2007/07/28 に変更します')
            self.oldest_date = '20070728'

        try:
            tmp = datetime.strptime(self.latest_date, '%Y%m%d')
        except:
            logger.warning('取得対象最新日の値が不正です')
            logger.warning(f'取得対象最新日:{self.latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.latest_date = jst.yesterday()

        # 日付妥当性チェック
        if self.oldest_date < '20070728':
            logger.warning('取得対象最古日の値が2007/07/28より前になっています')
            logger.warning('2007/07/28以前のオッズデータはnetkeibaサイト内に存在しないため取得できません')
            logger.warning(f'取得対象最古日:{self.oldest_date}→2007/07/28に変更します')
            self.oldest_date = jst.yesterday()
        elif self.oldest_date == jst.date():
            logger.warning('エラーを起こす可能性が高いため本日のレースは取得できません')
            logger.warning(f'取得対象最古日:{self.oldest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.oldest_date = jst.yesterday()
        elif self.oldest_date > jst.date():
            logger.warning('取得対象最古日の値が未来になっています')
            logger.warning(f'取得対象最古日:{self.oldest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.oldest_date = jst.yesterday()

        if self.latest_date == jst.date():
            logger.warning('エラーを起こす可能性が高いため本日のレースは取得できません')
            logger.warning(f'取得対象最新日:{self.latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.latest_date = jst.yesterday()
        elif self.latest_date > jst.date():
            logger.warning('取得対象最新日の値が未来になっています')
            logger.warning(f'取得対象最新日:{self.latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.latest_date = jst.yesterday()

        if self.latest_date < self.oldest_date:
            logger.warning('取得対象最古日と最新日の記載順が逆のため入れ替えて処理を行います')
            tmp = self.latest_date
            self.latest_date = self.oldest_date
            self.oldest_date = tmp

        logger.info('日付のバリデーションチェック終了')

    def get_dates(self):
        '''取得対象日の取得を行う'''

        # 対象日格納用
        target_dates = []

        # 対象最新日の月から順に検索していく
        month = self.latest_date[:6]

        # 対象最古日より前の月になるまでループ
        while month >= self.oldest_date[:6]:
            logger.info(f'{jst.change_format(month, "%Y%m", "%Y/%m")}のレース開催日を取得します')
            print(f'{jst.change_format(month, "%Y%m", "%Y/%m")}のレース開催日を取得します')

            # HTMLタグ取得
            html = soup.get_soup(f'{self.url.RESULTS}{month}01')

            # 開催カレンダーの取得
            calendar = html.find('table')

            # 開催日のリンクがある日付を抽出
            dates = re.finditer(r'/race/list/(\d+)/', str(calendar))

            # 降順にするためリストに変換
            date_list = [m.groups()[0] for m in dates]
            date_list.reverse()

            # 期間内だったらリストに追加
            for date in date_list:
                if self.oldest_date <= date <= self.latest_date:
                    target_dates.append(date)

            # 月をひとつ前に戻す
            if month[4:] == '01':
                month = str(int(month) - 89)
            else:
                month = str(int(month) - 1)

        return target_dates

    def get_race_url(self, date):
        '''指定した日に開催される競馬場のURLを取得する'''
        # HTMLタグ取得
        html = soup.get_soup(f'{self.url.RESULTS}{date}')

        # レース一覧記載枠の箇所を抽出
        race_frame = html.find('div', class_ = 'race_kaisai_info')

        # レースへのリンクをすべて取得
        races = re.finditer(r'/race/(\d+)/', str(race_frame))

        # リストに変換して返す
        return [m.groups()[0] for m in races]

    def error_output(self, message, e, stacktrace):
        '''エラー時のログ出力/LINE通知を行う
        Args:
            message(str) : エラーメッセージ
            e(str) : エラー名
            stacktrace(str) : スタックトレース
        '''
        logger.error(message)
        logger.error(e)
        logger.error(stacktrace)
        line.send(message)
        line.send(e)
        line.send(stacktrace)

class ResultRace(SearchRace):
    '''netkeibaのサイトから過去の中央競馬のレース結果データを取得する
    '''

    def __init__(self, argv0 = None, argv1 = None, argv2 = None):
        logger.info('----------------------------')
        logger.info('中央競馬レース結果取得システム起動')
        line.send('中央競馬レース結果取得システム起動')
        logger.info('初期処理開始')
        super().__init__(argv0, argv1, argv2)
        self.main()
        logger.info('中央競馬レース結果取得システム終了')
        line.send('中央競馬レース結果取得システム終了')

    def main(self):
        '''主処理、各メソッドの呼び出し'''

        # 対象の日付リストの取得
        dates = self.get_dates()

        logger.info(f'取得対象日数は{len(dates)}日です')
        print(f'取得対象日数は{len(dates)}日です')

        # レースのある日を1日ずつ遡って取得処理を行う
        for date in tqdm(dates):

            logger.info(f'{jst.change_format(date, "%Y%m%d", "%Y/%m/%d")}のレース結果の取得を開始します')

            try:
                # 指定日に行われる全レースのレースIDの取得
                race_ids = self.get_race_url(date)
            except Exception as e:
                self.error_output('レースURL取得処理でエラー', e, traceback.format_exc())
                exit()

            for race_id in race_ids:

                try:
                    # レース情報/レース結果テーブルの取得
                    result = self.get_result(race_id)

                    # DataFrame型(=正常レスポンス)でない場合は何もしない
                    if type(result) == bool:
                        continue

                except Exception as e:
                    self.error_output('レース結果取得処理でエラー', e, traceback.format_exc())
                    exit()

                try:
                    # レースデータの加工/CSV出力
                    self.record_result(date, result)
                except Exception as e:
                    self.error_output('テーブルデータの加工/出力処理でエラー', e, traceback.format_exc())
                    exit()

                time.sleep(3)

    def get_result(self, race_id):
        '''レース番号からレース情報・結果をスクレイピング
        Args:
            race_id(str):レース番号。10桁(西暦+開催回+開催日+競馬場コード)
        Returns:
            df(pandas.DataFrame):レース情報と各馬の情報・結果をもったデータ
        '''

        logger.info(f'{babacodechange.netkeiba(race_id[4:6])}{race_id[10:]}Rのレース結果を取得します')

        # レース結果のURLからHTMLデータをスクレイピング
        result_url = f'{URL.RACE}{race_id}'

        print(race_id)
        print(result_url)

        df = pd.read_html(result_url)[0]
        #html = soup.get_soup(result_url)

        print(df)
        print('-----------')
        #print(html)
        exit()

        # TODO データ加工

        # return df

    def record_result(self, date, race_id, result):
        '''レース結果にレース情報を付加して出力する'''

        # レース情報を頭数分用意する
        info = [[date, race_id[4:6], race_id[10:]] for _ in range(len(result))]

        write_df = pd.concat([pd.DataFrame(info, index = result.index), pd.DataFrame(result.index, index = result.index), result], axis=1)

        write_df.columns = ['発走日', '競馬場コード', 'レース番号', '馬番', '単勝オッズ', '複勝オッズ下限', '複勝オッズ上限']

        # CSVに出力
        if self.output_type == 'a':
            # 一つのファイルに出力
            output.csv(write_df, 'jra_raceresult')
        elif self.output_type == 'y':
            # 年ごとにファイルを分割
            output.csv(write_df, f'jra_raceresult_{date[:4]}')
        else:
            # 月ごとにファイルを分割
            output.csv(write_df, f'jra_raceresult{date[:6]}')

class ResultOdds(SearchRace):
    '''netkeibaのサイトから中央競馬の最終オッズを取得する
    '''

    def __init__(self, argv0 = None, argv1 = None, argv2 = None):
        logger.info('----------------------------')
        logger.info('中央競馬過去オッズ取得システム起動')
        line.send('中央競馬過去オッズ取得システム起動')
        logger.info('初期処理開始')
        super().__init__(argv0, argv1, argv2)
        self.main()
        logger.info('中央競馬過去オッズ取得システム終了')
        line.send('中央競馬過去オッズ取得システム終了')


    def main(self):
        '''主処理、各メソッドの呼び出し'''

        # 対象の日付リストの取得
        dates = self.get_dates()

        logger.info(f'取得対象日数は{len(dates)}日です')
        print(f'取得対象日数は{len(dates)}日です')

        # レースのある日を1日ずつ遡って取得処理を行う
        for date in tqdm(dates):

            logger.info(f'{jst.change_format(date, "%Y%m%d", "%Y/%m/%d")}のオッズデータの取得を開始します')

            try:
                # 指定日に行われる全レースのレースIDの取得
                race_ids = self.get_race_url(date)
            except Exception as e:
                self.error_output('レースURL取得処理でエラー', e, traceback.format_exc())
                exit()

            for race_id in race_ids:

                try:
                    # オッズテーブルの取得
                    odds_table = self.get_odds(race_id)

                    # DataFrame型(=正常レスポンス)でない場合は何もしない
                    if type(odds_table) == bool:
                        continue

                except Exception as e:
                    self.error_output('オッズテーブル取得処理でエラー', e, traceback.format_exc())
                    exit()

                try:
                    # テーブルデータの加工/CSV出力
                    self.record_odds(date, race_id, odds_table)
                except Exception as e:
                    self.error_output('テーブルデータの処理でエラー', e, traceback.format_exc())
                    exit()

                time.sleep(3)

    def get_odds(self, race_id):
        '''APIから単勝・複勝オッズのデータ(JSON)を取得する'''

        logger.info(f'{babacodechange.netkeiba(race_id[4:6])}{race_id[10:]}Rのオッズデータを取得します')

        # APIからJSON取得
        html = soup.get_soup(f'{self.url.TANPUKU}{race_id}')
        json_data = json.loads(html.text)

        # レスポンスが正しく返ってきたかのチェック
        if json_data['reason'] == '':
            try:
                # JSONから必要なカラムを切り出し
                df = pd.concat([pd.DataFrame(json_data['data']['odds']['1']).T, pd.DataFrame(json_data['data']['odds']['2']).T], axis = 1)
            except:
                # netkeiba側のJSONがおかしい場合があるのでそれのリカバリ処理
                logger.warning('オッズ取得処理にて正常でないJSONのレスポンスを取得')
                return False
            df = df.iloc[:,[0, 3, 4]]
            df.columns = ['単勝', '複勝下限', '複勝上限']

            return df
        elif json_data['reason'] == 'result odds empty':
            logger.warning('オッズ取得処理にて空のレスポンスを取得')
            return False
        else:
            logger.warning('オッズ取得処理にて空レスポンス以外のエラー')
            return False

    def record_odds(self, date, race_id, odds):
        '''オッズデータにレース情報を付加して出力する'''

        # レース情報を頭数分用意する
        info = [[date, race_id[4:6], race_id[10:]] for _ in range(len(odds))]

        write_df = pd.concat([pd.DataFrame(info, index = odds.index), pd.DataFrame(odds.index, index = odds.index), odds], axis=1)

        write_df.columns = ['発走日', '競馬場コード', 'レース番号', '馬番', '単勝オッズ', '複勝オッズ下限', '複勝オッズ上限']

        # CSVに出力
        if self.output_type == 'a':
            # 一つのファイルに出力
            output.csv(write_df, 'jra_resultodds')
        elif self.output_type == 'y':
            # 年ごとにファイルを分割
            output.csv(write_df, f'jra_resultodds_{date[:4]}')
        else:
            # 月ごとにファイルを分割
            output.csv(write_df, f'jra_resultodds_{date[:6]}')

class URL():
    '''netkeibaの各ページのURL'''
    # レースリンク一覧
    RESULTS = 'https://db.netkeiba.com/race/list/'
    # レース情報
    RACE = 'https://db.netkeiba.com/race/'
    # 単複オッズAPI
    TANPUKU = 'https://race.netkeiba.com/api/api_get_jra_odds.html?type=1&race_id='


class Common():
    def __init__(self):
        pass
  * レース開催日
  * レース番号
  * 競馬場

* レース情報(発走前)
class RaceInfo():
    def __init__(self):
        # レース名
        self.race_name = ''
        # 馬場
        self.baba = ''
        # 天候
        self.weather = ''
        # 馬場状態
        self.baba_status = ''
        # 距離
        self.distance = ''
        # 回り(右/左)
        self.around = ''
        # 回り(内/外)
        self.in_out = ''
        # 発走時刻
        self.race_time = ''
        # 開催回
        self.hold_num = ''
        # 開催日
        self.hold_date = ''
        # 格・グレード
        self.grade = ''
        # 出走条件(年齢)
        self.require_age = ''
        # 出走条件(性別)
        self.require_gender = ''
        # 出走条件(国内/国際/混合)
        self.require_country = ''
        # 出走条件(特別指定/指定/他)
        self.require_local = ''
        # 斤量条件(定量/賞金別定/重賞別定/ハンデ)
        self.load_kind = ''
        # 1着賞金 TODO 同着時チェック
        self.first_prize = ''
        # 2着賞金
        self.second_prize = ''
        # 3着賞金
        self.third_prize = ''
        # 4着賞金
        self.fourth_prize = ''
        # 5着賞金
        self.fifth_prize = ''
        # 出走頭数
        self.horse_num = ''

* レース情報(発走後)
class RaceResult():
    def __init__(self):
        # コーナー通過順(馬番)
        self.corner_rank = []
        # ペース(秒)
        self.pace = []

* 馬情報(発走前)
class HorseInfo():
    def __init__(self):
        pass
  * 枠番
  * 馬番 (複合PK)
  * 馬名
  * 馬齢
  * 性別
  * 斤量
  * 騎手
  * 単勝
  * 人気
  * 馬体重
  * 馬体重増減
  * 調教師所属(関東/関西)
  * 調教師名
  * 馬主名
--馬柱から
  * レース間隔
  * 父名
  * 母名
  * 母父名
  * 脚質?
  * 生産(国内/海外)
  * 所属(地方/中央)
  * ブリンカー(有/無)
  * 毛色

*  出走馬情報(発走後)
class HorseResult():
    def __init__(self):
        # 馬番(複合PK)
        self.horse_num = ''
        # 着順
        self.rank = ''
        # タイム
        self.goal_time = ''
        # 着差
        self.diff_distance = ''

if __name__ == '__main__':
    # ログ用インスタンス作成
    # プログレスバーを出すためコンソールには出力しない
    logger = logger.Logger(0)

    # 初期処理
    try:
        if len(sys.argv) >= 4:
            ro = ResultOdds(sys.argv[1], sys.argv[2], sys.argv[3])
        elif len(sys.argv) >= 3:
            ro = ResultOdds(sys.argv[1], sys.argv[2])
        elif len(sys.argv) == 2:
            ro = ResultOdds(sys.argv[1])
        else:
            ro = ResultOdds()
    except Exception as e:
        logger.error('初期処理でエラー')
        logger.error(e)
        logger.error(traceback.format_exc())
        line.send('初期処理でエラー')
        line.send(e)
        line.send(traceback.format_exc())
        raise
