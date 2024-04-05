# coding: utf-8
# ----------------------------------------------------------------------------------
#? Process集計クラス
# 基本はカプセル化したものを使う。
# GUIがある場合には引数にいれるものは引数に入れて渡す
# ----------------------------------------------------------------------------------
import os
import time
import requests
from datetime import datetime


import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

# 自作モジュール
from logger.debug_logger import Logger
from site_operations.sub_shops import OpGametrade

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")

# 拡張機能の絶対path
script_dir = os.path.dirname(os.path.abspath(__file__))
security_path = os.path.join(script_dir, 'data', 'uBlock-Origin.crx')
cap_path = os.path.join(script_dir, 'data', 'hlifkpholllijblknnmbfagnkjneagid.crx')

# ----------------------------------------------------------------------------------
# gui作成時にはinitにIDとPasswordを追加して渡せるようにする

class GametradeProcess:
    def __init__(self, main_url, cookies_file_name, image, sheet_url, account_id, debug_mode=False):
        self.main_url = main_url
        self.cookies_file_name = cookies_file_name
        self.image = image
        self.sheet_url = sheet_url
        self.account_id = account_id

        # 現在のURLを示すメソッドを定義
        self.setup_chrome()
        self.current_url = self.chrome.current_url


        self.logger = self.setup_logger(debug_mode=debug_mode)

        #! テストするインスタンス生成
        self.site_operations = OpGametrade(self.chrome,main_url, cookies_file_name, image, sheet_url, account_id)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

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
            chrome_options.add_argument("--window-size=1200,1000")  # ウィンドウサイズの指定
            chrome_options.add_extension(security_path)  # iframe対策の広告ブロッカー
            chrome_options.add_extension(cap_path)
            service = Service(ChromeDriverManager().install())
            self.chrome = webdriver.Chrome(service=service, options=chrome_options)
            self.current_url = self.chrome.current_url

        except WebDriverException as e:
            self.logger.error(f"webdriverでのエラーが発生: {e}")
            self.error_screenshot_discord(
                "【エラー】webdriverが実行されなかった",
                str(e),
                "【エラー】webdriverが実行されなかった"
            )


# ----------------------------------------------------------------------------------
# infoスクショセットアップ

    def info_screenshot_discord(self, comment, info_message):
        # スクショ用のタイムスタンプ
        timestamp = datetime.now().strftime("%m-%d_%H-%M")

        filename = f"lister_page_{timestamp}.png"

        # 絶対path
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # 現在のスクリプトの親ディレクトリのパス
        parent_dir = os.path.dirname(script_dir)

        # スクショ保管場所の絶対path
        screenshot_dir = os.path.join(parent_dir, 'DebugScreenshot/')

        full_path = os.path.join(screenshot_dir, filename)


        # スクリーンショットを保存
        screenshot_saved = self.chrome.save_screenshot(full_path)
        if screenshot_saved:
            self.logger.debug(f"スクリーンショットを保存: {full_path}")

        content = f"【INFO】{comment}"

        with open(full_path, 'rb') as file:
            files = {"file": (full_path, file, "image/png")}
            response = requests.post(self.discord_url, data={"content": content}, files=files)
            print(f"Discordへの通知結果: {response.status_code}")

        print(info_message)


# ----------------------------------------------------------------------------------
# エラー時のスクショ セットアップ

    def error_screenshot_discord(self, comment, error_message):
        # スクショ用のタイムスタンプ
        timestamp = datetime.now().strftime("%m-%d_%H-%M")

        filename = f"lister_page_{timestamp}.png"

        # 絶対path
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # 現在のスクリプトの親ディレクトリのパス
        parent_dir = os.path.dirname(script_dir)

        # スクショ保管場所の絶対path
        screenshot_dir = os.path.join(parent_dir, 'DebugScreenshot/')

        full_path = os.path.join(screenshot_dir, filename)


        # スクリーンショットを保存
        screenshot_saved = self.chrome.save_screenshot(full_path)
        if screenshot_saved:
            self.logger.debug(f"スクリーンショットを保存: {full_path}")

        content = f"【WARNING】{comment}"

        with open(full_path, 'rb') as file:
            files = {"file": (full_path, file, "image/png")}
            response = requests.post(self.discord_url, data={"content": content}, files=files)
            print(f"Discordへの通知結果: {response.status_code}")

        raise Exception(f"{self.account_id} {error_message}")


# ----------------------------------------------------------------------------------
#? ここにカプセル化した内容をいれる

    async def process(self):
        self.logger.info(f"{self.account_id} スクレイピング 開始")
        self.logger.debug(f"{self.account_id}サイトを開いてます。")
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
        self.logger.info(f"{self.account_id} スクレイピング 開始")
        self.logger.debug(f"{self.account_id} サイトを開いてます。")
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
#? ここにカプセル化した内容をいれる

    async def valorant_process(self):
        self.logger.info(f"{self.account_id} スクレイピング 開始")
        self.logger.debug(f"{self.account_id} サイトを開いてます。")
        self.chrome.get(self.main_url)

        current_url = self.chrome.current_url
        self.logger.debug(f"URL: {current_url}")
        time.sleep(1)

        # 現在のURL
        self.logger.debug(f"{__name__} URL: {self.current_url}")


        #! ここからインスタンスを入れていく
        await self.site_operations.valorantOpGetOrElse()

        self.logger.info(" 処理 完了")

        self.chrome.quit()


# ----------------------------------------------------------------------------------