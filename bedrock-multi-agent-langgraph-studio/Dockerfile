# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only necessary files first (for caching)
COPY pyproject.toml poetry.lock* requirements.txt* ./

# Install dependencies (choose one of the two methods below)
# -- Poetry (if you're using it)
RUN pip install poetry && poetry config virtualenvs.create false \
  && poetry install --no-root --no-interaction --no-ansi

# -- Or requirements.txt
# RUN pip install -r requirements.txt

# Copy app source
COPY . .

# Set environment variables (optional for dev)
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Default command
#ENTRYPOINT ["python", "runner.py"]

