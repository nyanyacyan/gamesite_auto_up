# coding: utf-8
# ----------------------------------------------------------------------------------
#? Process集計クラス
# 基本はカプセル化したものを使う。
# GUIがある場合には引数にいれるものは引数に入れて渡す
# ----------------------------------------------------------------------------------
import os, asyncio
from gametrado_process import GametradeProcess


# ----------------------------------------------------------------------------------
# 写真のフルパスのために定義

def get_fullpath(relative_path):
    # 絶対path
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # # item_photo の絶対path
    # item_photo_dir = os.path.join(script_dir, 'item_photo')

    # 繋げることを定義して返す
    return os.path.join(script_dir, relative_path)


# ----------------------------------------------------------------------------------


async def main_define(main_url, cookies_file_name, image, gametitle, sheet_url, account_id, semaphore):
    gametrade = GametradeProcess(main_url, cookies_file_name, image, gametitle, sheet_url, account_id)

    async with semaphore:

        await gametrade.agency_process()


# ----------------------------------------------------------------------------------
# 並列処理の間にsleepを入れる

async def process_account(account, semaphore, delay=0):

    await asyncio.sleep(delay)

    return await main_define(account["main_url"], account["cookies_file_name"], account["image"], account["gametitle"], account["sheet_url"], account["account_id"], semaphore)


# ----------------------------------------------------------------------------------


async def agency_main():
    accounts = [
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_E"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_E")),
            "gametitle" : os.getenv("GAME_TRADE_TITLE_E"),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_E"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_E"),
        },
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_F"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_F")),
            "gametitle" : os.getenv("GAME_TRADE_TITLE_F"),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_F"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_F"),
        },
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_G"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_G")),
            "gametitle" : os.getenv("GAME_TRADE_TITLE_G"),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_G"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_G"),
        },
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_H"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_H")),
            "gametitle" : os.getenv("GAME_TRADE_TITLE_H"),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_H"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_H"),
        },

    ]


    # 最大で処理できる数を2つまでに絞り込み
    semaphore = asyncio.Semaphore(2)

    for i in range(0, len(accounts), 2):  # 2つのタスクごとに処理

        tasks = []

        # accountsの中に「image」があるものだけ実施
        if i < len(accounts) and accounts[i]["image"]:

            # 最初のタスクは遅らせない
            tasks.append(process_account(accounts[i], semaphore, delay=0))

        if i+1 < len(accounts) and accounts[i+1]["image"]:

            # 2つ目は15秒遅らせる
            tasks.append(process_account(accounts[i+1], semaphore, delay=60))


        try:
            await asyncio.gather(*tasks)

        except Exception as e:
            print(f"アカウント入力なし: {e}")
            continue


# ----------------------------------------------------------------------------------


if __name__ == "__main__":
    asyncio.run(agency_main())


# ----------------------------------------------------------------------------------