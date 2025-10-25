import re

def add_salary(salary_str):
    # Check salary_str passed in as str
    if not isinstance(salary_str, str):
        return None, None, None

    salary_str = salary_str.lower().strip()

    # Standardize and process "Thoả thuận"
    pattern = 'thoả thuận|thoáº£ thuáº­n'

    if re.search(pattern, salary_str):
        return None, None, None

    if 'usd' in salary_str:
        unit = 'USD'
    else:
        unit = 'VND'

    currency_multiply = {
        'tỷ': 1000000000,
        'triệu': 1000000,
        'nghìn': 1000,
        'ngàn': 1000
    }

    multiplier = 1

    for key, value in currency_multiply.items():
        if key in salary_str:
            multiplier = value

    cleaned_salary_str = re.sub(r'[^\d\-.,]', '', salary_str).strip()

    # Standardize and process "X - Y"
    if re.search(r'\d+([.,]\d+)?\s*\-\s*\d+([.,]\d+)?', cleaned_salary_str):
        salary = cleaned_salary_str.split("-")
        min_salary = float(salary[0].replace(',', '')) * multiplier
        max_salary = float(salary[1].replace(',', '')) * multiplier
        return min_salary, max_salary, unit

    # Standardize and process "Tới X" or "Trên X"
    min_salary, max_salary = None, None

    if re.search(r'\d+([.,]\d+)?', cleaned_salary_str):
        cleaned_salary_str = cleaned_salary_str.replace(',', '')

        salary = float(cleaned_salary_str) * multiplier

        if 'Tới' in salary_str or 'Tá»›i' in salary_str:
            max_salary = salary
        elif 'Trên' in salary_str or 'TrÃªn' in salary_str:
            min_salary = salary
        else:
            max_salary = salary
            min_salary = salary
    return min_salary, max_salary, unit

def split_address(address_str):
    # Check address_str passed in as str
    if not isinstance(address_str, str):
        return None, None

    # Separation rules Addres = City:District
    address = [x.strip() for x in address_str.split(":")]

    if len(address) > 1:
        city = address[0]
        district = address[1]
    else:
        city = address[0]
        district = None
    return city, district

def group_job_tile(job_title_str):
    # Define job groups
    job_group = {
        'Intern': ['thực tập sinh', 'intern'],
        'Project Management': ['project manager', 'quản lý dự án', 'scrum master'],
        'Product Management': ['product owner'],
        'Tech Lead': ['tech lead', 'trưởng nhóm', 'trưởng bộ phận'],
        'Business Analyst': ['business analyst', 'ba'],
        'Tester': ['qa', 'tester'],
        'IT Support': ['it support', 'helpdesk', 'triển khai phần mềm', 'cộng tác viên it'],
        'System': ['system admin', 'infra'],
        'DevOps': ['devops', 'sre'],
        'Data': ['ai engineer', 'business intelligence', 'bi', 'big data'],
        'Fullstack Developer': ['full-stack'],
        'Frontend Developer': ['front end', 'angularjs', 'vuejs', 'web designer', 'html/css'],
        'Backend Developer': ['backend'],
        'Mobile Developer': ['mobile'],
        '.NET Developer': ['.net'],
        'Java Developer': ['java'],
        'Embedded Developer': ['embedded'],
        'Software Engineer': ['developer', 'lập trình', 'engineer', 'phần mềm', 'web'],
        'Business Development': ['business development'],
        'Marketing': ['marketing'],
        'Admin': ['secretary', 'thư ký'],
    }
    job_title_str = job_title_str.lower().strip()
    # print(job_title_str)
    for key in job_group.keys():
        for value in job_group[key]:
            if value in job_title_str:
                return key

    return 'Other'

def cleaning_data(df):
    # 1. Chuẩn hóa cột salary về dạng số, xử lý các giá trị như "Thoả thuận", "Trên X triệu", "X - Y triệu", "Tới X triệu"
    # 2. Tạo thêm các cột phụ: min_salary, max_salary, salary_unit (VND/USD)
    salary_list = []

    for salary_str in df['salary']:
        result = add_salary(salary_str)
        salary_list.append(result)

    df[['min_salary', 'max_salary', 'unit']] = salary_list

    # 3. Xử lý cột address để tách thành city và district
    address_list = []
    for address_str in df['address']:
        result = split_address(address_str)
        address_list.append(result)

    df[['city', 'district']] = address_list

    # 4. Chuẩn hóa job_title để gom nhóm các vị trí tương tự (ví dụ: "Software Engineer", "Developer", "Programmer" có thể gom vào một nhóm)
    job_group_list = []
    for job_group_str in df['job_title']:
        result = group_job_tile(job_group_str)
        job_group_list.append(result)

    df['job_group'] = job_group_list
