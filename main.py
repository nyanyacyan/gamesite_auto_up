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

    if relative_path:
        full_path = os.path.join(script_dir, relative_path)

    else:
        full_path = script_dir

    return full_path


# ----------------------------------------------------------------------------------
# async def main_define(main_url, cookies_file_name, image, gametitle, sheet_url, account_id, semaphore):
#     gametrade = GametradeProcess(main_url, cookies_file_name, image, gametitle, sheet_url, account_id)


async def main_define(main_url, cookies_file_name, image, sheet_url, account_id, semaphore):
    gametrade = GametradeProcess(main_url, cookies_file_name, image, sheet_url, account_id)

    async with semaphore:

        await gametrade.process()


# ----------------------------------------------------------------------------------
# 並列処理の間にsleepを入れる

async def process_account(account, semaphore, delay=0): 

    await asyncio.sleep(delay)

    return await main_define(account["main_url"], account["cookies_file_name"], account["image"], account["sheet_url"], account["account_id"], semaphore)


# ----------------------------------------------------------------------------------

async def main():
    accounts = [
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_A"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_A")),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_A"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_A"),
        },
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_B"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_B")),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_B"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_B"),
        },
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_C"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_C")),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_C"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_C"),
        },
        {
            "main_url" : os.getenv("GAME_TRADE_MAIN_URL"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_D"),
            "image" : get_fullpath(os.getenv("GAME_TRADE_IMAGE_D")),
            "sheet_url" : os.getenv("GAME_TRADE_SHEET_URL_D"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_D"),
        },

    ]

    # 最大で処理できる数を2つまでに絞り込み
    semaphore = asyncio.Semaphore(2)

    for i in range(0, len(accounts), 2):  # 2つのタスクごとに処理

        tasks = []

        # accountsの中に「image」があるものだけ実施
        if i < len(accounts) and accounts[i]["image"]:
            print(f"Processing account {i}: {accounts[i]}")  # デバッグ出力
            # 最初のタスクは遅らせない
            tasks.append(process_account(accounts[i], semaphore, delay=0))

        if i+1 < len(accounts) and accounts[i+1]["image"]:
            print(f"Processing account {i+1}: {accounts[i+1]}")  # デバッグ出力
            # 2つ目は15秒遅らせる
            tasks.append(process_account(accounts[i+1], semaphore, delay=60))

        try:
            await asyncio.gather(*tasks)

        except Exception as e:
            print(f"アカウント入力なし: {e}")
            continue


# ----------------------------------------------------------------------------------


if __name__ == "__main__":
    asyncio.run(main())


# ----------------------------------------------------------------------------------