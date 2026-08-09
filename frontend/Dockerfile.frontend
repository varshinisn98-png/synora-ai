# Use a stable, compatible Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8501
ENV BACKEND_URL=http://localhost:8000

# Set working directory
WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend codebase
COPY . /app/

# Expose Streamlit port
EXPOSE 8501

# Start Streamlit application
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]
