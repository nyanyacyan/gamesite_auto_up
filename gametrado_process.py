# coding: utf-8
# ----------------------------------------------------------------------------------
#? Process集計クラス
# 基本はカプセル化したものを使う。
# GUIがある場合には引数にいれるものは引数に入れて渡す
# ----------------------------------------------------------------------------------
import os
import time
import asyncio

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# 自作モジュール
from logger.debug_logger import Logger
from site_operations.sub_shops import OpGametrade

# 拡張機能の絶対path
script_dir = os.path.dirname(os.path.abspath(__file__))
security_path = os.path.join(script_dir, 'data', 'uBlock-Origin.crx')
cap_path = os.path.join(script_dir, 'data', 'hlifkpholllijblknnmbfagnkjneagid.crx')

# ----------------------------------------------------------------------------------
# gui作成時にはinitにIDとPasswordを追加して渡せるようにする

class GametradeProcess:
    def __init__(self, main_url, cookies_file_name, image, gametitle, sheet_url, account_id, debug_mode=False):
        self.main_url = main_url
        self.cookies_file_name = cookies_file_name
        self.image = image
        self.sheet_url = sheet_url
        self.account_id = account_id

        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
        chrome_options.add_argument("--window-size=1200,1000")  # ウィンドウサイズの指定
        chrome_options.add_extension(security_path)  # iframe対策の広告ブロッカー
        chrome_options.add_extension(cap_path)
        service = Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(service=service, options=chrome_options)

        # 現在のURLを示すメソッドを定義
        self.current_url = self.chrome.current_url


        self.logger = self.setup_logger(debug_mode=debug_mode)

        # #! GUIで呼び出すときに必要な引数
        # self.main_url = main_url
        # self.userid = userid
        # self.password = password


        #! テストするインスタンス生成
        self.site_operations = OpGametrade(self.chrome,main_url, cookies_file_name, image, gametitle, sheet_url, account_id)



# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
#? ここにカプセル化した内容をいれる

    async def process(self):
        self.logger.info(" スクレイピング 開始")
        self.logger.debug("サイトを開いてます。")
        self.chrome.get(self.main_url)

        current_url = self.chrome.current_url
        self.logger.debug(f"URL: {current_url}")
        time.sleep(1)

        # 現在のURL
        self.logger.debug(f"{__name__} URL: {self.current_url}")


        #! ここからインスタンスを入れていく
        await self.site_operations.OpGetOrElse()

        self.logger.info(" 処理 完了")

        self.chrome.quit()


# ----------------------------------------------------------------------------------
#? ここにカプセル化した内容をいれる

    async def agency_process(self):
        self.logger.info(" スクレイピング 開始")
        self.logger.debug("サイトを開いてます。")
        self.chrome.get(self.main_url)

        current_url = self.chrome.current_url
        self.logger.debug(f"URL: {current_url}")
        time.sleep(1)

        # 現在のURL
        self.logger.debug(f"{__name__} URL: {self.current_url}")


        #! ここからインスタンスを入れていく
        await self.site_operations.AgencyOpGetOrElse()

        self.logger.info(" 処理 完了")

        self.chrome.quit()


# ----------------------------------------------------------------------------------
