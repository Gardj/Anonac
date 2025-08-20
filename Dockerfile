FROM python:3.11.11-slim

WORKDIR /anonac

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /anonac

CMD ["python", "-m", "anonac.main"]


