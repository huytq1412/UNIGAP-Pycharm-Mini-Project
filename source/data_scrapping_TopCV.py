from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import concurrent.futures

def convert_created_date(created_date_str):
    # Function to generate 'created_date'
    today = date.today()
    created_date = None

    if not isinstance(created_date_str, str):
        return None

    # If the input string includes "hôm nay", "phút", "giờ" -> get today date
    if "hôm nay" in created_date_str or "phút" in created_date_str or "giờ" in created_date_str:
        return today.strftime('%Y-%m-%d')

    created_date_cleaned = re.search(r'(\d+)\s+(ngày|tuần|tháng|năm)\s+trước', created_date_str)

    diff = int(created_date_cleaned[1])
    unit = created_date_cleaned[2]

    # If the input string includes "ngày", "tuần", "tháng", "năm" -> recalculate the date
    if unit == "ngày":
        created_date = today - timedelta(days=diff)
    elif unit == "tuần":
        created_date = today - timedelta(weeks=diff)
    elif unit == "tháng":
        created_date = today - relativedelta(months=diff)
    elif unit == "năm":
        created_date = today - relativedelta(years=diff)
    else:
        created_date = today

    return created_date.strftime('%Y-%m-%d')

def detail_scrapping(detail_url):
    # Function to generate 'time_remain' and 'job_description'

    # Default 2 times, if information is still not obtained then wait and try again
    # To handle the case of crawling too fast, the server does not return data
    for attempt in range(2):
        time_remain = None
        job_description = None

        try:
            response = requests.get(detail_url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # get 'time_remain'
                time_tag = soup.select_one('span.deadline')

                if time_tag:
                    time_remain = " ".join(time_tag.stripped_strings)

                # get 'job_description'
                desc_tag = soup.select_one('div.job-description__item--content')
                if desc_tag:
                    job_description = " ".join(desc_tag.stripped_strings)

                # Found data -> success
                if time_tag or desc_tag:
                    return time_remain, job_description

            # If the code runs to here (status != 200 or tag data not found)
            print(f"Warning: Attempt {attempt + 1} for {detail_url} failed (code: {response.status_code}). Please wait...")
            time.sleep(10)  # Default wait 10 seconds and try again

        except Exception as e:
            print(f"Error while scraping the page {detail_url}: {e}")

    return time_remain, job_description

def data_scrapping():
    # data scrapping url
    base_url = "https://www.topcv.vn/tim-viec-lam-moi-nhat?type_keyword=1&page={}&sba=1"
    all_jobs_list = []
    page_number = 1

    existed_links = set()

    # Use the command below to loop through each page of data until it is finished then break
    # while True:
    # Use the command below to select the data range you want to get
    for page_number in range(1, 5):
        url = base_url.format(page_number)
        print(f"\n--- Crawling page {page_number} ---")

        try:
            res = requests.get(url, timeout=10)

            if res.status_code != 200:
                print("Error retrieving data from server")
                break

            soup = BeautifulSoup(res.text, "html5lib")

            # Get the parent tag containing all jobs
            all_jobs = soup.select('div.job-item-search-result')

            if not all_jobs:
                print("No jobs found. No more page.")
                break

            tmp_jobs_list = []
            link_description_list = []

            # Process the loop to end the While loop
            # If the link of the first job on the page already exists -> stop. No more page
            first_job_tag = all_jobs[0].select_one('h3.title a')
            is_duplicate_page = False
            if first_job_tag and first_job_tag.has_attr('href'):
                first_link = first_job_tag['href'].split('&u_sr_id=')[0]
                if first_link in existed_links:
                    print(f"Duplicate page detected (link {first_link} found). Stop.")
                    is_duplicate_page = True

            if is_duplicate_page:
                break

            # Loop processing of each job
            for job in all_jobs:
                # get 'link_description'
                link_tag = job.select_one('h3.title a')
                if link_tag and link_tag.has_attr('href'):
                    link_description = link_tag['href'].split('&u_sr_id=')[0]
                else:
                    link_description = None

                # If the link already exists in the existed_links -> Move to next job
                if link_description in existed_links:
                    print(f"Job already exists. Skip job")
                    continue

                # Add a existed_links set containing existing links to check with first_link
                existed_links.add(link_description)

                # get 'job title'
                job_tag = job.select_one('h3.title a span')
                if job_tag:
                    job_title = job_tag.text.strip()
                else:
                    job_title = None

                # get 'company'
                company_tag = job.select_one('span.company-name')
                if company_tag:
                    company = company_tag.text.strip()
                else:
                    company = None

                # get 'salary'
                salary_tag = job.select_one('div.info label.salary span')
                if salary_tag:
                    salary = salary_tag.text.strip()
                else:
                    salary = None

                # get 'address'
                address_tag = job.select_one('div.info label.address')
                if address_tag and address_tag.has_attr('title'):
                    html_string = address_tag['title']
                    # There are 2 cases of address. With and without <li> tag
                    # Find address with the pattern <li> first
                    address_pattern_li = re.findall(r'<li>(.*?)</li>', html_string)

                    if address_pattern_li:
                        # If pattern <li> is found -> Join all address with ":"
                        cleaned_list = [addr.strip() for addr in address_pattern_li]
                        address = ":".join(cleaned_list)
                    else:
                        # If pattern <li> is found -> Remove unnecessary tags
                        address_cleaned = re.sub(r'<br\s*/?>', ': ', html_string)
                        address = re.sub(r'<[^>]+>', '', address_cleaned).strip()
                else:
                    address = None

                # get 'created_date'
                created_date_tag = job.select_one('label.label-update')

                if created_date_tag:
                    created_date_str = created_date_tag.text.strip()

                    created_date = convert_created_date(created_date_str)
                else:
                    created_date = None

                tmp_jobs_list.append({
                    'created_date': created_date,
                    'job_title': job_title,
                    'company': company,
                    'salary': salary,
                    'address': address,
                    'link_description': link_description})

                # Create a list containing job links on the current page
                link_description_list.append(link_description)

            # get 'time_remain' and 'job_description'
            # Use concurrent.futures to have more threads crawling link data
            # Default 5 threads to crawl data
            workers = 5
            detail_data_list = []
            time.sleep(2)
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                # Run the `detail_scrapping` function in parallel on multiple threads
                results = executor.map(detail_scrapping, link_description_list)
                # and returns the list of job_description and time_remain
                detail_data_list = list(results)

            # Merge result
            for i in range(len(tmp_jobs_list)):
                tmp_jobs = tmp_jobs_list[i]

                detail_data = detail_data_list[i]

                time_remain = detail_data[0]
                job_description = detail_data[1]

                tmp_jobs['time'] = time_remain
                tmp_jobs['job_description'] = job_description

                all_jobs_list.append(tmp_jobs)

            page_number += 1
            time.sleep(10)  # Wait 10 seconds before scrapping the next page

        except Exception as e:
            print(f"Error while scrapping data: {e}")
            break
    print("\n--- DATA SCRAPPING COMPLETE ---")

    if all_jobs_list:
        df = pd.DataFrame(all_jobs_list)
        print(f"Total {len(df)} jobs were scrapped from {page_number - 1} pages.")
        return df
    else:
        print("No data can be scrapped.")
        return None

# Get current file directory
current_dir = os.path.dirname(__file__)

# Get project root directory
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Get file .env directory
env_path = os.path.join(project_dir, '.env')

if __name__ == "__main__":
    df = data_scrapping()

    load_dotenv(dotenv_path=env_path)
    data_path = os.environ.get('DATA_PATH')

    try:
        df.to_csv(f'{data_path}/dataTopCV.csv', index=False, encoding='utf-8-sig')

        print(f"\n--- DATA SAVED SUCCESSFULLY ---")

    except Exception as e:
        print(f"\n--- ERROR WHEN SAVING CSV FILE: {e} ---")
