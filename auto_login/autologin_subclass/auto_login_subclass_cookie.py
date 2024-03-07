# coding: utf-8
# ----------------------------------------------------------------------------------
# 非同期処理 Cookie保存クラス
# 自動ログインするためのCookieを取得
# 今後、サイトを追加する場合にはクラスを追加していく=> 増え過ぎた場合は別ファイルへ

# 2023/2/9制作

# １----------------------------------------------------------------------------------
from dotenv import load_dotenv
import os

# 自作モジュール
from auto_login.auto_login_cookie import AutoLogin

load_dotenv()  # .env ファイルから環境変数を読み込む

class IfNeeded(AutoLogin):
    def __init__(self, debug_mode=False):
        super().__init__(debug_mode=debug_mode)

        self.site_name = "GAMETRADE"
        self.url_game_trade = os.getenv('GAME_TRADE_LOGIN_AFTER_URL')  # login_url
        self.id_game_trade = os.getenv('GAME_TRADE_ID_1')  # userid
        self.password_game_trade = os.getenv('GAME_TRADE_PASS_1')  # password
        self.userid_xpath_game_trade = "//input[@name='login_id']"  # userid_xpath
        self.password_xpath_game_trade = "//input[@name='password']"  # password_xpath
        self.login_button_xpath_game_trade = "//button[@name='submit']"  # login_button_xpath
        self.cart_element_xpath_game_trade = "//li[@class='header_cart_link']"  # cart_element_xpath
        self.remember_box_xpath_game_trade = "//label[contains(text(), 'ブラウザを閉じてもログインしたままにする')]"  # remember_box_xpath
        self.cookies_file_name_game_trade = "game_trade_cookie_file.pkl"  # cookies_file_name


    async def auto_login_game_trade_async(self):
        await self.auto_login_async(
            self.site_name,
            self.url_game_trade,
            self.id_game_trade,
            self.password_game_trade,
            self.userid_xpath_game_trade,
            self.password_xpath_game_trade,
            self.login_button_xpath_game_trade,
            self.cart_element_xpath_game_trade,
            self.remember_box_xpath_game_trade,
            self.cookies_file_name_game_trade
        )


# ２----------------------------------------------------------------------------------


