# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential


# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the FastAPI port (8000) and Dash port (8050)
EXPOSE 8000 8050

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

