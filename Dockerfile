# Usa una base leggera con Python
FROM python:3.11-slim

# Evita input interattivi
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean

# Crea e usa una directory per l'app
WORKDIR /app

# Copia i file
COPY requirements.txt .
COPY bot.py .

# Installa i pacchetti Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando di avvio
CMD ["python", "bot.py"]
