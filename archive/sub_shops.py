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
    def __init__(self, chrome, main_url, cookies_file_name, image, debug_mode=False):
        self.main_url = main_url
        self.cookies_file_name = cookies_file_name
        self.image = image
        # 親クラスにて定義した引数をここで引き渡す
        # configの内容をここで全て定義
        self.config = {
            "site_name": "GAMETRADE",
            "lister_btn_xpath" : "//div[@class='exhibit-exhibit-button']/a",
            "photo_file_input_xpath" : "exhibit_exhibit_images[file][]",
            "title_input_xpath" : "game_title",
            "title_predict_xpath" : f"//ul[@id='ui-id-2']//div[contains(@class, 'ui-menu-item-wrapper') and contains(text(), '{self.gametitle}')]"
        }

        super().__init__(chrome, main_url, cookies_file_name, image, self.config, debug_mode=debug_mode)

    # getOrElseは実行を試み、失敗した場合は引数で指定した値を返す
    async def OpGetOrElse(self):
        # 継承してるクラスのメソッドを非同期処理して実行
        # initにて初期化済みのためconfigを渡すだけでOK
        await self.site_operation_async()


# ２----------------------------------------------------------------------------------