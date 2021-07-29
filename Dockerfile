FROM python:alpine

COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt && rm requirements.txt

COPY main.py /main.py
ENTRYPOINT ["python3", "main.py"]