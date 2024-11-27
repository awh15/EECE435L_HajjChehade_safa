FROM python:3.9-alpine

WORKDIR /app

# Copy the entire project (including shared)
COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt && pip install -r shared/requirements.txt

EXPOSE 5250

CMD ["python", "-m", "log_service.log"]
