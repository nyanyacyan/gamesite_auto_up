# coding: utf-8
# ----------------------------------------------------------------------------------
# ! 非同期処理→ まとめて非同期処理へ変換する
# サイトを操作して出品まで実装クラス
# headlessモード、reCAPTCHA回避
# 2023/3/9 制作
# ----------------------------------------------------------------------------------
import asyncio
import functools
import os
import pickle
import time
import requests
import pyperclip
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        UnexpectedAlertPresentException,
                                        NoAlertPresentException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

# 自作モジュール
from auto_login.solve_recaptcha import RecaptchaBreakthrough
from logger.debug_logger import Logger
from spreadsheet.read import Read


load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")

# 絶対path
script_dir = os.path.dirname(os.path.abspath(__file__))

# 現在のスクリプトの親ディレクトリのパス
parent_dir = os.path.dirname(script_dir)

# Cookieの絶対path
cookie_dir = os.path.join(parent_dir, 'auto_login', 'cookies/')

# スクショ保管場所の絶対path
screenshot_dir = os.path.join(parent_dir, 'DebugScreenshot/')


# ----------------------------------------------------------------------------------
# Cookie利用してログインして処理を実行するクラス

class SiteOperations:
    def __init__(self, chrome, main_url, cookies_file_name, image, gametitle, config, sheet_url, account_id, debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.chrome = chrome
        self.main_url = main_url
        self.cookies_file_name = cookies_file_name
        self.image = image
        self.gametitle = gametitle
        self.sheet_url = sheet_url
        self.account_id = account_id

        self.discord_url = os.getenv('DISCORD_BOT_URL')

        #! 使ってないものは削除する

        #* 利用してるものconfig
        self.site_name = config["site_name"]
        self.lister_btn_xpath = config["lister_btn_xpath"]
        self.photo_file_input_xpath = config["photo_file_input_xpath"]
        self.title_input_xpath = config["title_input_xpath"]
        self.title_predict_xpath = config["title_predict_xpath"]
        self.item_title_xpath = config["item_title_xpath"]
        self.item_text_xpath = config["item_text_xpath"]
        self.level_input_xpath = config["level_input_xpath"]
        self.rank_input_xpath = config["rank_input_xpath"]
        self.legend_input_xpath = config["legend_input_xpath"]
        self.item_price_xpath = config["item_price_xpath"]
        self.check_box_xpath = config["check_box_xpath"]
        self.deploy_btn_xpath = config["deploy_btn_xpath"]
        self.last_check_xpath = config["last_check_xpath"]
        self.close_btn_xpath = config["close_btn_xpath"]
        self.comment_btn_xpath = config["comment_btn_xpath"]
        self.item_comment_xpath = config["item_comment_xpath"]
        self.item_comment_btn_xpath = config['item_comment_btn_xpath']
        self.agency_input_xpath = config['agency_input_xpath']


        # SolverRecaptchaクラスを初期化
        self.recaptcha_breakthrough = RecaptchaBreakthrough(self.chrome)

        self.spreadsheet_data = Read(sheet_url, account_id)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# スクショセットアップ

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


    def cookie_login(self):
        '''Cookieを使ってログイン'''
        cookies_fullpath = os.path.join(cookie_dir, self.cookies_file_name)

        cookies = []

        # Cookieファイルを展開
        try:
            cookies = pickle.load(open(cookies_fullpath, 'rb'))

        except FileNotFoundError as e:
            self.logger.error(f"ファイルが見つかりません:{e}")

        except Exception as e:
            self.logger.error(f"処理中にエラーが起きました:{e}")

        self.chrome.get(self.main_url)
        self.logger.info("メイン画面にアクセス")

        # Cookieを設定
        for c in cookies:
            self.chrome.add_cookie(c)

        self.chrome.get(self.main_url)
        self.logger.info("Cookieを使ってメイン画面にアクセス")


        if self.main_url != self.chrome.current_url:
            self.logger.info("Cookieでのログイン成功")

        else:
            self.logger.info("Cookieでのログイン失敗 sessionでのログインに変更")
            session = requests.Session()

            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

            response = session.get(self.main_url)

            # テキスト化
            res_text = response.text
            self.logger.debug(f"res_text: {res_text}"[:30])

            #! 後で修正 テキストが確認できたらログインのできたこと内容をピックアップして「ログインの成功の条件」に追加
            # if "ログイン成功の条件" in res_text:
            #     self.logger.info("requestsによるCookieでのログイン成功")
            # else:
            #     self.logger.info("requestsによるCookieでのログイン失敗")

        try:
            # ログインした後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ログインページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.account_id} ログイン処理中にエラーが発生: {e}")

        # #TODO スクリーンショット
        # self.chrome.save_screenshot('cookie_login_after.png')
        # self.logger.debug(f"{self.account_id} ログイン状態のスクショ撮影")


# ----------------------------------------------------------------------------------


    def lister_btnPush(self):
        '''出品ボタンを見つけて押す'''
        try:
            # 出品ボタンを探して押す
            self.logger.debug("出品ボタンを特定開始")
            lister_btn = self.chrome.find_element_by_xpath(self.lister_btn_xpath)
            self.logger.debug("出品ボタンを発見")

        except NoSuchElementException as e:
            self.logger.error(f"出品ボタンが見つかりません:{e}")

        lister_btn.click()

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.account_id} 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------
# '''ダイアログを介さず、そのままファイルをアップロード'''

    def photo_upload(self):
        try:
            # fileのアップロードの<input>要素を探す
            self.logger.debug(" fileのアップロードの<input>要素 を捜索開始")
            file_input = self.chrome.find_element_by_id(self.photo_file_input_xpath)
            self.logger.debug(" fileのアップロードの<input>要素 を発見")

        except NoSuchElementException as e:
            self.logger.error(f" fileのアップロードの<input>要素 が見つかりません:{e}")

        try:
            self.logger.debug(" self.photo_file_xpath を特定開始")
            self.logger.debug(f" self.image {self.image}")
            # image_full_path = os.path.abspath(self.image)
            file_input.send_keys(self.image)
            self.logger.debug(" self.photo_file_xpath を特定開始")

        except FileNotFoundError as e:
            self.logger.error(f" photo_file_xpath が見つかりません:{e}")

        time.sleep(1)

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug("ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"実行処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------
# タイトル部分を入力して予測変換から指定タイトルを選択

    def game_title_input(self):
        try:
            # title入力欄を探す
            self.logger.debug(" title入力欄 を捜索開始")
            game_title_input = self.chrome.find_element_by_id(self.title_input_xpath)
            self.logger.debug(" title入力欄 を発見")

        except NoSuchElementException as e:
            self.logger.error(f" fileのアップロードの<input>要素 が見つかりません:{e}")

        try:
            self.logger.debug(" title_input に入力 開始")
            pyperclip.copy(self.spreadsheet_data.get_game_title())

            # コピペをSeleniumのKeysを使って行う
            game_title_input.send_keys(Keys.CONTROL, 'v')
            game_title_input.send_keys(Keys.COMMAND, 'v')

            # game_title_input.send_keys(self.gametitle)
            self.logger.debug(" title_input に入力 完了")

        except FileNotFoundError as e:
            self.logger.error(f" photo_file_xpath が見つかりません:{e}")

        time.sleep(1)

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug("ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"実行処理中にエラーが発生: {e}")

        time.sleep(1)

        try:
            # 入力予測欄を探す
            self.logger.debug(self.title_predict_xpath)
            self.logger.debug(" 入力予測欄 を捜索開始")
            title_predict = self.chrome.find_element_by_xpath(self.title_predict_xpath)
            self.logger.debug(" 入力予測欄 を発見")

            self.logger.debug(" 入力予測欄 をクリック開始")
            title_predict.click()
            self.logger.debug(" 入力予測欄 をクリック終了")

        # もし要素が見つからない場合にdisplay:noneを鑑みる
        except NoSuchElementException as e:
            self.logger.debug("指定した入力予測欄 が見つかりません")

            # display:noneを解除
            self.logger.debug(" display:noneを解除 開始")
            self.chrome.execute_script("document.getElementById('ui-id-2').style.display = 'block';")
            self.logger.debug(" display:noneを解除 完了開始")

            try:
                # 入力予測欄を探す
                self.logger.debug(" 入力予測欄 を捜索開始")
                title_predict = self.chrome.find_element_by_xpath(self.title_predict_xpath)
                self.logger.debug(" 入力予測欄 を発見")

                time.sleep(1) 

                self.logger.debug(" 入力予測欄 をクリック開始")
                title_predict.click()
                self.logger.debug(" 入力予測欄 をクリック終了")

                time.sleep(3) 

            except UnexpectedAlertPresentException:
                try:
                    alert = self.chrome.switch_to_alert
                    alert_text = alert.text
                    if "同一ゲームタイトルでの連続出品はできません。5分以上経過してから再度お試しください。" in alert_text:

                        self.logger.info("【エラー】5分以内に同じものを出品")
                        alert.accept()

                        # スクショ撮影して送付
                        filename = f"DebugScreenshot/lister_page_{timestamp}.png"
                        screenshot_saved = self.chrome.save_screenshot(filename)
                        self.logger.debug(f"エラーのスクショ撮影")
                        if screenshot_saved:

                        #! ログイン失敗を通知 クライアントに合った連絡方法
                            content="【WARNING】5分以内投稿のため出品失敗。。"

                            with open(filename, 'rb') as f:
                                files = {"file": (filename, f, "image/png")}
                                requests.post(self.discord_url, data={"content": content}, files=files)

                        self.logger.error(f"【WARNING】5分以内投稿のため出品失敗: {e}")
                        raise Exception("【WARNING】5分以内投稿のため出品失敗")

                    else:
                        alert.accept()
                except NoAlertPresentException:
                    alert.accept()

            # もし見つからなかった場合にdisplay:noneが解除されてるのか確認
            except NoSuchElementException:
                self.logger.debug("再度の検索でも入力予測欄が見つかりません")

                display = self.chrome.execute_script("return document.getElementById('ui-id-2').style.display;")
                if display != 'none':
                    self.logger.debug("display:noneが正しく解除されました。")
                    try:
                        title_predict = WebDriverWait(self.chrome, 10).until(
                            EC.visibility_of_element_located((By.XPATH, self.title_predict_xpath))
                        )
                        self.logger.debug("再度、入力予測欄を発見しました。")

                    except TimeoutException:
                        self.logger.debug("display:none解除後も要素が見つかりません。")
                else:
                    self.logger.debug("display:noneが解除されていません。")

        except Exception as e:
            self.logger.error(f"実行処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# タイトルの入力

    def item_title(self):
        try:
            # item_title を探して押す
            self.logger.debug(" item_title の特定 開始")
            title_input = self.chrome.find_element_by_id(self.config['item_title_xpath'])
            self.logger.debug("item_title を発見")

        except NoSuchElementException as e:
            self.logger.error(f"item_title が見つかりません:{e}")

        try:
            self.logger.debug(f"スプシのタイトルに入力する文言 :{self.spreadsheet_data.get_item_title()[:30]}")
            self.logger.debug(" item_title 入力開始")

            # 絵文字があるため一度クリップボードに入れ込んでコピーする
            pyperclip.copy(self.spreadsheet_data.get_item_title())

            # コピペをSeleniumのKeysを使って行う
            title_input.send_keys(Keys.CONTROL, 'v')
            title_input.send_keys(Keys.COMMAND, 'v')

            self.logger.debug(" item_title 入力完了")

        # もし要素が見つからない場合
        except NoSuchElementException as e:
            self.logger.error(f"指定した入力予測欄 が見つかりません: {e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.account_id} 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------
# 商品の説明文

    def item_text(self):
        try:
            # item_text を探して押す
            self.logger.debug(" item_text の特定 開始")
            title_input = self.chrome.find_element_by_id(self.config['item_text_xpath'])
            self.logger.debug("item_text を発見")

        except NoSuchElementException as e:
            self.logger.error(f"item_text が見つかりません:{e}")

        try:
            self.logger.debug(f"スプシのタイトルに入力する文言 :{self.spreadsheet_data.get_item_text()}"[:30])
            self.logger.debug(" item_text 入力開始")

            # 絵文字があるため一度クリップボードに入れ込んでコピーする
            pyperclip.copy(self.spreadsheet_data.get_item_text())

            # コピペをSeleniumのKeysを使って行う
            title_input.send_keys(Keys.CONTROL, 'v')    #! 本番ではこっちを使う
            title_input.send_keys(Keys.COMMAND, 'v')

            self.logger.debug(" item_text 入力完了")

        # もし要素が見つからない場合
        except NoSuchElementException as e:
            self.logger.error(f"指定した入力予測欄 が見つかりません: {e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.account_id} 処理中にエラーが発生: {e}")

        time.sleep(1)



# ----------------------------------------------------------------------------------
# '''level_input を見つけて押す'''

    def level_input(self):
        try:
            # 出品ボタンを探して押す
            self.logger.debug(" level_input を特定開始")
            level_input = self.chrome.find_element_by_id(self.level_input_xpath)
            self.logger.debug(" level_input を発見")

        except NoSuchElementException as e:
            # スクリーンショット
            filename = f"DebugScreenshot/lister_page_{timestamp}.png"
            screenshot_saved = self.chrome.save_screenshot(filename)
            self.logger.debug(f"エラーのスクショ撮影")
            if screenshot_saved:

            #! ログイン失敗を通知 クライアントに合った連絡方法
                content="【WARNING】reCAPTCHAの処理に失敗しております。\n手動での操作が必要な可能性があります。"

                with open(filename, 'rb') as f:
                    files = {"file": (filename, f, "image/png")}
                    requests.post(self.discord_url, data={"content": content}, files=files)

            raise(f"{self.account_id}: level_input が見つかりません:{e}")

        self.logger.debug(" level_input に数値入力 開始")
        level_input.send_keys('1')
        self.logger.debug(" level_input に数値入力 終了")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            raise(f"{self.account_id} 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------
# '''rank_input を見つけて押す'''

    def rank_input(self):
        try:
            # 出品ボタンを探して押す
            self.logger.debug(" rank_input 捜索 開始")
            select_element = self.chrome.find_element_by_id(self.rank_input_xpath)
            self.logger.debug(" rank_input 発見")

            self.logger.debug(" rank_input 選択 開始")

            # ドロップダウンメニューを選択できるように指定
            select_object = Select(select_element)

            # 選択肢をChoice
            select_object.select_by_visible_text("エーペックスプレデター")
            self.logger.debug(" rank_input 選択 終了")

        except NoSuchElementException as e:
            raise(f"{self.account_id}: rank_input が見つかりません:{e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            raise(f"{self.account_id} rank_input 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------
# '''legend_input を見つけて押す'''

    def legend_input(self):
        try:
            # 出品ボタンを探して押す
            self.logger.debug(" legend_input を特定開始")
            legend_input = self.chrome.find_element_by_id(self.legend_input_xpath)
            self.logger.debug(" legend_input を発見")

        except NoSuchElementException as e:
            raise(f"{self.account_id}: legend_input が見つかりません:{e}")

        self.logger.debug(" legend_input に数値入力 開始")
        legend_input.send_keys('1')
        self.logger.debug(" legend_input に数値入力 終了")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            raise(f"{self.account_id} legend_input 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------
# 商品の説明文

    def item_price(self):
        try:
            # item_price を探して押す
            self.logger.debug(" item_price_input の特定 開始")
            item_price_input = self.chrome.find_element_by_id(self.config['item_price_xpath'])
            self.logger.debug("item_price_input を発見")

            self.logger.debug(f"スプシのタイトルに入力する文言 :{self.spreadsheet_data.get_item_price()}")
            self.logger.debug(" item_price 入力開始")

            # 絵文字があるため一度クリップボードに入れ込んでコピーする
            pyperclip.copy(self.spreadsheet_data.get_item_price())

            # コピペをSeleniumのKeysを使って行う
            item_price_input.send_keys(self.spreadsheet_data.get_item_price())

            self.logger.debug(" item_price 入力完了")

        except NoSuchElementException as e:
            raise(f"{self.account_id}: item_price_input が見つかりません:{e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            raise(f"{self.account_id} item_price 処理中にエラーが発生: {e}")



        time.sleep(1)


# ----------------------------------------------------------------------------------
# チェックボックスクリック

    def check_box_Push(self):
        try:
            # deploy_btnを探して押す
            self.logger.debug(" check_box_Push 捜索 開始")
            check_box = self.chrome.find_element_by_id(self.config['check_box_xpath'])
            self.logger.debug(f"check_box :{check_box}")
            self.logger.debug(" check_box_Push 発見")

        except NoSuchElementException as e:
            raise(f"{self.account_id}: check_box_Push が見つかりません:{e}")


        check_box.click()

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} 次のページ読み込み完了")

        except Exception as e:
            raise(f"{self.account_id} check_box_Push 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------


    def recap_deploy(self):
        try:
            # deploy_btn 要素を見つける
            self.logger.debug(f"{self.account_id} 出品ボタン 捜索 開始")
            deploy_btn = self.chrome.find_element_by_xpath(self.deploy_btn_xpath)
            self.logger.debug(f"{self.account_id} 出品ボタン 捜索 終了")

            # ボタンをクリックする
            deploy_btn.click()
            self.logger.debug(f"{self.account_id} クリック 完了")

        except NoSuchElementException as e:
            raise(f"{self.account_id}: rank_input が見つかりません:{e}")

        # 通常のクリックができなかった時にJavaScriptにてクリック
        except ElementNotInteractableException:
            self.chrome.execute_script("arguments[0].click();", deploy_btn)
            self.logger.debug(f"{self.account_id} JavaScriptを使用してクリック実行")

        # ページ読み込み待機
        try:
            # ログインした後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ログインページ読み込み完了")


        except Exception as e:
            self.logger.error(f"{self.account_id} 2CAPTCHAの処理を実行中にエラーが発生しました: {e}")

        time.sleep(30)  # reCAPTCHA処理の待機時間


# ----------------------------------------------------------------------------------


    def deploy_btnPush(self):
        try:
            # deploy_btnを探して押す
            self.logger.debug(" deploy_btn を特定開始")
            deploy_btn = self.chrome.find_element_by_xpath(self.deploy_btn_xpath)
            self.logger.debug(" deploy_btn を発見")

        except NoSuchElementException as e:
            raise(f"{self.account_id}: deploy_btnPush が見つかりません:{e}")

        deploy_btn.click()

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 120).until(
                EC.visibility_of_element_located((By.XPATH, self.config['last_check_xpath']))
            )

        except Exception as e:
            # # エラーのスクショを送信
            # filename = f"DebugScreenshot/lister_page_{timestamp}.png"
            # screenshot_saved = self.chrome.save_screenshot(filename)
            # self.logger.debug(f"出品ボタン押下の際にエラーになった際 スクショ撮影")
            # if screenshot_saved:

            # #! ログイン失敗を通知 クライアントに合った連絡方法
            #     content="【WARNING】出品ボタン押下の際にエラー"

            #     with open(filename, 'rb') as f:
            #         files = {"file": (filename, f, "image/png")}
            #         requests.post(self.discord_url, data={"content": content}, files=files)

            # raise(f"{self.account_id} deploy_btnPush 処理中にエラーが発生: {e}")

            self.error_screenshot_discord(
                "reCAPTCHAのエラーの可能性大・・",  # discordへの出力
                str(e),
                "reCAPTCHAのエラーの可能性大・・"  # ログへの出力
            )

        time.sleep(3)  # reCAPTCHA処理の待機時間


# ----------------------------------------------------------------------------------


    def last_check(self):
        try:
            # last_check 要素を見つける
            self.logger.debug(f"{self.account_id} 出品完了Message 捜索 開始")
            self.chrome.find_element_by_xpath(self.config['last_check_xpath'])
            self.logger.debug(f"{self.account_id} 出品完了Message 捜索 終了")

            self.logger.debug(f"{self.account_id} 出品完了モーダル 捜索 開始")
            close_btn = self.chrome.find_element_by_xpath(self.config['close_btn_xpath'])
            self.logger.debug(f"{self.account_id} 出品完了モーダル 捜索 終了")

            # ボタンをクリックする
            close_btn.click()
            self.logger.debug(f"{self.account_id} クリック 完了")

        except NoSuchElementException as e:
            filename = f"DebugScreenshot/lister_page_{timestamp}.png"
            screenshot_saved = self.chrome.save_screenshot(filename)
            self.logger.debug(f"エラーのスクショ撮影")
            if screenshot_saved:

            #! ログイン失敗を通知 クライアントに合った連絡方法
                content="【WARNING】出品に失敗してる可能性あり。。"

                with open(filename, 'rb') as f:
                    files = {"file": (filename, f, "image/png")}
                    requests.post(self.discord_url, data={"content": content}, files=files)

            raise Exception(f"{self.account_id}: 【WARNING】 出品処理に失敗: {e}")

        time.sleep(2)


# ----------------------------------------------------------------------------------


    def comment_btn(self):
        try:
            self.logger.debug(f"{self.account_id} comment_btn 捜索 開始")
            comment_btn = self.chrome.find_element_by_xpath(self.config['comment_btn_xpath'])
            self.logger.debug(f"{self.account_id} comment_btn 捜索 終了")

            # ボタンをクリックする
            comment_btn.click()
            self.logger.debug(f"{self.account_id} クリック 完了")

        except NoSuchElementException as e:
            filename = f"DebugScreenshot/lister_page_{timestamp}.png"
            screenshot_saved = self.chrome.save_screenshot(filename)
            self.logger.debug(f"エラーのスクショ撮影")
            if screenshot_saved:

            #! ログイン失敗を通知 クライアントに合った連絡方法
                content="【WARNING】出品に失敗してる可能性あり。。"

                with open(filename, 'rb') as f:
                    files = {"file": (filename, f, "image/png")}
                    requests.post(self.discord_url, data={"content": content}, files=files)

            raise Exception(f"{self.account_id}: comment_btn が見つかりません:{e}")

        time.sleep(2)


# ----------------------------------------------------------------------------------
# 商品に追加コメント

    def item_comment(self):
        try:
            # item_comment を探して押す
            self.logger.debug(" item_comment の特定 開始")
            item_comment_input = self.chrome.find_element_by_id(self.config['item_comment_xpath'])
            self.logger.debug("item_comment を発見")

        except NoSuchElementException as e:
            raise(f"{self.account_id}: item_comment が見つかりません:{e}")

        try:
            self.logger.debug(f"スプシのタイトルに入力する文言 :{self.spreadsheet_data.get_item_comment()}")
            self.logger.debug(" item_comment 入力開始")

            # 絵文字があるため一度クリップボードに入れ込んでコピーする
            pyperclip.copy(self.spreadsheet_data.get_item_comment())

            # コピペをSeleniumのKeysを使って行う
            item_comment_input.send_keys(self.spreadsheet_data.get_item_comment())

            self.logger.debug(" item_comment 入力完了")

        # もし要素が見つからない場合
        except NoSuchElementException as e:
            raise(f"{self.account_id}: 指定した入力予測欄 が見つかりません: {e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            raise(f"{self.account_id} item_comment 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------


    def item_comment_btn(self):
        try:
            self.logger.debug(f"{self.account_id} item_comment_btn 捜索 開始")
            item_comment_btn = self.chrome.find_element_by_xpath(self.config['item_comment_btn_xpath'])
            self.logger.debug(f"{self.account_id} item_comment_btn 捜索 終了")

            # ボタンをクリックする
            item_comment_btn.click()
            self.logger.debug(f"{self.account_id} クリック 完了")

        except NoSuchElementException as e:
            filename = f"DebugScreenshot/lister_page_{timestamp}.png"
            screenshot_saved = self.chrome.save_screenshot(filename)
            self.logger.debug(f"エラーのスクショ撮影")
            if screenshot_saved:

            #! ログイン失敗を通知 クライアントに合った連絡方法
                content="【WARNING】出品に失敗してる可能性あり。。"

                with open(filename, 'rb') as f:
                    files = {"file": (filename, f, "image/png")}
                    requests.post(self.discord_url, data={"content": content}, files=files)

            self.logger.error(f"【WARNING】item_comment_btn が見つからない: {e}")
            raise Exception(f"{self.account_id}: item_comment_btn が見つかりません:{e}")

        time.sleep(2)


# ----------------------------------------------------------------------------------
# '''agency_input を見つけて押す'''
# display:noneを解除したあとの操作はJavaScriptにて行う必要がある

    def agency_input(self):
        try:
            # 出品ボタンを探して押す
            self.logger.debug(" agency_input 捜索 開始")
            select_element = self.chrome.find_element_by_id(self.agency_input_xpath)
            self.logger.debug(" agency_input 発見")


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
                print(f"display:noneが見つからない: {e}")
                raise

            except Exception as e:
                self.logger.error(f"display:noneの削除に失敗しましたので確認が必要です:{e}")
                raise

            time.sleep(2)

            self.logger.debug(" agency_input 選択 開始")

            # ドロップダウンメニューを選択できるように指定
            self.chrome.execute_script("""var element = document.getElementById('exhibit_exhibit_category_id');
                                    element.value = '48'; // 代行を選択
                                    // change イベントをトリガー
                                    var event = new Event('change', { bubbles: true });
                                    element.dispatchEvent(event);""")

            self.logger.debug(" agency_input 選択 終了")

            time.sleep(1)
            select_element.send_keys(Keys.ENTER)

        except NoSuchElementException as e:
            raise Exception(f"{self.account_id}: comment_btn が見つかりません:{e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.account_id} ページ読み込み完了")

        except Exception as e:
            raise Exception(f"{self.account_id}: comment_btn が見つかりません:{e}")

        time.sleep(3)


# ----------------------------------------------------------------------------------
# メインメソッド(アカウント)

    def site_operation(self):
        '''メインメソッド'''
        self.logger.debug(f"{__name__}: 処理開始")

        self.cookie_login()
        self.lister_btnPush()
        self.photo_upload()
        self.game_title_input()
        self.item_title()
        self.item_text()
        self.level_input()
        self.rank_input()
        self.legend_input()
        self.item_price()
        self.check_box_Push()
        self.deploy_btnPush()
        self.last_check()
        self.comment_btn()
        self.item_comment()
        self.item_comment_btn()

        time.sleep(3)

        # 成功のスクショを送信
        self.info_screenshot_discord(
            "reCAPTCHA回避 成功",  # discordへの通知
            "reCAPTCHA回避 成功"  # ログへの通知
        )

        time.sleep(2)


        self.logger.debug(f"{__name__}: 処理完了")


# ----------------------------------------------------------------------------------
# もしタイトルが追加になった場合には(self.site_operation)部分を変数にする
# それぞれのタイトルをメソッド化してスプシの内容が反映するように変更

#TODO メインメソッドを非同期処理に変換
    # 同期メソッドを非同期処理に変換
    async def site_operation_async(self):
        loop = asyncio.get_running_loop()

        # ブロッキング、実行タイミング、並列処理などを適切に行えるように「functools」にてワンクッション置いて実行
        await loop.run_in_executor(None, functools.partial(self.site_operation))


# ----------------------------------------------------------------------------------
# スプシからのデータ内容を確認して実行するメインメソッドを切り替えて実行する


# def method_11():
#     print("実行中: メソッド11")

# def method_22():
#     print("実行中: メソッド22")

# def method_33():
#     print("実行中: メソッド33")

# # 関数をキーにマッピング
# methods = {
#     "A": method_11,
#     "B": method_22,
#     "C": method_33,
# }

# # スプレッドシートから取得した値
# value_from_spreadsheet = "B"  # 例えば、"B"が選択されたとします

# # 辞書を使用して関数を呼び出す
# method_to_call = methods.get(value_from_spreadsheet)

# if method_to_call:
#     method_to_call()
# else:
#     print("該当するメソッドがありません。")

# ----------------------------------------------------------------------------------
# メインメソッド(代行)

    def agency_site_operation(self):
        '''メインメソッド'''
        self.logger.debug(f"{__name__}: 処理開始")

        self.cookie_login()
        self.lister_btnPush()
        self.photo_upload()
        self.game_title_input()
        self.agency_input()
        self.item_title()
        self.item_text()
        # self.level_input()
        # self.rank_input()
        # self.legend_input()
        self.item_price()
        self.check_box_Push()
        self.deploy_btnPush()
        self.last_check()
        self.comment_btn()
        self.item_comment()
        self.item_comment_btn()

        time.sleep(3)

        # 成功のスクショを送信
        self.info_screenshot_discord(
            "reCAPTCHA回避 成功",  # discordへの通知
            "reCAPTCHA回避 成功"  # ログへの通知
        )

        time.sleep(2)


        self.logger.debug(f"{__name__}: 処理完了")


# ----------------------------------------------------------------------------------
# メインメソッドを非同期処理に変換

    async def agency_site_operation_async(self):
        loop = asyncio.get_running_loop()

        # ブロッキング、実行タイミング、並列処理などを適切に行えるように「functools」にてワンクッション置いて実行
        await loop.run_in_executor(None, functools.partial(self.agency_site_operation))


# ----------------------------------------------------------------------------------