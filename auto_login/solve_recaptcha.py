# coding: utf-8
# ----------------------------------------------------------------------------------
# recaptcha回避　クラス
# 2023/1/20制作
# 2023/3/8修正
# 仮想環境 / source autologin-v1/bin/activate

# ----------------------------------------------------------------------------------
import sys
import os, time
import requests
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from twocaptcha import TwoCaptcha
from dotenv import load_dotenv

# 自作モジュール
from logger.debug_logger import Logger

load_dotenv()

timestamp = datetime.now().strftime("%m-%d_%H-%M")


# ----------------------------------------------------------------------------------


class RecaptchaBreakthrough:
    def __init__(self, chrome, debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.chrome = chrome

        # 2captcha APIkeyを.envから取得
        self.api_key = os.getenv('TWOCAPTCHA_KEY')

        #* 通知関係
        self.discord_url = os.getenv('DISCORD_BOT_URL')


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# 2CAPTCHAへのリクエスト

    def checkKey(self, sitekey, url):
        solver = TwoCaptcha(self.api_key)

        try:
            result = solver.recaptcha(
                sitekey=sitekey,
                url=url
                )

        except Exception as e:
            sys.exit(e)

        else:
            return result


# ----------------------------------------------------------------------------------
# reCAPTCHA処理

    def recaptchaIfNeeded(self, current_url):
        try:
            self.logger.debug("display:noneを削除開始")

            # display:noneを[""](空欄)に書き換え
            self.chrome.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')

            # 現在のdisplayプロパティ内の値を抽出
            style = self.chrome.execute_script('return document.getElementById("g-recaptcha-response").style.display')

            self.logger.debug(style)

            if style == "":
                self.logger.debug("display:noneの削除に成功しました")
            else:
                raise Exception("display:noneの削除に失敗しました")

        except NoSuchElementException as e:
            print(f"要素が見つからない: {e}")

        except Exception as e:
            self.logger.error(f"display:noneの削除に失敗しましたので確認が必要です:{e}")
            sys.exit(1)


        # data-sitekeyを検索
        recaptcha_element = self.chrome.find_element_by_css_selector('[data-sitekey]')

        # sitekeyの値を抽出
        data_sitekey_value = recaptcha_element.get_attribute('data-sitekey')

        self.logger.debug(f"data_sitekey_value: {data_sitekey_value}")
        self.logger.debug(f"current_url: {current_url}")

        self.logger.info("2captcha開始")
        time.sleep(1)

        result = self.checkKey(
            data_sitekey_value,
            current_url
        )

        try:
            # レスポンスがあった中のトークン部分を抽出
            code = result['code']

        except Exception as e:
            self.logger.error(f"エラーが発生しました: {e}")


        try:
            # トークンをtextareaに入力
            textarea = self.chrome.find_element_by_id('g-recaptcha-response')
            self.chrome.execute_script(f'arguments[0].value = "{code}";', textarea)

            # textareaの値を取得
            textarea_value = self.chrome.execute_script('return document.getElementById("g-recaptcha-response").value;')

            if code == textarea_value:
                self.logger.debug("textareaにトークン入力完了")
                time.sleep(2)

        except Exception as e:
            self.logger.error(f"トークンの入力に失敗: {e}")


# ----------------------------------------------------------------------------------
# 実行Process

    def process(self, current_url):
        try_count = 0

        while try_count < 1:
            try_count += 1

            # sitekeyを検索
            self.logger.info(f"【{try_count}回目】reCAPTCHAチェック")
            elements = self.chrome.find_elements_by_css_selector('[data-sitekey]')
            if len(elements) > 0:
                self.logger.info(f"【{try_count}回目】reCAPTCHA 発見")

                # solveRecaptchaファイルを実行
                try:
                    self.recaptchaIfNeeded(current_url)
                    self.logger.info(f"【{try_count}回目】reCAPTCHA 突破!!")

                    time.sleep(3)

                except Exception as e:
                    filename = f"DebugScreenshot/lister_page_{timestamp}.png"
                    screenshot_saved = self.chrome.save_screenshot(filename)
                    self.logger.debug(f"エラーのスクショ撮影")
                    if screenshot_saved:

                    #! ログイン失敗を通知 クライアントに合った連絡方法
                        content="【WARNING】reCAPTCHAの処理に失敗しております。\n手動での操作が必要な可能性があります。"

                        with open(filename, 'rb') as f:
                            files = {"file": (filename, f, "image/png")}
                            requests.post(self.discord_url, data={"content": content}, files=files)

                    self.logger.error(f"reCAPTCHA処理に失敗しました: {e}")
                    raise Exception("【WARNING】reCAPTCHAの処理に失敗。")

            else:
                self.logger.info(f"【{try_count}回目】reCAPTCHAなし")
                break


# ----------------------------------------------------------------------------------