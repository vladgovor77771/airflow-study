from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.sensors.python import PythonSensor
from candle import CandleInfo
from psycopg2.extras import RealDictCursor
from typing import List

import binance_
import huobi_



def is_binance_alive(**kwargs):
    return binance_.check_alive()

def is_huobi_alive(**kwargs):
    return huobi_.check_alive()

class CryptoPostgresHook(PostgresHook):
    def __init__(self, postgres_conn_id: str, *args, **kwargs):
        super().__init__(postgres_conn_id=postgres_conn_id, *args, **kwargs)

    def insert_candle(self, candle: CandleInfo):
        sql = """
            INSERT INTO crypto.candles(market, symbol, timestamp_from, timestamp_to, open_price, close_price, high_price, low_price, volume, trades_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (candle.market, candle.symbol, candle.timestamp_from, candle.timestamp_to, candle.open_price, candle.close_price, candle.high_price, candle.low_price, candle.volume, candle.trades_amount)
        self.run(sql, parameters=params)

    def get_candles(self, utc_timestamp) -> List[CandleInfo]:
        sql = """
            SELECT * FROM crypto.candles WHERE timestamp_from >= %s
        """
        params = (utc_timestamp,)
        cursor = self.get_conn().cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        candles = [CandleInfo(**row) for row in rows]

        return candles



def get_huobi_candles(**kwargs):
    candle = huobi_.get_candles("btcusdt", 2)[1]
    db_hook = CryptoPostgresHook(postgres_conn_id="data-postgres")
    db_hook.insert_candle(candle)


def get_binance_candles(**kwargs):
    candle = binance_.get_candles("BTCUSDT", 2)[0]
    db_hook = CryptoPostgresHook(postgres_conn_id="data-postgres")
    db_hook.insert_candle(candle)


def analyze_candles(**kwargs):
    db_hook = CryptoPostgresHook(postgres_conn_id="data-postgres")

    # Получить данные о свечах из базы данных
    timestamp_from = int((datetime.now() - timedelta(minutes=1)).timestamp())
    candles = db_hook.get_candles(timestamp_from)
    return candles


def print_candles(candles, **kwargs):
    print(candles)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 4, 28),
}

dag = DAG(
    'crypto_dag',
    default_args=default_args,
    description='A DAG for parsing, saving and analyzing data from markets',
    schedule_interval=timedelta(minutes=1),
    catchup=False
)

huobi_parse_candles = PythonOperator(
    task_id='get_huobi_candles',
    python_callable=get_huobi_candles,
    provide_context=True,
    dag=dag
)

binance_parse_candles = PythonOperator(
    task_id='get_binance_candles',
    python_callable=get_binance_candles,
    provide_context=True,
    dag=dag
)

binance_sensor = PythonSensor(
    task_id='is_binance_alive',
    python_callable=is_binance_alive,
    dag=dag
)

huobi_sensor = PythonSensor(
    task_id='is_huobi_alive',
    python_callable=is_huobi_alive,
    dag=dag
)

analyze_task = PythonOperator(
    task_id='analyze_candles',
    python_callable=analyze_candles,
    dag=dag
)

print_task = PythonOperator(
    task_id='print_candles',
    python_callable=print_candles,
    op_args=[analyze_task.output],
    dag=dag
)

binance_sensor >> binance_parse_candles
huobi_sensor >> huobi_parse_candles
[huobi_parse_candles, binance_parse_candles] >> analyze_task >> print_task
