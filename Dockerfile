FROM python:3.10

COPY . .
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package -r requirements.txt

CMD ["python3", "main.py"]
