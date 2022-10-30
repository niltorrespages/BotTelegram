FROM python:3.9

ADD botTelegram.py botTelegram.py

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "botTelegram.py"]

