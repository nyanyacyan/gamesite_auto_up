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
from site_operations.site_operations import SiteOperations

load_dotenv()  # .env ファイルから環境変数を読み込む


# 1----------------------------------------------------------------------------------


class OpGametrade(SiteOperations):
    def __init__(self, chrome, main_url, debug_mode=False):
        self.main_url = main_url
        # 親クラスにて定義した引数をここで引き渡す
        # configの内容をここで全て定義
        self.config_xpath = {
            "site_name": "GAMETRADE",
            "cookies_file_name": "game_trade_cookie_file.pkl",
            "lister_btn_xpath" : "//div[@class='exhibit-exhibit-button']/a",
            "deploy_btn_xpath" : "//button[@type='submit' and contains(text(), '出品する')]"
        }

        super().__init__(chrome, main_url, self.config_xpath, debug_mode=debug_mode)

    # getOrElseは実行を試み、失敗した場合は引数で指定した値を返す
    async def OpGetOrElse(self):
        # 継承してるクラスのメソッドを非同期処理して実行
        # initにて初期化済みのためconfig_xpathを渡すだけでOK
        await self.site_operation_async()


# ２----------------------------------------------------------------------------------