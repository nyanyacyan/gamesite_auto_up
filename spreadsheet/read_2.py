# coding: utf-8
# ----------------------------------------------------------------------------------
# スプシからデータを読み込むクラス（リンクを知ってる全員がアクセスできる）

# 2023/3/21制作
# ----------------------------------------------------------------------------------
import os
import requests
import pandas as pd
import io
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 自作モジュール
from logger.debug_logger import Logger


load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")


# ----------------------------------------------------------------------------------
class SpreadsheetReader:
    def __init__(self, sheet_url):
        self.sheet_url = sheet_url

        # pandasでの解析までが終わってる状態を作り出してる
        # initにいれることによって即時動かすことができる
        self.df = self.load_spreadsheet()


# ----------------------------------------------------------------------------------


    def load_spreadsheet(self):
        # スプシデータにアクセス
        spreadsheet = requests.get(self.sheet_url)

        # pandasによってCSVを読み取る
        # バイナリデータをutf-8に変換する
        # on_bad_lines='skip'→パラメータに'skip'を指定することで、不正な形式スキップして表示できる（絵文字、特殊文字）
        # StringIOは、文字列データをファイルのように扱えるようにするもの。メモリ上に仮想的なテキストファイルを作成する
        # .set_index('account')これによってIndexを'account'に設定できる。
        string_data = spreadsheet.content.decode('utf-8')
        data_io = io.StringIO(string_data)

        df = pd.read_csv(data_io, on_bad_lines='skip')
        return df.set_index('account')


# ----------------------------------------------------------------------------------


class Read(SpreadsheetReader):
    def __init__(self, sheet_url, account_id, debug_mode=False):

        # super().__init__(sheet_url)→親クラスから引き継いだ引数
        super().__init__(sheet_url)
        self.account_id = account_id
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.setup_chrome()


# ----------------------------------------------------------------------------------
# Loggerセットアップ(要初期化)

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# Chromeセットアップ（動かす箇所にしか配置しない）(要初期化)

    def setup_chrome(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
            chrome_options.add_argument("--window-size=1000,800")  # ウィンドウサイズの指定
            # chrome_options.add_extension('data/uBlock-Origin.crx')  # iframe対策の広告ブロッカー
            service = Service(ChromeDriverManager().install())
            self.chrome = webdriver.Chrome(service=service, options=chrome_options)
            self.current_url = self.chrome.current_url

        except WebDriverException as e:
            self.logger.error(f"webdriverでのエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# 共通の型を作成 →必要要素を引数にいれる

    def get_item_detail(self, detail_type):
        item_detail = self.df.loc[self.account_id, detail_type]
        self.logger.debug(f"{detail_type}: {item_detail}")
        return item_detail


# ----------------------------------------------------------------------------------
# 商品タイトル部分を取得

    def get_item_title(self):
        return self.get_item_detail('title')


# ----------------------------------------------------------------------------------
# 商品説明部分を取得

    def get_item_text(self):
        return self.get_item_detail('text')


# ----------------------------------------------------------------------------------
# 商品価格部分を取得

    def get_item_price(self):
        return self.get_item_detail('price')


# ----------------------------------------------------------------------------------