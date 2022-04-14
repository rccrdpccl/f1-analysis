FROM python:3.10.4-slim-buster
RUN apt-get update && apt-get install -y libx11-dev tk python3-tk &&\
 pip3 install matplotlib fastf1 pyqt5
