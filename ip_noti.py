from typing import Optional
import subprocess

class Ip:
    ip: str = ""
    def get_ip(self) -> Optional[str]:
        ip = subprocess.getoutput("hostname -I").split(" ")[0]
        if self.ip == ip:
            return
        msg = f"# IP发送变更 \n\n"
        if self.ip:
            msg += f"{self.ip} -> {ip}"
        else:
            msg += f"当前 ip: {ip}"
        self.ip = ip
        return msg
