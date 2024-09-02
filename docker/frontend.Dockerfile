FROM python:3.11.7-slim-bookworm

# Install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-tk tk-dev && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY ./frontend/requirements.txt /usr/local/src/myscripts/requirements.txt 
WORKDIR /usr/local/src/myscripts
RUN pip install --no-cache-dir -r requirements.txt

# Install Jupyter and IPython kernel
RUN pip install jupyter ipykernel

# Create and install the IPython kernel
RUN python -m ipykernel install --user --name python3 --display-name "Python 3"

# Copy frontend code
COPY ./frontend /usr/local/src/myscripts/frontend
WORKDIR /usr/local/src/myscripts/frontend

# Set environment variable for base directory
ENV BASE_DIR="${PYTHONPATH}:/usr/local/src/myscripts/assets/scripts"

# Expose port for Streamlit
EXPOSE 80

# Command to run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "80", "--server.enableXsrfProtection", "false"]
