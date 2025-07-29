FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

# for fallback. cmd will be overrided in docker-compose.yml
CMD ["python", "--version"]