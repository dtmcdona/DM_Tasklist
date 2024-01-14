FROM ubuntu:bionic-20230530

RUN apt-get update && apt-get install python3.8 tesseract-ocr python3-pip curl unzip -yf
# Install Chrome
RUN apt-get update -y
RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb
RUN dpkg -i /chrome.deb || apt-get install -yf
RUN rm /chrome.deb
RUN apt-get install -y dbus-x11
RUN apt-get -y install libssl1.0-dev
RUN curl https://chromedriver.storage.googleapis.com/103.0.5060.134/chromedriver_linux64.zip -o /usr/local/bin/chromedriver.zip
RUN cd /usr/local/bin && unzip chromedriver.zip
RUN chmod +x /usr/local/bin/chromedriver
USER root
RUN apt update
RUN apt-get install -y poppler-utils
RUN apt-get install build-essential binutils gcc
RUN apt-get install libenchant1c2a -y
RUN apt-get clean
RUN apt install -y python3 python3-pip
RUN DEBIAN_FRONTEND=noninteractive apt install -y python3-xlib python3-tk python3-dev
RUN apt install -y xvfb xserver-xephyr python3-tk python3-dev
RUN apt-get install -y scrot
RUN Xvfb :99 -ac &
RUN export DISPLAY=:99
RUN mkdir /app
COPY requirements.txt /app
WORKDIR /app
RUN : \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        software-properties-common \
    && add-apt-repository -y ppa:deadsnakes \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.8-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && :

RUN python3.8 -m venv /venv
ENV PATH=/venv/bin:$PATH
RUN /bin/bash -c "source /venv/bin/activate"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./app /app