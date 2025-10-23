import pandas as pd
from source.transform import cleaning_data
from source.load import loadtodb

def etl(data_path, db_conn_uri):
    try:
        # Extract the data from .csv file.
        df = pd.read_csv(data_path, delimiter=',')

        # Transform the data
        df['created_date'] = pd.to_datetime(df['created_date'])

        # 4. Load the transformed data into the "employees" table in the Microsoft SQL (or any SQL) database.
        if df['id'].isnull().any():
            raise ValueError("Dữ liệu nguồn chứa 'id' không hợp lệ.")
        if df['id'].duplicated().any():
            raise ValueError("Dữ liệu nguồn chứa 'id' nhân viên trùng lặp.")

        tgt_table = 'JobList'

        loadtodb(df, db_conn_uri, tgt_table)

    except FileNotFoundError :
        print(f"Lỗi không tìm thấy file.")
    except ValueError:
        print(f"Lỗi dữ liệu.")
    except Exception as e:
        print(f"Đã xảy ra lỗi.")