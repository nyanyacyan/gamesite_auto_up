import os, asyncio
from auto_login.autologin_subclass.shops import Gametrade


# ----------------------------------------------------------------------------------
# semaphoreはフラグみたいなもの→これがあることで一つ一つのタスクを認識できる→今回は２つまでしかない制約に対して利用

#? 複数のサイトになった場合にはインスタンスを追加する
async def first_process(loginurl, userid, password, cookies_file_name, account_id, semaphore):


    # インスタンス
    gemetrade = Gametrade(loginurl, userid, password, cookies_file_name, account_id)

    async with semaphore:
    # youtube_to_wavメソッドを実行
        await gemetrade.getOrElse()


# ----------------------------------------------------------------------------------
# 並列処理の間にsleepを入れる

async def process_account(account, semaphore, delay=0):

    await asyncio.sleep(delay)

    return await first_process(account["loginurl"], account["userid"], account["password"], account["cookies_file_name"], account["account_id"], semaphore)


# ----------------------------------------------------------------------------------


async def main():
    #! 同一のサイトのアカウントはここに追記
    accounts = [
        {
            "loginurl" : os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid" : os.getenv("GAME_TRADE_ID_A"),
            "password" : os.getenv("GAME_TRADE_PASS_A"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_A"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_A")
        },
        {
            "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid": os.getenv("GAME_TRADE_ID_B"),
            "password": os.getenv("GAME_TRADE_PASS_B"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_B"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_B")
        },
        {
            "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid": os.getenv("GAME_TRADE_ID_C"),
            "password": os.getenv("GAME_TRADE_PASS_C"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_C"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_C")
        },
        {
            "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid": os.getenv("GAME_TRADE_ID_D"),
            "password": os.getenv("GAME_TRADE_PASS_D"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_D"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_D")
        },
        {
            "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid": os.getenv("GAME_TRADE_ID_E"),
            "password": os.getenv("GAME_TRADE_PASS_E"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_E"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_E")
        },
        {
            "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid": os.getenv("GAME_TRADE_ID_F"),
            "password": os.getenv("GAME_TRADE_PASS_F"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_F"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_F")
        },
        {
            "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid": os.getenv("GAME_TRADE_ID_G"),
            "password": os.getenv("GAME_TRADE_PASS_G"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_G"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_G")
        },
        {
            "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid": os.getenv("GAME_TRADE_ID_H"),
            "password": os.getenv("GAME_TRADE_PASS_H"),
            "cookies_file_name" : os.getenv("GAME_TRADE_COOKIE_H"),
            "account_id" : os.getenv("GAME_TRADE_ACCOUNT_ID_H")
        },
    ]

    # 最大で処理できる数を2つまでに絞り込み
    semaphore = asyncio.Semaphore(2)

    for i in range(0, len(accounts), 2):  # 2つのタスクごとに処理

        tasks = []

        # accountsの中に「userid」があるものだけ実施
        if i < len(accounts) and accounts[i]["userid"]:

            # 最初のタスクは遅らせない
            tasks.append(process_account(accounts[i], semaphore, delay=0))

        if i+1 < len(accounts) and accounts[i+1]["userid"]:

            # 2つ目は15秒遅らせる
            tasks.append(process_account(accounts[i+1], semaphore, delay=30))


        try:
            await asyncio.gather(*tasks)

        except Exception as e:
            print(f"アカウント入力なし: {e}")
            continue


# ----------------------------------------------------------------------------------


if __name__ == '__main__':
    asyncio.run(main())


# ----------------------------------------------------------------------------------
