FROM python:3.9.6
ENV PYTHONUNBUFFERED=1
COPY . /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 8002
