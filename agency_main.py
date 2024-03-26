# coding: utf-8
# ----------------------------------------------------------------------------------
#? Process集計クラス
# 基本はカプセル化したものを使う。
# GUIがある場合には引数にいれるものは引数に入れて渡す
# ----------------------------------------------------------------------------------
import os, asyncio
from gametrado_process import GametradeProcess


# ----------------------------------------------------------------------------------


def get_fullpath(relative_path):
    # 絶対path
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # # item_photo の絶対path
    # item_photo_dir = os.path.join(script_dir, 'item_photo')

    # 繋げることを定義して返す
    return os.path.join(script_dir, relative_path)


# ----------------------------------------------------------------------------------


async def main_define(main_url, cookies_file_name, image, gametitle, sheet_url, account_id):
    gametrade = GametradeProcess(main_url, cookies_file_name, image, gametitle, sheet_url, account_id)


    await gametrade.agency_process()


# ----------------------------------------------------------------------------------


async def agency_main():
    accounts = [
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_1"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_1")),
            "gametitle" : os.getenv("GAME_TRADE_TITLE_1"),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_1"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_1"),
        }
        # {
        #     "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_2"),
        #     "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_2")),
        #     "gametitle" : os.getenv("GAME_TRADE_TITLE_2"),
        #     "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_2"),
        #     "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_2"),
        # },
        # {
        #     "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_3"),
        #     "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_3")),
        #     "gametitle" : os.getenv("GAME_TRADE_TITLE_3"),
        #     "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_3"),
        #     "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_3"),
        # },
        # {
        #     "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_4"),
        #     "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_4")),
        #     "gametitle" : os.getenv("GAME_TRADE_TITLE_4"),
        #     "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_4"),
        #     "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_4"),
        # },
        # {
        #     "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_5"),
        #     "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_5")),
        #     "gametitle" : os.getenv("GAME_TRADE_TITLE_5"),
        #     "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_5"),
        #     "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_5"),
        # },
        # {
        #     "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_6"),
        #     "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_6")),
        #     "gametitle" : os.getenv("GAME_TRADE_TITLE_6"),
        #     "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_6"),
        #     "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_6"),
        # },
        # {
        #     "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_7"),
        #     "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_7")),
        #     "gametitle" : os.getenv("GAME_TRADE_TITLE_7"),
        #     "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_7"),
        #     "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_7"),
        # },
        # {
        #     "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
        #     "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_8"),
        #     "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_8")),
        #     "gametitle" : os.getenv("GAME_TRADE_TITLE_8"),
        #     "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_8"),
        #     "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_8"),
        # },
    ]


    # 複数の際にはこちらを使う
    tasks = [main_define(account["main_url"], account["cookies_file_name"], account["image"], account["gametitle"], account["sheet_url"], account["account_id"]) for account in accounts]

    # すべてのタスクが完了するまで待機
    await asyncio.gather(*tasks)


# ----------------------------------------------------------------------------------


if __name__ == "__main__":
    asyncio.run(agency_main())


# ----------------------------------------------------------------------------------