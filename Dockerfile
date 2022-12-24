FROM python:3.9 as builder
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
    && pip install python-socketio
COPY . ./

FROM builder
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app ./
EXPOSE 5000
CMD ["python" , "-u" ,"main.py"]