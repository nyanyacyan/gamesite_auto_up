# coding: utf-8
# ----------------------------------------------------------------------------------
# 非同期処理 Cookie保存クラス
# 自動ログインするためのCookieを取得
# 今後、サイトを追加する場合にはクラスを追加していく=> 増え過ぎた場合は別ファイルへ

# 2023/2/9制作

# ----------------------------------------------------------------------------------


from dotenv import load_dotenv
import os

# 自作モジュール
from auto_login.auto_login_cookie import NoCookieLogin

load_dotenv()  # .env ファイルから環境変数を読み込む


# 1----------------------------------------------------------------------------------


class Gametrade(NoCookieLogin):
    def __init__(self, debug_mode=False):
        # 親クラスにて定義した引数をここで引き渡す
        # configの内容をここで全て定義
        config_xpath = {
            "site_name": "GAMETRADE",
            "login_url": os.getenv('GAME_TRADE_LOGIN_AFTER_URL'),
            "userid": os.getenv('GAME_TRADE_ID_1'),
            "password": os.getenv('GAME_TRADE_PASS_1'),
            "userid_xpath": "//input[@name='login_id']",
            "password_xpath": "//input[@name='password']",
            "login_button_xpath": "//button[@name='submit']",
            "user_element_xpath": "//div[@class='user']",
            "cookies_file_name": "game_trade_cookie_file.pkl"
        }

        super().__init__(config_xpath, debug_mode=debug_mode)

    # getOrElseは実行を試み、失敗した場合は引数で指定した値を返す
    async def getOrElse(self, config_xpath):
        # 継承してるクラスのメソッドを非同期処理して実行
        # initにて初期化済みのためconfig_xpathを渡すだけでOK
        await self.no_cookie_login_async(config_xpath)


# ２----------------------------------------------------------------------------------


