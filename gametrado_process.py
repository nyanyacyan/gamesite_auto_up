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
from auto_login.autologin_subclass.shops import Gametrade
from site_operations.sub_shops import OpGametrade

# ----------------------------------------------------------------------------------
# gui作成時にはinitにIDとPasswordを追加して渡せるようにする

class GametradeProcess:
    def __init__(self, main_url, debug_mode=False):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
        chrome_options.add_argument("--window-size=1000,800")  # ウィンドウサイズの指定
        chrome_options.add_extension('data/uBlock-Origin.crx')  # iframe対策の広告ブロッカー
        service = Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(service=service, options=chrome_options)

        # 現在のURLを示すメソッドを定義
        self.current_url = self.chrome.current_url


        self.logger = self.setup_logger(debug_mode=debug_mode)

        # #! GUIで呼び出すときに必要な引数
        # self.login_url = login_url
        # self.userid = userid
        # self.password = password


        #! テストするインスタンス生成
        self.site_operations = OpGametrade(main_url)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
#? ここにカプセル化した内容をいれる

    async def _process(self):
        self.logger.info(" スクレイピング 開始")
        self.logger.debug("サイトを開いてます。")
        self.chrome.get(self.login_url)

        current_url = self.chrome.current_url
        self.logger.debug(f"URL: {current_url}")
        time.sleep(1)

        self.logger.info(f"{self.site_name} Cookie作成を開始")
        self.chrome.get(self.login_url)

        # 現在のURL
        self.logger.debug(f"{self.site_name} URL: {self.current_url}")


        #! ここからインスタンスを入れていく
        await self.get_cookie.getOrElse()
        await self.site_operations.OpGetOrElse()

        self.logger.info(" 処理 完了")

        self.chrome.quit()


# ----------------------------------------------------------------------------------