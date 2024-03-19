# coding: utf-8
# ----------------------------------------------------------------------------------
# ! 非同期処理→ まとめて非同期処理へ変換する
# 写真などのファイルをアップロードを実装クラス
# 2023/3/10 制作
# ----------------------------------------------------------------------------------
import asyncio
from datetime import datetime
import functools
import os
import pickle
import time
import requests
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
from auto_login.solve_recaptcha import RecaptchaBreakthrough
from logger.debug_logger import Logger

load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")


# ----------------------------------------------------------------------------------


class FileSelect:
    '''Cookie利用してログインして処理を実行するクラス'''
    def __init__(self, config_fileSelect, debug_mode=False):
        '''config_xpathにパスを集約させて子クラスで引き渡す'''
        self.logger = self.setup_logger(debug_mode=debug_mode)

        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
        chrome_options.add_argument("--window-size=1280,1000")  # ウィンドウサイズの指定

        # ChromeDriverManagerを使用して自動的に適切なChromeDriverをダウンロードし、サービスを設定
        service = Service(ChromeDriverManager().install())

        # WebDriverインスタンスを生成
        self.chrome = webdriver.Chrome(service=service, options=chrome_options)

        # 現在のURLを示すメソッドを定義
        self.current_url = self.chrome.current_url

        # メソッド全体で使えるように定義（デバッグで使用）
        self.site_name = config_fileSelect["site_name"]

        #! 使ってないものは削除する
        # xpath全体で使えるように初期化
        #* 利用してるものconfig_fileSelect
        self.cookies_file_name = config_fileSelect["cookies_file_name"]
        self.main_url = config_fileSelect["main_url"]
        self.lister_btn_xpath = config_fileSelect["lister_btn_xpath"]
        self.photo_select_btn_xpath = config_fileSelect["photo_select_btn_xpath"]
        self.photo_file_input_xpath = config_fileSelect["photo_file_input_xpath"]
        self.photo_file_xpath = config_fileSelect["photo_file_xpath"]


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------


    def photo_upload(self):
        '''ダイアログを介さず、そのままファイルをアップロード'''
        try:
            # fileのアップロードの<input>要素を探す
            self.logger.debug(" fileのアップロードの<input>要素 を捜索開始")
            file_input = self.chrome.find_element_by_xpath(self.photo_file_input_xpath)
            self.logger.debug(" fileのアップロードの<input>要素 を発見")

        except NoSuchElementException as e:
            self.logger.error(f" fileのアップロードの<input>要素 が見つかりません:{e}")

        try:
            self.logger.debug(" self.photo_file_xpath を特定開始")
            file_input.send_keys(self.photo_file_xpath)
            self.logger.debug(" self.photo_file_xpath を特定開始")

        except FileNotFoundError as e:
            self.logger.error(f" photo_file_xpath が見つかりません:{e}")

        time.sleep(1)

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} 次のページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 実行処理中にエラーが発生: {e}")

        #TODO スクリーンショット
        filename = f"DebugScreenshot/photo_select_btnPush_after_{timestamp}.png"
        self.chrome.save_screenshot(filename)

        time.sleep(1)

