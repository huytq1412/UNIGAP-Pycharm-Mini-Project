import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sqlalchemy import create_engine
import re

def getdata_fromdb(db_conn_uri,tgt_table):
    try:
        engine = create_engine(db_conn_uri)
        df = pd.read_sql(f"SELECT * FROM {tgt_table}", engine)
        return df
    except Exception as e:
        print(f"Could not run analysis: {e}")

def convert_salary(df, convert_rate):
    # Create new salary column converted to (million) VND
    def apply_salary(row):
        min_salary = row['min_salary']
        max_salary = row['max_salary']
        unit = row['unit']

        if unit == 'usd' or unit == 'USD':
            min_salary = min_salary * convert_rate
            max_salary = max_salary * convert_rate

        if pd.notna(min_salary) and pd.notna(max_salary):
            return ((min_salary + max_salary) / 2) / 1000000
        elif pd.notna(min_salary):
            return min_salary / 1000000
        elif pd.notna(max_salary):
            return max_salary / 1000000
        else:
            return None

    df['converted_salary(mil VND)'] = df.apply(apply_salary, axis=1)
    # Shink to lower than 1000 mil VND because some data are too large (might cause report imbalance)
    df = df[df['converted_salary(mil VND)'] < 1000]
    return df

def plot_salary_distribution(df, convert_rate, report_path):
    try:
        report_path = f'{report_path}/salary_distribution.png'

        df_salary = convert_salary(df, convert_rate)

        sns.set_theme()
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=df_salary, x='job_group', y='converted_salary(mil VND)' , palette='viridis');
        plt.xticks(rotation=45, ha='right')
        plt.title('Salary distribution (million VND) by job group', fontsize=20)
        plt.ylabel('Average salary (million VND)')
        plt.xlabel('Job group')
        plt.tight_layout()
        plt.savefig(report_path)
    except Exception as e:
        print(f"Could not plot salary distribution: {e}")

def plot_job_heatmap(df, report_path):
    try:
        report_path = f'{report_path}/job_heatmap.png'

        df_job = df[df['city'] != 'Toàn Quốc']
        df_job_pivot = pd.pivot_table(df_job, index='city', columns='job_group', aggfunc='size', fill_value=0)

        plt.figure(figsize=(12, 8))
        sns.heatmap(df_job_pivot, annot=True, fmt='d', cmap='viridis', linecolor='white', linewidths=0.5)
        plt.title('Job distribution heat map', fontsize=20)
        plt.xlabel('Job group', fontsize=12)
        plt.ylabel('City', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(report_path)
    except Exception as e:
        print(f"Could not plot job heatmap: {e}")


def plot_techtrend(df, report_path):
    try:
        report_path = f'{report_path}/techtrend.png'

        # Declare current technology trends keyword
        tech_keyword = ['BA', 'devops', 'data', '.net', 'python','java','react','aws','docker','node']
        tech_keyword = [tech.lower() for tech in tech_keyword]

        series_job = df['job_group']

        tech_counts = {}

        for tech in tech_keyword:
            pattern = re.escape(tech)

            mask = series_job.str.contains(pattern, case=False, regex=True, na=False)

            count = (mask[mask == True].count())

            tech_counts[tech] = count

        # Create a tech trend dataframe based on technology keywords
        df_techtrend = pd.DataFrame(tech_counts.items(), columns=['tech', 'count'])

        plt.figure(figsize=(12, 8))
        sns.barplot(data=df_techtrend, x='tech', y='count', palette='viridis')
        plt.title('Technology trends', fontsize=20)
        plt.xlabel('Technology', fontsize=12)
        plt.ylabel('Number of job recruitments', fontsize=12)
        plt.tight_layout()
        plt.savefig(report_path)
    except Exception as e:
        print(f"Could not plot tech trends: {e}")