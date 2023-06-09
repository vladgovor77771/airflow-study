FROM apache/airflow:2.5.3
RUN python --version && sleep 5
USER root
RUN apt-get update
RUN apt-get install -y gcc musl-dev
USER airflow
RUN pip install --user --upgrade pip
RUN pip install python-binance
