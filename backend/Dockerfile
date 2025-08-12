FROM python:3.11-slim

WORKDIR /app

COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run the app
CMD ["python", "main.py"]