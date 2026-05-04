FROM python:3.13.2

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--port", "3300", "--host", "0.0.0.0", "--reload"]
