import requests
from loguru import logger
import time
import re
from typing import Optional
from requests import Response


class Dounai:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_url = self.__get_base_url()
        self.session = requests.Session()
        self.update_msg = ""

    def checkin(self) -> str:
        self.update_msg = f"# [豆豆豆奶]({self.base_url})签到系统 \n\n"
        if not self.__checkin():
            self.__login()
            if not self.__checkin(True):
                self.update_msg += "** 签到失败,请重试!!! **"
        return self.update_msg

    def __post(self, url, data={}, retry_times=5) -> Optional[Response]:
        for _ in range(retry_times):
            try:
                return self.session.post(url, data, timeout=20)
            except:
                time.sleep(1)

    def __login(self):
        logger.info(f"准备登录 {self.username}")
        self.update_msg += f"## 准备尝试登录 \n\n"

        response = self.__post(self.login_url,
                               {
                                   "email": self.username,
                                   "passwd": self.password
                               })

        if response and response.status_code == 200:
            self.update_msg += f"> 登录成功... \n\n"
            logger.info(response.json()["msg"])
        else:
            self.update_msg += f"> 登录失败... 请稍后再试 \n"
            logger.error("登录失败")

    def __checkin(self, is_retry=False) -> bool:
        msg = "准备重新尝试签到" if is_retry else "准备尝试签到"
        logger.info(f"{msg}..")
        self.update_msg += f"## {msg} \n\n"
        response = self.__post(self.checkin_url)

        if response and response.status_code == 200:
            response.encoding = "utf-8"
            try:
                result = response.json()
                self.update_msg += f"> 签到成功..\n> {result['msg']} \n\n"
                logger.info(result["msg"])
                return True
            except:
                logger.warning("登录超时, 请重新登录..")
                self.update_msg += f"> 登录超时, 请重新登录 \n\n"
                return False
        else:
            logger.error("签到失败...")
            return False

    @property
    def login_url(self):
        return f"https://{self.base_url}/auth/login"

    @property
    def checkin_url(self):
        return f"https://{self.base_url}/user/checkin"

    def __get_base_url(self) -> Optional[str]:
        response = requests.get("https://doubledou.win")
        if response.status_code == 200:
            response.encoding = "utf-8"
            regex = r"新地址([0-9a-zA-Z]+\.[0-9a-zA-Z]+)"
            result = re.search(regex, response.text)
            if result:
                return result.group(1)
            else:
                logger.error("无法获取 dounai 的链接.")
        else:
            logger.error("无法获取 dounai 的链接.")
