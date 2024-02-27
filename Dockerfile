FROM python:3.12.1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

COPY init.sql /docker-entrypoint-initdb.d/

COPY dummy.sql /docker-entrypoint-initdb.d/

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
