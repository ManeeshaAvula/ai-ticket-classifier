FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so this layer is cached.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and training data.
COPY app ./app
COPY train_model.py .
COPY data ./data

# Train the model at build time so the image is self-contained.
RUN python train_model.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
