# Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY resumeScreener ./resumeScreener

WORKDIR /app/resumeScreener

EXPOSE 7899
EXPOSE 8345

CMD ["sh", "-c", "python app.py & python api.py"]