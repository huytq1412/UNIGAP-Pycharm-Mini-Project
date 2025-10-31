import pandas as pd
from transform import cleaning_data
from load import loadtodb

def etl(data_path, db_conn_uri, tgt_table):
    try:
        # Extract the data from .csv file.
        df = pd.read_csv(data_path, delimiter=',')

        # Transform the data
        df['created_date'] = pd.to_datetime(df['created_date'])
        cleaning_data(df)

        # # Load the transformed data into the target table
        loadtodb(df, db_conn_uri, tgt_table)

    except FileNotFoundError :
        print(f"File not found error.")
    except ValueError:
        print(f"Data error.")
    except Exception as e:
        print(f"An error has occurred: {e}")

