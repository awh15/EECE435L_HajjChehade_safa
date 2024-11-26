FROM python:3.9-alpine

WORKDIR /app

# Copy the entire project (including shared)
COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt && pip install -r shared/requirements.txt && pip install marshmallow-enum

EXPOSE 5200

CMD ["python", "-m", "inventory_service.inventory"]
