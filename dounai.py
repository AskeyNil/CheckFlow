import requests
import time
import re
from typing import Optional
from requests import Response
import os
import json
from pathlib import Path
from http.cookiejar import MozillaCookieJar


def feishu_bot(card: dict) -> None:
    """
    使用 飞书机器人 推送消息。
    """
    fskey = os.environ.get("FSKEY", "")
    if not fskey:
        print("飞书 服务的 FSKEY 未设置!!\n取消推送")
        return
    print("飞书 服务启动")

    url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{fskey}"
    data = {"msg_type": "interactive", "card": card}
    response = requests.post(url, data=json.dumps(data)).json()

    if response.get("StatusCode") == 0:
        print("飞书 推送成功！")
    else:
        print("飞书 推送失败！错误信息如下：\n", response)


class Account:
    username: str
    password: str
    at: str

    def __init__(self, **kargs) -> None:
        self.username = kargs["username"]
        self.password = kargs["password"]
        self.at = kargs["at"]


class DounaiManager:
    def __init__(self, config: Path):
        users = [
            Account(**user) for user in json.loads(config.read_text())["dounai_users"]
        ]
        self.cards = {
            "header": {
                "template": "blue",
                "title": {"tag": "plain_text", "content": "【豆豆豆奶】签到系统"},
            },
            "elements": [],
        }
        self.elements: list = self.cards["elements"]
        self.base_url = self.__get_base_url()
        self.elements.append(
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "豆豆豆奶🍼"},
                        "type": "default",
                        "multi_url": {
                            "url": self.base_url,
                        },
                    }
                ],
            },
        )
        for user in users:
            if DounaiCheckin(user.username, user.password, self.base_url).check_in():
                self.elements.append(
                    {
                        "tag": "div",
                        "text": {
                            "content": f"**{user.username}**：<font color='green'> 签到成功 </font> ",
                            "tag": "lark_md",
                        },
                    }
                )
            else:
                self.elements.append(
                    {
                        "tag": "div",
                        "text": {
                            "content": f"**{user.username}**：<font color='red'> 签到失败 </font> <at email={user.at}></at>",
                            "tag": "lark_md",
                        },
                    },
                )
        feishu_bot(self.cards)

    def __get_base_url(self) -> Optional[str]:
        response = requests.get("https://doubledou.win")
        if response.status_code == 200:
            response.encoding = "utf-8"
            regex = r"新地址([0-9a-zA-Z]+\.[0-9a-zA-Z]+)"
            result = re.search(regex, response.text)
            if result:
                return result.group(1)
            else:
                print("无法获取 dounai 的链接.")
        else:
            print("无法获取 dounai 的链接.")


class DounaiCheckin:
    def __init__(self, username: str, password: str, base_url: str) -> None:
        self.username = username
        self.password = password
        self.base_url = base_url
        self.session = requests.Session()
        self.is_login = False
        self.cookies_file = f"/tmp/dounai.{username}.cookies"
        self.cookies = MozillaCookieJar()
        self.session.cookies = self.cookies
        if os.path.isfile(self.cookies_file):
            self.is_login = True
            self.cookies.load(self.cookies_file, True, True)

    def check_in(self):
        # 判断 cookies
        if self.is_login:
            if self.__check_in():
                return True
        if not self.__login():
            return False
        return self.__check_in()

    def __post(self, url, data={}, retry_times=5) -> Optional[Response]:
        for _ in range(retry_times):
            try:
                return self.session.post(url, data, timeout=20)
            except:
                time.sleep(1)

    def __check_in(self) -> bool:
        print("准备签到..")
        response = self.__post(self.checkin_url)

        if response and response.status_code == 200:
            response.encoding = "utf-8"
            try:
                result = response.json()
                print(result)
                return True
            except:
                print("登录超时, 请重新登录..")
                return False

        print("签到失败...")
        return False

    def __login(self) -> bool:
        print(f"准备登录 {self.username}")
        response = self.__post(
            self.login_url, {"email": self.username, "passwd": self.password}
        )

        if response and response.status_code == 200:
            self.cookies.save(self.cookies_file, True, True)
            print(response.json()["msg"])
            return True
        else:
            print("登录失败")
            return False

    @property
    def login_url(self):
        return f"https://{self.base_url}/auth/login"

    @property
    def checkin_url(self):
        return f"https://{self.base_url}/user/checkin"


DounaiManager(Path("./config.json"))
