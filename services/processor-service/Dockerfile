FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install redis requests psycopg2-binary
CMD ["python", "main.py"]