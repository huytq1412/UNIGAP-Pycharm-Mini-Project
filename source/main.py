import os
from dotenv import load_dotenv
from ETL import etl
from report import getdata_fromdb, plot_salary_distribution, plot_job_heatmap, plot_techtrend

# Get current file directory
current_dir = os.path.dirname(__file__)

# Get project root directory
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Get file .env directory
env_path = os.path.join(project_dir, '.env')

if __name__ == '__main__':
    load_dotenv(dotenv_path=env_path)

    # Get database connection
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')
    data_path = os.environ.get('DATA_PATH')

    db_conn_uri = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

    data_path = f'{data_path}/data.csv'

    tgt_table = 'JobList'

    # ETL data
    print("--- Running ETL ---")
    etl(data_path, db_conn_uri, tgt_table)
    print("--- ETL Finished ---\n")

    # Create data reports
    print("--- Running Data Analysis from PostgreSQL Data ---")
    try:
        # Get data from PostgreSQL
        df_from_db = getdata_fromdb(db_conn_uri, tgt_table)

        convert_rate = 25000
        report_path =  os.environ.get('REPORT_PATH')

        os.makedirs(report_path, exist_ok=True)

        # 1. Vẽ biểu đồ phân bố mức lương theo vị trí
        plot_salary_distribution(df_from_db, convert_rate, report_path)

        # 2. Vẽ bản đồ nhiệt (heatmap) phân bố việc làm theo khu vực
        plot_job_heatmap(df_from_db, report_path)

        # 3. Biểu đồ xu hướng công nghệ hot
        plot_techtrend(df_from_db, report_path)

        print("Reports saved to project folder.")
    except Exception as e:
        print(f"Could not run analysis: {e}")
