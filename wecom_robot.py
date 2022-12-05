import requests
from typing import List, Optional
from enum import Enum
from loguru import logger
import base64 as b64
import hashlib
import os

class WecomRobot:
    class Type(Enum):
        TEXT = "text"
        MARKDOWN = "markdown"
        IMAGE = "image"
        # 图文类型
        NEWS = "news"
        FILE = "file"
        # 模板卡片类型
        TEMPLATE_CARD = "template_card"

    def __init__(self, key) -> None:
        self.__key = key

    @property
    def webhook(self):
        return f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.__key}"

    def send_text(self,
                  content: str,
                  mentioned_list: Optional[List[str]] = None,
                  mentioned_mobile_list: Optional[List[str]] = None):
        local = locals()
        local.pop("self")
        self.__send(WecomRobot.Type.TEXT, **local)

    def send_markdown(self, content: str):
        local = locals()
        local.pop("self")
        self.__send(WecomRobot.Type.MARKDOWN, **local)

    def send_image(self, image_url: str):
        if image_url.startswith("http"):
            img_src = requests.get(image_url)
            if img_src.status_code != 200:
                logger.error("图片获取失败.")
                return
            content = img_src.content
        else:
            if not os.path.exists(image_url):
                logger.error(f"图片({image_url})不存在.")
                return
            with open(image_url, "rb") as f:
                content = f.read()

        base64 = str(b64.b64encode(content), 'utf-8')
        md5_ = hashlib.md5()
        md5_.update(content)
        md5 = md5_.hexdigest()

        self.__send(WecomRobot.Type.IMAGE, base64=base64, md5=md5)

    def __send(self, type: Type, **kwargs):
        headers = {
            "Content-Type": "application/json"
        }
        json_data = {
            "msgtype": type.value,
            type.value: kwargs
        }
        response = requests.post(self.webhook, headers=headers, json=json_data)
        if response.status_code == 200:
            logger.info("发送成功...")
            logger.info(response.text)
        else:
            logger.info("发送失败...")


