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
from selenium.webdriver.support.ui import WebDriverWait, Select
from webdriver_manager.chrome import ChromeDriverManager

# 自作モジュール
from auto_login.solve_recaptcha import RecaptchaBreakthrough
from logger.debug_logger import Logger


load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")


# ----------------------------------------------------------------------------------
# Cookie利用してログインして処理を実行するクラス

class SiteOperations:
    def __init__(self, chrome, main_url, cookies_file_name, image, gametitle, config,  debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.chrome = chrome
        self.main_url = main_url
        self.cookies_file_name = cookies_file_name
        self.image = image
        self.gametitle = gametitle

        #! 使ってないものは削除する

        #* 利用してるものconfig
        self.site_name = config["site_name"]
        self.lister_btn_xpath = config["lister_btn_xpath"]
        self.photo_file_input_xpath = config["photo_file_input_xpath"]
        self.title_input_xpath = config["title_input_xpath"]
        self.title_predict_xpath = config["title_predict_xpath"]
<<<<<<< HEAD
        self.item_title_xpath = config["item_title_xpath"]
        self.item_text_xpath = config["item_text_xpath"]
        self.level_input_xpath = config["level_input_xpath"]
        self.rank_input_xpath = config["rank_input_xpath"]
        self.legend_input_xpath = config["legend_input_xpath"]
        self.item_price_xpath = config["item_price_xpath"]
        self.check_box_xpath = config["check_box_xpath"]
        self.deploy_btn_xpath = config["deploy_btn_xpath"]

<<<<<<< HEAD
=======
>>>>>>> parent of a8ecfdd (スクレイピング最後まで完了)
=======
>>>>>>> 7cddafa4b48b547c09391ee3ca214746c9c984ae

        # SolverRecaptchaクラスを初期化
        self.recaptcha_breakthrough = RecaptchaBreakthrough(self.chrome)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------


    def cookie_login(self):
        '''Cookieを使ってログイン'''

        # Cookieファイルを展開
        try:
            cookies = pickle.load(open('auto_login/cookies/' + self.cookies_file_name, 'rb'))

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
            self.logger.info("Cookieでのログイン失敗")
            session = requests.Session()

            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

            response = session.get(self.main_url)

            # テキスト化
            res_text = response.text
            self.logger.debug(f"res_text: {res_text}")

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
            self.logger.debug(f"{self.site_name} ログインページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} ログイン処理中にエラーが発生: {e}")


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
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

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
            image_full_path = os.path.abspath(self.image)
            file_input.send_keys(image_full_path)
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
# タイトル部分を入力して予測編から指定タイトルを選択

    def title_input(self):
        try:
            # title入力欄を探す
            self.logger.debug(" title入力欄 を捜索開始")
            file_input = self.chrome.find_element_by_id(self.title_input_xpath)
            self.logger.debug(" title入力欄 を発見")

        except NoSuchElementException as e:
            self.logger.error(f" fileのアップロードの<input>要素 が見つかりません:{e}")

        try:
            self.logger.debug(" self.photo_file_xpath を特定開始")
            file_input.send_keys(self.gametitle)
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

        try:
            # 入力予測欄を探す
            self.logger.debug(self.title_predict_xpath)
            self.logger.debug(" 入力予測欄 を捜索開始")
            title_predict = self.chrome.find_element_by_xpath(self.title_predict_xpath)
            self.logger.debug(" 入力予測欄 を発見")

            self.logger.debug(" 入力予測欄 をクリック開始")
            title_predict.click()
            self.logger.debug(" 入力予測欄 をクリック終了")

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
<<<<<<< HEAD
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
            self.logger.debug(f"スプシのタイトルに入力する文言 :{self.spreadsheet_data.get_item_title()}")
            self.logger.debug(" item_title 入力開始")

            # 絵文字があるため一度クリップボードに入れ込んでコピーする
            pyperclip.copy(self.spreadsheet_data.get_item_title())

            # コピペをSeleniumのKeysを使って行う
            title_input.send_keys(Keys.CONTROL, 'v')    #! 本番ではこっちを使う
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
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

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
            self.logger.debug(f"スプシのタイトルに入力する文言 :{self.spreadsheet_data.get_item_text()}")
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
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

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
            self.logger.error(f" level_input が見つかりません:{e}")

        self.logger.debug(" level_input に数値入力 開始")
        level_input.send_keys('1')
        self.logger.debug(" level_input に数値入力 終了")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

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
            self.logger.error(f" rank_input が見つかりません:{e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

        time.sleep(1)
<<<<<<< HEAD
=======


# ----------------------------------------------------------------------------------
# '''legend_input を見つけて押す'''

    def legend_input(self):
        try:
            # 出品ボタンを探して押す
            self.logger.debug(" legend_input を特定開始")
            legend_input = self.chrome.find_element_by_id(self.legend_input_xpath)
            self.logger.debug(" legend_input を発見")

        except NoSuchElementException as e:
            self.logger.error(f" legend_input が見つかりません:{e}")

        self.logger.debug(" legend_input に数値入力 開始")
        legend_input.send_keys('1')
        self.logger.debug(" legend_input に数値入力 終了")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------
# 商品の説明文

    def item_price(self):
        try:
            # item_price を探して押す
            self.logger.debug(" item_price の特定 開始")
            item_price_input = self.chrome.find_element_by_id(self.config['item_price_xpath'])
            self.logger.debug("item_price を発見")

        except NoSuchElementException as e:
            self.logger.error(f"item_price が見つかりません:{e}")

        try:
            self.logger.debug(f"スプシのタイトルに入力する文言 :{self.spreadsheet_data.get_item_price()}")
            self.logger.debug(" item_price 入力開始")

            # 絵文字があるため一度クリップボードに入れ込んでコピーする
            pyperclip.copy(self.spreadsheet_data.get_item_price())

            # コピペをSeleniumのKeysを使って行う
            item_price_input.send_keys(self.spreadsheet_data.get_item_price())

            self.logger.debug(" item_price 入力完了")

        # もし要素が見つからない場合
        except NoSuchElementException as e:
            self.logger.error(f"指定した入力予測欄 が見つかりません: {e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

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
            self.logger.error(f" check_box_Push が見つかりません:{e}")

        check_box.click()

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} 次のページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 実行処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------

#! deployする際に「reCAPTCHAあり」の場合に利用
#TODO 手直し必要

    def recap_deploy(self):
        '''reCAPTCHA検知してある場合は2CAPTCHAメソッドを実行'''
        try:
            # 現在のURL
            current_url = self.chrome.current_url
            self.logger.debug(current_url)
            # sitekeyを検索
            elements = self.chrome.find_elements_by_css_selector('[data-sitekey]')
            if len(elements) > 0:
                self.logger.info(f"{self.site_name} reCAPTCHA処理実施中")


                # solveRecaptchaファイルを実行
                try:
                    self.recaptcha_breakthrough.recaptchaIfNeeded(current_url)
                    self.logger.info(f"{self.site_name} reCAPTCHA処理、完了")

                except Exception as e:
                    self.logger.error(f"{self.site_name} reCAPTCHA処理に失敗しました: {e}")
                    # ログイン失敗をライン通知


                self.logger.debug(f"{self.site_name} クリック開始")

                # deploy_btn 要素を見つける
                deploy_btn = self.chrome.find_element_by_xpath(self.deploy_btn_xpath)

                # ボタンが無効化されているか確認し、無効化されていれば有効にする
<<<<<<< HEAD
<<<<<<< HEAD
                self.chrome.execute_script("document.getElementByXPATH(self.deploy_btn_xpath).disabled = false;")
=======
                # self.chrome.execute_script("document.getElementByXPATH(self.deploy_btn_xpath).disabled = false;")
>>>>>>> 4346100b5c7c891dcd38f08bd909138f3437d368
=======
                # self.chrome.execute_script("document.getElementByXPATH(self.deploy_btn_xpath).disabled = false;")
>>>>>>> 4346100b5c7c891dcd38f08bd909138f3437d368

                # ボタンをクリックする
                deploy_btn.click()

            else:
                self.logger.info(f"{self.site_name} reCAPTCHAなし")

                login_button = self.chrome.find_element_by_xpath(self.login_button_xpath)
                self.logger.debug(f"{self.site_name} ボタン捜索完了")

                deploy_btn.click()
                self.logger.debug(f"{self.site_name} クリック完了")

        # recaptchaなし
        except NoSuchElementException:
            self.logger.info(f"{self.site_name} reCAPTCHAなし")

            login_button = self.chrome.find_element_by_xpath(self.login_button_xpath)
            self.logger.debug(f"{self.site_name} ボタン捜索完了")


            # ログインボタンクリック
            try:
                deploy_btn.click()
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
            self.logger.error(f"{self.site_name} 2CAPTCHAの処理を実行中にエラーが発生しました: {e}")

        time.sleep(3)
>>>>>>> 7cddafa4b48b547c09391ee3ca214746c9c984ae


# ----------------------------------------------------------------------------------
# '''legend_input を見つけて押す'''

    def legend_input(self):
        try:
            # 出品ボタンを探して押す
            self.logger.debug(" legend_input を特定開始")
            legend_input = self.chrome.find_element_by_id(self.legend_input_xpath)
            self.logger.debug(" legend_input を発見")

        except NoSuchElementException as e:
            self.logger.error(f" legend_input が見つかりません:{e}")

        self.logger.debug(" legend_input に数値入力 開始")
        legend_input.send_keys('1')
        self.logger.debug(" legend_input に数値入力 終了")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

        time.sleep(1)

# ----------------------------------------------------------------------------------
#! 「reCAPTCHAなし」でdeploy

    def deploy_btnPush(self):
        '''出品ページにあるすべての入力が完了したあとに押す「出品する」というボタン→ deploy_btn を見つけて押す'''
        try:
            # deploy_btnを探して押す
            self.logger.debug(" deploy_btn を特定開始")
            deploy_btn = self.chrome.find_element_by_xpath(self.deploy_btn_xpath)
            self.logger.debug(" deploy_btn を発見")

        except NoSuchElementException as e:
            self.logger.error(f" deploy_btn が見つかりません:{e}")

        deploy_btn.click()

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} 次のページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 実行処理中にエラーが発生: {e}")

# ----------------------------------------------------------------------------------
# 商品の説明文

<<<<<<< HEAD
    def item_price(self):
        try:
            # item_price を探して押す
            self.logger.debug(" item_price の特定 開始")
            item_price_input = self.chrome.find_element_by_id(self.config['item_price_xpath'])
            self.logger.debug("item_price を発見")

        except NoSuchElementException as e:
            self.logger.error(f"item_price が見つかりません:{e}")

        try:
            self.logger.debug(f"スプシのタイトルに入力する文言 :{self.spreadsheet_data.get_item_price()}")
            self.logger.debug(" item_price 入力開始")

            # 絵文字があるため一度クリップボードに入れ込んでコピーする
            pyperclip.copy(self.spreadsheet_data.get_item_price())

            # コピペをSeleniumのKeysを使って行う
            item_price_input.send_keys(self.spreadsheet_data.get_item_price())

            self.logger.debug(" item_price 入力完了")

        # もし要素が見つからない場合
        except NoSuchElementException as e:
            self.logger.error(f"指定した入力予測欄 が見つかりません: {e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

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
            self.logger.error(f" check_box_Push が見つかりません:{e}")

        check_box.click()

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} 次のページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 実行処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------

#! deployする際に「reCAPTCHAあり」の場合に利用
#TODO 手直し必要

    def recap_deploy(self):
        '''reCAPTCHA検知してある場合は2CAPTCHAメソッドを実行'''
        try:
            # 現在のURL
            current_url = self.chrome.current_url
            self.logger.debug(current_url)
            # sitekeyを検索
            elements = self.chrome.find_elements_by_css_selector('[data-sitekey]')
            if len(elements) > 0:
                self.logger.info(f"{self.site_name} reCAPTCHA処理実施中")


                # solveRecaptchaファイルを実行
                try:
                    self.recaptcha_breakthrough.recaptchaIfNeeded(current_url)
                    self.logger.info(f"{self.site_name} reCAPTCHA処理、完了")

                except Exception as e:
                    self.logger.error(f"{self.site_name} reCAPTCHA処理に失敗しました: {e}")
                    # ログイン失敗をライン通知


                self.logger.debug(f"{self.site_name} クリック開始")

                # deploy_btn 要素を見つける
                deploy_btn = self.chrome.find_element_by_xpath(self.deploy_btn_xpath)

                # ボタンが無効化されているか確認し、無効化されていれば有効にする
<<<<<<< HEAD
<<<<<<< HEAD
                self.chrome.execute_script("document.getElementByXPATH(self.deploy_btn_xpath).disabled = false;")
=======
                # self.chrome.execute_script("document.getElementByXPATH(self.deploy_btn_xpath).disabled = false;")
>>>>>>> 4346100b5c7c891dcd38f08bd909138f3437d368
=======
                # self.chrome.execute_script("document.getElementByXPATH(self.deploy_btn_xpath).disabled = false;")
>>>>>>> 4346100b5c7c891dcd38f08bd909138f3437d368

                # ボタンをクリックする
                deploy_btn.click()

            else:
                self.logger.info(f"{self.site_name} reCAPTCHAなし")

                login_button = self.chrome.find_element_by_xpath(self.login_button_xpath)
                self.logger.debug(f"{self.site_name} ボタン捜索完了")

                deploy_btn.click()
                self.logger.debug(f"{self.site_name} クリック完了")

        # recaptchaなし
        except NoSuchElementException:
            self.logger.info(f"{self.site_name} reCAPTCHAなし")

            login_button = self.chrome.find_element_by_xpath(self.login_button_xpath)
            self.logger.debug(f"{self.site_name} ボタン捜索完了")


            # ログインボタンクリック
            try:
                deploy_btn.click()
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
            self.logger.error(f"{self.site_name} 2CAPTCHAの処理を実行中にエラーが発生しました: {e}")

        time.sleep(3)


=======
>>>>>>> parent of a8ecfdd (スクレイピング最後まで完了)

# ----------------------------------------------------------------------------------
#! 「reCAPTCHAなし」でdeploy

    def deploy_btnPush(self):
        '''出品ページにあるすべての入力が完了したあとに押す「出品する」というボタン→ deploy_btn を見つけて押す'''
        try:
            # deploy_btnを探して押す
            self.logger.debug(" deploy_btn を特定開始")
            deploy_btn = self.chrome.find_element_by_xpath(self.deploy_btn_xpath)
            self.logger.debug(" deploy_btn を発見")

        except NoSuchElementException as e:
            self.logger.error(f" deploy_btn が見つかりません:{e}")

        deploy_btn.click()

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} 次のページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 実行処理中にエラーが発生: {e}")


=======
>>>>>>> 7cddafa4b48b547c09391ee3ca214746c9c984ae
# ----------------------------------------------------------------------------------










#TODO メインメソッド
#TODO ここにすべてを集約させる

    def site_operation(self):
        '''メインメソッド'''
        self.logger.debug(f"{__name__}: 処理開始")

        self.cookie_login()
        self.lister_btnPush()
        self.photo_upload()
        self.title_input()
<<<<<<< HEAD
        self.item_title()
        self.item_text()
        self.level_input()
        self.rank_input()
        self.legend_input()
        self.item_price()
        self.check_box_Push()
        self.recap_deploy()

        time.sleep(30)
=======
>>>>>>> parent of a8ecfdd (スクレイピング最後まで完了)

        self.logger.debug(f"{__name__}: 処理完了")




# ----------------------------------------------------------------------------------


#TODO メインメソッドを非同期処理に変換
    # 同期メソッドを非同期処理に変換
    async def site_operation_async(self):
        loop = asyncio.get_running_loop()

        # ブロッキング、実行タイミング、並列処理などを適切に行えるように「functools」にてワンクッション置いて実行
        await loop.run_in_executor(None, functools.partial(self.site_operation))