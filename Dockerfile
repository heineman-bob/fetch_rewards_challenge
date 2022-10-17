from python:3.10.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80", "--reload"]

