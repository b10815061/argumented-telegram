FROM python:3.9.7 as builder
USER ${USER}
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r ./requirements.txt \
    && pip install psycopg2 \
    && pip install python-socketio 
RUN apt-get update \
    && apt-get install -y vim
RUN pip uninstall python-socketio -y \
    && pip install python-socketio \ 
    && pip install pyinstaller

COPY . ./

FROM builder
WORKDIR /usr/src/app
COPY --from=builder . ./usr/src/app
EXPOSE 5000
RUN pyinstaller --onefile main.py