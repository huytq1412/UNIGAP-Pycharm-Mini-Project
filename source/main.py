import os
from dotenv import load_dotenv
from ETL import etl

if __name__ == '__main__':
    load_dotenv()

    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')
    data_path = os.environ.get('DATA_PATH')

    db_conn_uri = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

    data_path = f'{data_path}/data.csv'

    print("--- Running ETL ---")
    etl(data_path, db_conn_uri)
    print("--- ETL Finished ---\n")
