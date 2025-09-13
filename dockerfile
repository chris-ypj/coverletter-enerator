FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
EXPOSE 8000

CMD ["streamlit", "run", "cover-letter-app/app.py", "--server.port", "8000", "--server.address", "0.0.0.0"]