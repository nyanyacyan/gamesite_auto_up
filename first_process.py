import os, asyncio
from auto_login.autologin_subclass.shops import Gametrade

#? 複数のサイトになった場合にはインスタンスを追加する
async def first_process(loginurl, userid, password):


    # インスタンス
    gemetrade = Gametrade(loginurl, userid, password)

    # youtube_to_wavメソッドを実行
    await gemetrade.getOrElse()

async def main():
    #! 同一のサイトのアカウントはここに追記
    accounts = [
        {
            "loginurl" : os.getenv("GAME_TRADE_LOGIN_URL"),
            "userid" : os.getenv("GAME_TRADE_ID_1"),
            "password" : os.getenv("GAME_TRADE_PASS_1")
        }
        # {
        #     "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
        #     "user_id": os.getenv("GAME_TRADE_ID_2"),
        #     "password": os.getenv("GAME_TRADE_PASS_2")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
        #     "user_id": os.getenv("GAME_TRADE_ID_3"),
        #     "password": os.getenv("GAME_TRADE_PASS_3")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
        #     "user_id": os.getenv("GAME_TRADE_ID_4"),
        #     "password": os.getenv("GAME_TRADE_PASS_4")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
        #     "user_id": os.getenv("GAME_TRADE_ID_5"),
        #     "password": os.getenv("GAME_TRADE_PASS_5")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
        #     "user_id": os.getenv("GAME_TRADE_ID_6"),
        #     "password": os.getenv("GAME_TRADE_PASS_6")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
        #     "user_id": os.getenv("GAME_TRADE_ID_7"),
        #     "password": os.getenv("GAME_TRADE_PASS_7")
        # },
        # {
        #     "loginurl": os.getenv("GAME_TRADE_LOGIN_URL"),
        #     "user_id": os.getenv("GAME_TRADE_ID_8"),
        #     "password": os.getenv("GAME_TRADE_PASS_8")
        # },
    ]

    # それぞれの項目を並行処理する
    tasks = [first_process(account["loginurl"], account["userid"], account["password"]) for account in accounts]

    # すべてのタスクが完了するまで待機
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())