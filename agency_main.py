# coding: utf-8
# ----------------------------------------------------------------------------------
#? Process集計クラス
# 基本はカプセル化したものを使う。
# GUIがある場合には引数にいれるものは引数に入れて渡す
# ----------------------------------------------------------------------------------
import os, asyncio
from gametrado_process import GametradeProcess


async def main_define(main_url, cookies_file_name, image, gametitle, sheet_url, account_id):
    gametrade = GametradeProcess(main_url, cookies_file_name, image, gametitle, sheet_url, account_id)


    await gametrade.agency_process()


async def agency_main():
    accounts = [
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_1"),
            "image" : os.getenv("GAME_TRADE_IMAGE_1"),
            "gametitle" : os.getenv("GAME_TRADE_TITLE_1"),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_1"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_1"),
        }
        # {
        #     "loginurl": os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_2")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_3")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_4")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_5")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_6")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_7")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_8")
        # },
    ]


    # 複数の際にはこちらを使う
    tasks = [main_define(account["main_url"], account["cookies_file_name"], account["image"], account["gametitle"], account["sheet_url"], account["account_id"]) for account in accounts]

    # すべてのタスクが完了するまで待機
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(agency_main())