# coding: utf-8
# ----------------------------------------------------------------------------------
# 非同期処理 自動ログインクラス
# headlessモード、reCAPTCHA回避
# 2023/3/8制作

#! webdriverをどこが開いているのかを確認しながら実装が必要。
# ----------------------------------------------------------------------------------


import asyncio
import functools
import os
import pickle
import requests
import time
import datetime
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        InvalidSelectorException,
                                        NoSuchElementException,
                                        WebDriverException,
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


# 拡張機能の絶対path
script_dir = os.path.dirname(os.path.abspath(__file__))
# 現在のスクリプトの親ディレクトリのパス
parent_dir = os.path.dirname(script_dir)

security_path = os.path.join(parent_dir, 'data', 'uBlock-Origin.crx')
cap_path = os.path.join(parent_dir, 'data', 'hlifkpholllijblknnmbfagnkjneagid.crx')
cookie_text_path = os.path.join(script_dir, 'cookies')


# ----------------------------------------------------------------------------------
# '''新しいCookieを取得する or Cookieが使わないサイト'''

class GetCookie:
    def __init__(self,  loginurl, userid, password, cookies_file_name, account_id, config, debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.setup_chrome()

        # 現在のURLを示すメソッドを定義
        self.current_url = self.chrome.current_url

        self.login_url = loginurl
        self.userid = userid
        self.password = password
        self.cookies_file_name = cookies_file_name
        self.account_id = account_id
        self.discord_url = os.getenv('DISCORD_BOT_URL')


        # xpath全体で使えるように初期化
        self.site_name = config["site_name"]
        self.userid_xpath = config["userid_xpath"]
        self.password_xpath = config["password_xpath"]
        self.login_button_xpath = config["login_button_xpath"]
        # self.login_checkbox_xpath = config["login_checkbox_xpath"]
        self.user_element_xpath = config["user_element_xpath"]

        # SolverRecaptchaクラスを初期化
        self.recaptcha_breakthrough = RecaptchaBreakthrough(self.chrome)


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
    # 同期的なログイン
    def open_site(self):
        '''Cookieで開かない際に使うメソッド'''
        self.logger.info(f"{self.site_name} Cookie作成を開始")
        self.chrome.get(self.login_url)

        # 現在のURL
        self.logger.debug(f"{self.site_name} URL: {self.current_url}")

        # userid_xpathが出てくるまで待機
        try:
            WebDriverWait(self.chrome, 10).until(EC.presence_of_element_located((By.XPATH, self.userid_xpath)))
            self.logger.debug(f"{self.site_name} 入力開始")

        except TimeoutException as e:
            self.error_screenshot_discord(
                f"{self.site_name} open_site タイムアウトエラー {e}",  # discordへの出力
                str(e),
                f"{self.site_name} open_site タイムアウトエラー {e}"  # ログへの出力
            )

        except Exception as e:
            self.error_screenshot_discord(
                f"{self.site_name} open_site 処理中にエラーが発生しました {e}",  # discordへの出力
                str(e),
                f"{self.site_name} open_site 処理中にエラーが発生しました {e}"  # ログへの出力
            )

        time.sleep(5)


# ----------------------------------------------------------------------------------


    # IDとパスを入力
    def id_pass_input(self):
        try:
            self.logger.debug(f"{self.account_id} : ID入力要素 捜索開始")
            userid_field = self.chrome.find_element(By.XPATH, self.userid_xpath)
            self.logger.debug(f"{self.account_id} : {self.userid}")
            userid_field.send_keys(self.userid)
            self.logger.debug(f"{self.account_id} : ID入力完了")

            time.sleep(1)

            password_field = self.chrome.find_element(By.XPATH, self.password_xpath)
            self.logger.debug(f"{self.account_id} : {self.password}")
            password_field.send_keys(self.password)
            self.logger.debug(f"{self.account_id} : パスワード入力 完了")

            # ページが完全に読み込まれるまで待機
            WebDriverWait(self.chrome, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            self.logger.debug("ページは完全に表示されてる")

            self.logger.debug(f"{self.account_id} : JavaScript にてクリック")
            WebDriverWait(self.chrome, 10).until(
                EC.visibility_of_element_located((By.XPATH, self.login_button_xpath))
            )
            self.logger.debug(f"{self.account_id} ： JavaScript にてクリック 完了")

        except NoSuchElementException as e:
            self.error_screenshot_discord(
                f"{self.site_name} id_pass_input 要素が見つかりません {e}",  # discordへの出力
                str(e),
                f"{self.site_name} id_pass_input 要素が見つかりません {e}"  # ログへの出力
            )

        except Exception as e:
            self.error_screenshot_discord(
                f"{self.site_name} id_pass_input 処理中にエラーが発生しました {e}",  # discordへの出力
                str(e),
                f"{self.site_name} id_pass_input 処理中にエラーが発生しました {e}"  # ログへの出力
            )

        time.sleep(1)


# ----------------------------------------------------------------------------------


    def login_checkbox(self):
        '''チェックボックスにチェックいれる'''
        # ログインを維持するチェックボックスを探す
        try:
            login_checkbox = self.chrome.find_element(By.XPATH, self.login_checkbox_xpath)
            self.logger.debug(f"{self.site_name} login_checkbox 見つかりました。")

        except ElementNotInteractableException as e:
            self.logger.error(f"{self.site_name} login_checkbox 見つかりません。{e}")

        except InvalidSelectorException:
            self.logger.debug(f"{self.site_name} login_checkbox ないためスキップ")

        try:
            if login_checkbox:
            # remember_boxをクリックする
                login_checkbox.click()
            self.logger.debug(f"{self.site_name} login_checkbox クリック")

        except UnboundLocalError:
            self.logger.debug(f"{self.site_name}  login_checkbox なし")

        time.sleep(3)


# ----------------------------------------------------------------------------------


    def recaptcha_process(self):
        '''reCAPTCHA検知してある場合は2CAPTCHAメソッドを実行'''
        # 現在のURL
        current_url = self.chrome.current_url
        self.logger.debug(current_url)

        # self.recaptcha_breakthrough.process(current_url)

        try:
            # deploy_btn 要素を見つける
            self.logger.debug(f"{self.site_name} 出品ボタン 捜索 開始")
                # ログインボタン要素を見つける
            login_button = self.chrome.find_element(By.XPATH, self.login_button_xpath)

            self.logger.debug(f"{self.site_name} ボタン捜索完了")

            # ボタンをクリックする
            self.logger.debug(f"{self.site_name} ボタン捜索完了")
            login_button.click()
            self.logger.debug(f"{self.site_name} ボタン捜索完了")

            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 120).until(
                EC.visibility_of_element_located((By.XPATH, self.config['user_element_xpath']))
            )

        except NoSuchElementException as e:
            self.error_screenshot_discord(
                f"{self.site_name} recaptcha_process 要素が見つかりません {e}",  # discordへの出力
                str(e),
                f"{self.site_name} recaptcha_process 要素が見つかりません {e}"  # ログへの出力
            )

        except TimeoutException as e:
            self.error_screenshot_discord(
                "reCAPTCHAのエラーの可能性大・・",  # discordへの出力
                str(e),
                "reCAPTCHAのエラーの可能性大・・"  # ログへの出力
            )

        except Exception as e:
            self.error_screenshot_discord(
                "reCAPTCHAのエラーの可能性大・・",  # discordへの出力
                str(e),
                "reCAPTCHAのエラーの可能性大・・"  # ログへの出力
            )

        time.sleep(3)  # reCAPTCHA処理の待機時間


# ----------------------------------------------------------------------------------


    def isChecked(self):
        # user情報があるかを確認してログインできてるかを確認
        try:
            self.chrome.find_element(By.XPATH, self.user_element_xpath)
            self.logger.info(f"{self.site_name} ログイン完了")

        except NoSuchElementException as e:
            self.error_screenshot_discord(
                f"{self.site_name} isChecked 要素が見つかりません {e}",  # discordへの出力
                str(e),
                f"{self.site_name} isChecked 要素が見つかりません {e}"  # ログへの出力
            )
        except Exception as e:
            self.error_screenshot_discord(
                f"{self.site_name} isChecked 処理中にエラーが発生しました {e}",  # discordへの出力
                str(e),
                f"{self.site_name} isChecked 処理中にエラーが発生しました {e}"  # ログへの出力
            )

        time.sleep(1)

# ----------------------------------------------------------------------------------


    def save_cookies(self):
        '''  Cookieを取得する'''
        self.logger.debug(f"{self.site_name} Cookieの取得開始")
        self.logger.debug(f"cookies_file_name :{self.cookies_file_name}")
        # cookiesは、通常、複数のCookie情報を含む大きなリスト担っている
        # 各Cookieはキーと値のペアを持つ辞書（またはオブジェクト）として格納されてる
        cookies = self.chrome.get_cookies()
        self.logger.debug(f"{self.site_name} Cookieの取得完了")

        # クッキーの存在を確認
        # 「expiry」は有効期限 →Columnに存在する
        # 各Cookieから['name']['expiry']を抽出してテキストに保存
        #! 必ずテキストを確認してCookieの有効期限を確認する
        #! 一番期日が短いものについて必ず確認してCookieの使用期間を明確にする
        #! _gid:24時間の有効期限があり、訪問者の1日ごとの行動を追跡

        if cookies:
            self.logger.debug(f"{self.account_id} クッキーが存在します。")
            with open(f'{cookie_text_path}/{self.account_id}_cookie.txt', 'w', encoding='utf-8') as file:
                for cookie in cookies:
                    if 'expiry' in cookie:
                        expiry_timestamp = cookie['expiry']

                        # UNIXタイムスタンプを datetime オブジェクトに変換
                        expiry_datetime = datetime.utcfromtimestamp(expiry_timestamp)

                        # テキストに書き込めるようにクリーニング
                        cookie_expiry_timestamp = f"Cookie: {cookie['name']} の有効期限は「{expiry_datetime}」\n"
                        file.write(cookie_expiry_timestamp)

        else:
            self.logger.debug(f"{self.site_name} にはクッキーが存在しません。")

        # Cookieのディレクトリを指定
        cookies_file_path = f'{cookie_text_path}/{self.cookies_file_name}'

        # pickleデータを蓄積（ディレクトリがなければ作成）
        with open(cookies_file_path, 'wb') as file:
            pickle.dump(cookies, file)

        self.logger.debug(f"{self.site_name} Cookie、保存完了。")

        with open(f'{cookie_text_path}/{self.cookies_file_name}', 'rb') as file:
            cookies = pickle.load(file)

        # 読み込んだデータを表示
        self.logger.debug(f"cookies: {cookies} \nCookieの存在を確認。")


# ----------------------------------------------------------------------------------


    # 非同期化させるために、すべてのメソッドをとりまとめ
    def cookie_get(self):
        '''ログインしてCookieを取得する。'''

        self.logger.debug(f"{__name__}: 処理開始")

        self.open_site()
        self.id_pass_input()
        # self.login_checkbox()
        self.recaptcha_process()
        self.isChecked()
        self.save_cookies()

        # self.info_screenshot_discord(
        #     "【reCAPTCHA回避】Cookieの取得に成功",
        #     "【reCAPTCHA回避】Cookieの取得に成功"
        # )

        time.sleep(2)

        self.chrome.quit()


# ----------------------------------------------------------------------------------


    # 同期メソッドを非同期処理に変換
    async def cookie_get_async(self):
        loop = asyncio.get_running_loop()

        # ブロッキング、実行タイミング、並列処理などを適切に行えるように「functools」にてワンクッション置いて実行
        await loop.run_in_executor(None, functools.partial(self.cookie_get))


# ----------------------------------------------------------------------------------