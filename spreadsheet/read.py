# coding: utf-8
# ----------------------------------------------------------------------------------
# スプシからデータを読み込むクラス（リンクを知ってる全員がアクセスできる）
#! 非同期処理

# 2023/3/21制作
# ----------------------------------------------------------------------------------
import asyncio
import functools
import os
import pickle
import time
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        InvalidSelectorException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# 自作モジュール
from logger.debug_logger import Logger


load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")


# ----------------------------------------------------------------------------------


class Read:
    def __init__(self, sheet_url, account_id, debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)

        # Chromeセットアップ（動かす箇所にしか配置しない）
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
        chrome_options.add_argument("--window-size=1000,800")  # ウィンドウサイズの指定
        # chrome_options.add_extension('data/uBlock-Origin.crx')  # iframe対策の広告ブロッカー
        service = Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(service=service, options=chrome_options)

        # 現在のURLを示すメソッドを定義
        self.current_url = self.chrome.current_url

        self.sheet_url = sheet_url
        self.account_id = account_id


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# 商品タイトル部分を取得

    def get_item_title(self):
        # スプシアクセス
        spreadsheet = requests.get(self.sheet_url)
        print(self.sheet_url)
        print(self.account_id)

        # スプシをCSVにてダウンロード
        with open('data/spreadsheet.csv', 'w', encoding='utf-8') as f:
            f.write(spreadsheet.content.decode('utf-8'))

        # DataFrame作成
        df = pd.read_csv("data/spreadsheet.csv", on_bad_lines='skip', index_col='account')

        item_title = df.loc[self.account_id, 'title']

        self.logger.debug(f"item_title: {item_title}")

        return item_title


# ----------------------------------------------------------------------------------
# 商品説明部分を取得

    def get_item_text(self):
        # スプシアクセス
        spreadsheet = requests.get(self.sheet_url)

        # スプシをCSVにてダウンロード
        with open('data/spreadsheet.csv', 'w', encoding='utf-8') as f:
            f.write(spreadsheet.content.decode('utf-8'))


        # DataFrame作成
        df = pd.read_csv("data/spreadsheet.csv", on_bad_lines='skip', index_col='account')

        item_text = df.loc[self.account_id,'text']

        self.logger.debug(f"item_title: {item_text}")

        return item_text