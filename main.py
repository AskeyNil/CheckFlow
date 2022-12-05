import time
import schedule
import wecom_robot
from loguru import logger
import ip_noti
from dounai import Dounai
import os


def get_env(name: str):
    env = os.getenv(name)
    return env if env else None


ip = ip_noti.Ip()
noti = None
if WECOM_KEY := get_env("WECOM_KEY"):
    print("123")
    noti = wecom_robot.WecomRobot(WECOM_KEY)
dounai = None
if (DOUNAI_NAME := get_env("DOUNAI_NAME")) and \
        (DOUNAI_PWD := get_env("DOUNAI_PWD")):
    dounai = Dounai(DOUNAI_NAME, DOUNAI_PWD)


def checkin():
    if dounai:
        title = dounai.checkin()
        if title:
            logger.error("签到失败了..")
            if noti:
                noti.send_markdown(title)
    else:
        logger.error("dounai 的账号密码未设置")


def get_ip():
    title = ip.get_ip()
    if title:
        logger.info("触发了更改 ip.")
        if noti:
            noti.send_markdown(title)


def main():
    checkin()
    schedule.every().day.at("08:00").do(checkin)
    schedule.every(10).seconds.do(get_ip)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
    # get_env("1")
