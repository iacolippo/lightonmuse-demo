# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Expose port you want your app on
EXPOSE 8501

WORKDIR /app

# Install production dependencies.
COPY requirements.txt requirements.txt
COPY lightonmuse-*-py3-none-any.whl $WORKDIR
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY app.py app.py

ENV PORT=

# Run
CMD streamlit run app.py --server.port=${PORT} --browser.serverAddress="0.0.0.0"
