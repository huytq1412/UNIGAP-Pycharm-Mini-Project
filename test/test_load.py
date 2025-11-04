import unittest
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from source.load import loadtodb
from pandas.testing import assert_frame_equal

# Get current file directory
current_dir = os.path.dirname(__file__)

# Get project root directory
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Get file .env directory
env_path = os.path.join(project_dir, '.env')

# Connect to file .env
load_dotenv(dotenv_path=env_path)

db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASS')

db_conn_uri = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

tgt_table = 'Test_JobList'

class TestLoadToDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run 1 time before all test cases.
        try:
            cls.engine = create_engine(db_conn_uri)
            print("--- Đã kết nối tới Database Test thành công ---")
        except Exception as e:
            raise unittest.SkipTest(f"Không thể kết nối DB Test. Lỗi: {e}")

    def setUp(self):
        # Run before each test case.
        self.tgt_table = tgt_table

        try:
            with self.engine.begin() as connection:
                connection.execute(text(f"DROP TABLE IF EXISTS {self.tgt_table}"))
        except Exception as e:
            self.fail(f"setUp failed: Cannot delete table. Error: {e}")

    def tearDown(self):
        try:
            with self.engine.begin() as connection:
                connection.execute(text(f"DROP TABLE IF EXISTS {self.tgt_table}"))
        except Exception as e:
            pass

    def getdata_fromdb(self):
        # Get data from database
        try:
            df = pd.read_sql(f"SELECT * FROM {self.tgt_table}", self.engine)
            return df
        except Exception as e:
            return pd.DataFrame()

    def test_loadtodb(self):
        # Test data loading into database
        print("\nRun Test: Load data into database")

        # Create sample dataframe
        sample_data = pd.DataFrame({
            'created_date': [pd.to_datetime('2025-01-01').date()],
            'job_title': ['Tester'],
            'company': ['Test Company'],
            'salary': ['10 - 20 triệu'],
            'address': ['Hà Nội'],
            'time': ['Còn 10 ngày'],
            'link_description': ['http://www.google.com'],
            'min_salary': [10000000.0],
            'max_salary': [20000000.0],
            'unit': ['VND'],
            'city': ['Hà Nội'],
            'district': [None],
            'job_group': ['Software Engineer']
        })

        # Load data into database
        loadtodb(sample_data, db_conn_uri, self.tgt_table)

        db_data = self.getdata_fromdb()

        # Remove id column from db_data
        if 'id' in db_data.columns:
            db_data = db_data.drop(columns=['id'])

        # Sort the dataframes for ease of comparison
        sample_data = sample_data[sorted(sample_data.columns)]
        db_data = db_data[sorted(db_data.columns)]

        # Test if the sample dataframe and the dataframe taken from the database are the same
        assert_frame_equal(sample_data, db_data, check_dtype=False)

    def test_rollback(self):
        # Test logic ROLLBACK.
        print("\nChạy Test: Logic ROLLBACK...")

        # Create sample dataframe
        sample_data = pd.DataFrame({
            'created_date': [pd.to_datetime('2025-01-01').date()],
            'job_title': ['Tester'],
            'company': ['Test Company'],
            'salary': ['10 - 20 triệu'],
            'address': ['Hà Nội'],
            'time': ['Còn 10 ngày'],
            'link_description': ['http://www.google.com'],
            'min_salary': ['min salary'], # Wrong datatype (must be NUMERIC)
            'max_salary': ['max salary'], # Wrong datatype (must be NUMERIC)
            'unit': ['VND'],
            'city': ['Hà Nội'],
            'district': [None],
            'job_group': ['Software Engineer']
        })

        # Load data into database
        loadtodb(sample_data, db_conn_uri, self.tgt_table)

        db_data = self.getdata_fromdb()

        # Check the length of dataframe db_data, if = 0 means error -> ROLLBACK successful
        self.assertEqual(len(db_data), 0)

if __name__ == '__main__':
    unittest.main()