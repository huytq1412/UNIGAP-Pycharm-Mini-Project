from sqlalchemy import text
from sqlalchemy import create_engine

def loadtodb(df, db_conn_uri, tgt_table):
    tmp_table = 'tmptable'

    try:
        engine = create_engine(db_conn_uri)
        print('Connected to database successfully')
    except Exception as e:
        print('Connection to database failed. Please check again.')
        return

    with engine.begin() as connection:
        try:
            connection.execute(text(f'''CREATE TABLE IF NOT EXISTS {tgt_table} (
                                            id SERIAL PRIMARY KEY,
                                            created_date DATE,
                                            job_title TEXT NOT NULL,
                                            company TEXT,
                                            salary VARCHAR(100),
                                            address TEXT,
                                            time VARCHAR(256),
                                            link_description TEXT NOT NULL UNIQUE,
                                            min_salary NUMERIC(12, 2),
                                            max_salary NUMERIC(12, 2),
                                            unit VARCHAR(25),
                                            city VARCHAR(100),
                                            district VARCHAR(100),
                                            job_group VARCHAR(100);'''))

            connection.execute(text(f'''CREATE TEMP TABLE IF NOT EXISTS {tmp_table}(
                                            id SERIAL PRIMARY KEY,
                                            created_date DATE,
                                            job_title TEXT NOT NULL,
                                            company TEXT,
                                            salary VARCHAR(100),
                                            address TEXT,
                                            time VARCHAR(256),
                                            link_description TEXT NOT NULL UNIQUE,
                                            min_salary NUMERIC(12, 2),
                                            max_salary NUMERIC(12, 2),
                                            unit VARCHAR(25),
                                            city VARCHAR(100),
                                            district VARCHAR(100),
                                            job_group VARCHAR(100);'''))

            df.to_sql(tmp_table, con=connection, if_exists='append', index=False)

            connection.execute(text(f'''INSERT INTO {tgt_table} (id, created_date, job_title, company, salary, address, time, link_description,
                                                                    min_salary, max_salary, unit, city, district, job_group)
                                        SELECT id, created_date, job_title, company, salary, address, time, link_description,
                                                min_salary, max_salary, unit, city, district, job_group
                                        FROM {tmp_table}
                                        ON CONFLICT (id) DO UPDATE
                                        SET created_date = EXCLUDED.created_date,
                                            job_title = EXCLUDED.job_title,
                                            company = EXCLUDED.company,
                                            salary = EXCLUDED.salary,
                                            address = EXCLUDED.address
                                            time = EXCLUDED.time
                                            link_description = EXCLUDED.link_description
                                            min_salary = COALESCE(EXCLUDED.min_salary, 0)
                                            max_salary = COALESCE(EXCLUDED.max_salary, 0)
                                            unit = EXCLUDED.unit
                                            city = EXCLUDED.city
                                            district = EXCLUDED.district
                                            job_group = EXCLUDED.job_group;'''))

        except Exception as e:
            connection.rollback()
            print(f"An error occurred while loading data into the database.")

