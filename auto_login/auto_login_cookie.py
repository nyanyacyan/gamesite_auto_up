# coding: utf-8
# ----------------------------------------------------------------------------------
# 非同期処理 自動ログインクラス
# headlessモード、reCAPTCHA回避
# 2023/3/8制作
# ----------------------------------------------------------------------------------


import asyncio
import datetime
import functools
import os
import pickle
import time
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
from auto_login.autologin_subclass import SolverRecaptcha
from logger.debug_logger import Logger

load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)


# ----------------------------------------------------------------------------------


class NoCookieLogin:
    def __init__(self, config_xpath, debug_mode=False):
        '''config_xpathにパスを集約させて子クラスで引き渡す'''
        # Loggerクラスを初期化
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        self.logger_instance = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.logger_instance.get_logger()
        self.debug_mode = debug_mode

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
        chrome_options.add_argument("--window-size=1680,1200")  # ウィンドウサイズの指定

        # ChromeDriverManagerを使用して自動的に適切なChromeDriverをダウンロードし、サービスを設定
        service = Service(ChromeDriverManager().install())

        # WebDriverインスタンスを生成
        self.chrome = webdriver.Chrome(service=service, options=chrome_options)

        # 現在のURLを示すメソッドを定義
        self.current_url = self.chrome.current_url

        # メソッド全体で使えるように定義
        self.site_name = config_xpath["site_name"]

        # xpath全体で使えるように初期化
        self.login_url = config_xpath["login_url"]
        self.userid = config_xpath["userid"]
        self.password = config_xpath["password"]
        self.userid_xpath = config_xpath["userid_xpath"]
        self.password_xpath = config_xpath["password_xpath"]
        self.login_button_xpath = config_xpath["login_button_xpath"]
        self.login_checkbox_xpath = config_xpath["login_checkbox_xpath"]
        self.user_element_xpath = config_xpath["user_element_xpath"]
        self.cookies_file_name = config_xpath["cookies_file_name"]

        # SolverRecaptchaクラスを初期化
        self.recaptcha_solver = SolverRecaptcha(self.chrome)

# ----------------------------------------------------------------------------------

    # 同期的なログイン
    def open_site(self):
        '''
        Cookieで開かない際に使うメソッド
        '''
        self.logger.info(f"{self.site_name} Cookie作成を開始")
        self.chrome.get(self.login_url)

        # 現在のURL
        self.logger.debug(f"{self.site_name} URL: {self.self.current_url}")



        # userid_xpathが出てくるまで待機
        try:
            WebDriverWait(self.chrome, 10).until(EC.presence_of_element_located((By.XPATH, self.userid_xpath)))
            self.logger.debug(f"{self.site_name} 入力開始")

        except TimeoutException as e:
            print(f"タイムアウトエラー:{e}")


