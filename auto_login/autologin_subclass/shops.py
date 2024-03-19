# coding: utf-8
# ----------------------------------------------------------------------------------
# 非同期処理 Cookie保存クラス
# 自動ログインするためのCookieを取得
# 今後、サイトを追加する場合にはクラスを追加していく=> 増え過ぎた場合は別ファイルへ

# 2023/3/9制作

# ----------------------------------------------------------------------------------


import os

from dotenv import load_dotenv

# 自作モジュール
from auto_login.getCookie import GetCookie

load_dotenv()  # .env ファイルから環境変数を読み込む


# 1----------------------------------------------------------------------------------


class Gametrade(GetCookie):
    def __init__(self, loginurl, userid, password, cookies_file_name, debug_mode=False):
        self.login_url = loginurl
        self.user_id = userid
        self.password = password
        self.cookies_file_name = cookies_file_name
        # 親クラスにて定義した引数をここで引き渡す
        # configの内容をここで全て定義
        self.config = {
            "site_name": "GAMETRADE",
            "userid_xpath": "//input[@id='session_email']",
            "password_xpath": "//input[@id='session_password']",
            "login_button_xpath": "//button[@type='submit']",
            "login_checkbox_xpath": "",
            "user_element_xpath": "//div[@class='user']",
        }

        super().__init__( loginurl, userid, password, cookies_file_name, self.config,  debug_mode=debug_mode)

    # getOrElseは実行を試み、失敗した場合は引数で指定した値を返す
    async def getOrElse(self):
        # 継承してるクラスのメソッドを非同期処理して実行
        # initにて初期化済みのためconfigを渡すだけでOK
        await self.cookie_get_async()


# ２----------------------------------------------------------------------------------


