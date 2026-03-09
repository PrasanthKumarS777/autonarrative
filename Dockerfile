# Using Python 3.11 slim image as the base
# Slim version reduces the final image size significantly compared to the full image
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy requirements first before copying code
# Docker caches this layer so reinstalling packages is skipped if requirements did not change
COPY requirements.txt .

# Install all Python dependencies
# No cache flag keeps the image size smaller by not storing pip cache inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Create necessary directories inside the container
RUN mkdir -p data/raw data/processed logs reports

# Expose port 8501 which is the default Streamlit port
EXPOSE 8501

# Default command runs the full pipeline first then launches the dashboard
CMD ["sh", "-c", "python main.py && streamlit run src/dashboard.py --server.port=8501 --server.address=0.0.0.0"]