# ----------------------------------------------------------------------------------

    def id_pass_input(self):
        # IDとパスを入力
        try:
            userid_field = self.chrome.find_element_by_xpath(self.userid_xpath)
            userid_field.send_keys(self.userid)
            self.logger.debug(f"{self.site_name} ID入力完了")

            password_field = self.chrome.find_element_by_xpath(self.password_xpath)
            password_field.send_keys(self.password)
            self.logger.debug(f"{self.site_name} パスワード入力完了")

        except NoSuchElementException as e:
            print(f"要素が見つからない: {e}")


        # ページが完全に読み込まれるまで待機
        WebDriverWait(self.chrome, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self.logger.debug("ページは完全に表示されてる")


        WebDriverWait(self.chrome, 10).until(
            EC.visibility_of_element_located((By.XPATH, self.login_button_xpath))
        )
        self.logger.debug(f"{self.site_name} ボタンDOMの読み込みは完了してる")

        time.sleep(1)


# ----------------------------------------------------------------------------------


    def login_checkbox(self):
        '''チェックボックスにチェックいれる'''
        # リファクタリングする
        # ログインを維持するチェックボックスを探す
        try:
            login_checkbox = self.chrome.find_element_by_xpath(self.login_checkbox_xpath)
            self.logger.debug(f"{self.site_name} チェックボタンが見つかりました。")

        except ElementNotInteractableException as e:
            self.logger.error(f"{self.site_name} チェックボックスが見つかりません。{e}")

        except InvalidSelectorException:
            self.logger.debug(f"{self.site_name} チェックボックスないためスキップ")

        try:
            if login_checkbox:
            # remember_boxをクリックする
                login_checkbox.click()
            self.logger.debug(f"{self.site_name} チェックボタンをクリック")

        except UnboundLocalError:
            self.logger.debug(f"{self.site_name} チェックボタンなし")

        time.sleep(1)


# ----------------------------------------------------------------------------------


    def recaptcha_process(self):
        '''reCAPTCHA検知してある場合は2CAPTCHAメソッドを実行'''
        # reCAPTCHA検知
        try:
            # sitekeyを検索
            elements = self.chrome.find_elements_by_css_selector('[data-sitekey]')
            if len(elements) > 0:
                self.logger.info(f"{self.site_name} reCAPTCHA処理実施中")


                # solveRecaptchaファイルを実行
                try:
                    self.recaptcha_solver.handle_recaptcha(self.current_url)
                    self.logger.info(f"{self.site_name} reCAPTCHA処理、完了")

                except Exception as e:
                    self.logger.error(f"{self.site_name} reCAPTCHA処理に失敗しました")
                    # ログイン失敗をライン通知
                    self.line_notify.line_notify(f"{self.site_name} ログインが正しくできませんでした")


                self.logger.debug(f"{self.site_name} クリック開始")

                # ログインボタン要素を見つける
                login_button = self.chrome.find_element_by_id(f"{self.site_name} recaptcha-submit")

                # ボタンが無効化されているか確認し、無効化されていれば有効にする
                self.chrome.execute_script("document.getElementById('recaptcha-submit').disabled = false;")

                # ボタンをクリックする
                login_button.click()

            else:
                self.logger.info(f"{self.site_name} reCAPTCHAなし")

                login_button = self.chrome.find_element_by_xpath(self.login_button_xpath)
                self.logger.debug(f"{self.site_name} ボタン捜索完了")

                login_button.send_keys(Keys.ENTER)
                self.logger.debug(f"{self.site_name} クリック完了")

        # recaptchaなし
        except NoSuchElementException:
            self.logger.info(f"{self.site_name} reCAPTCHAなし")

            login_button = self.chrome.find_element_by_xpath(self.login_button_xpath)
            self.logger.debug(f"{self.site_name} ボタン捜索完了")


            # ログインボタンクリック
            try:
                login_button.send_keys(Keys.ENTER)
                self.logger.debug(f"{self.site_name} クリック完了")

            except ElementNotInteractableException:
                self.chrome.execute_script("arguments[0].click();", login_button)
                self.logger.debug(f"{self.site_name} JavaScriptを使用してクリック実行")

        # ページ読み込み待機
        try:
            # ログインした後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ログインページ読み込み完了")


        except Exception as e:
            self.logger.error(f"{self.site_name} handle_recaptcha を実行中にエラーが発生しました: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------


    def isChecked(self):
        # user情報があるかを確認してログインできてるかを確認
        try:
            self.chrome.find_element_by_xpath(self.user_element_xpath)
            self.logger.info(f"{self.site_name} ログイン完了")

        except NoSuchElementException as e:
            self.logger.error(f"{self.site_name} カートの確認が取れませんでした: {e}")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生しました: {e}")

        time.sleep(1)

# ----------------------------------------------------------------------------------


    def save_cookies(self):
        '''  Cookieを取得する
        '''
        self.logger.debug(f"{self.site_name} Cookieの取得開始")
        # cookiesは、通常、複数のCookie情報を含む大きなリスト担っている
        # 各Cookieはキーと値のペアを持つ辞書（またはオブジェクト）として格納されてる
        cookies = self.chrome.get_cookies()
        self.logger.debug(f"{self.site_name} Cookieの取得完了")

        # クッキーの存在を確認
        # 「expiry」は有効期限 →Columnに存在する
        # 各Cookieから['name']['expiry']を抽出してテキストに保存
        if cookies:
            self.logger.debug(f"{self.site_name} クッキーが存在します。")
            with open('cookie_expiry_timestamp.txt', 'w', encoding='utf-8') as file:
                for cookie in cookies:
                    if 'expiry' in cookie:
                        expiry_timestamp = cookie['expiry']

                        # UNIXタイムスタンプを datetime オブジェクトに変換
                        datetime.datetime.utcfromtimestamp(expiry_timestamp)

                        # テキストに書き込めるようにクリーニング
                        cookie_expiry_timestamp = f"Cookie: {cookie['name']} の有効期限は「{expiry_timestamp}」\ｎ"
                        file.write(cookie_expiry_timestamp)

        else:
            self.logger.debug(f"{self.site_name} にはクッキーが存在しません。")

        # Cookieのディレクトリを指定
        cookies_file_path = f'cookies/{self.cookies_file_name}'

        # pickleデータを蓄積（ディレクトリがなければ作成）
        with open(cookies_file_path, 'w') as file:
            pickle.dump(cookies, file)

        self.logger.debug(f"{self.site_name} Cookie、保存完了。")


# ----------------------------------------------------------------------------------


    # 非同期化させるために、すべてのメソッドをとりまとめ
    def no_cookie_login(self):
        '''  ログインしてCookieを取得する。
        '''
        self.logger.debug(f"{__name__}: 処理開始")

        self.open_site()
        self.id_pass_input()
        self.login_checkbox()
        self.recaptcha_process()
        self.isChecked()
        self.save_cookies()

        self.logger.debug(f"{__name__}: 処理完了")


# ----------------------------------------------------------------------------------


    # 同期メソッドを非同期処理に変換
    async def no_cookie_login_async(self):
        loop = asyncio.get_running_loop()

        # ブロッキング、実行タイミング、並列処理などを適切に行えるように「functools」にてワンクッション置いて実行
        await loop.run_in_executor(executor, functools.partial(self.no_cookie_login))