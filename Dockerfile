# Use official Python slim image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy everything into the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Ensure evidence and upload folders exist
RUN mkdir -p evidence upload data scripts

# Rebuild the database from YAML zip if present
RUN if [ -f upload/yamls.zip ]; then \
        python3 scripts/unzip_and_rebuild.py; \
    else \
        echo "⚠️  No yamls.zip found. Skipping rebuild."; \
    fi

# Streamlit uses port 8501
EXPOSE 8501

# Start Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
