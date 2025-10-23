import re
import pandas as pd

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

    cleaned_salary_str = re.sub(r'[^\d\-.,]', '', salary_str).strip()

    # Standardize and process "X - Y"
    if re.search(r'\d+\s*\-\s*\d+[.,]\d+', cleaned_salary_str):
        salary = cleaned_salary_str.split("-")
        min_salary = salary[0]
        max_salary = salary[1]
        return min_salary, max_salary, unit

    # Standardize and process "Tới X" or "Trên X"
    min_salary, max_salary = None, None

    if re.search(r'\d+', cleaned_salary_str):
        salary = float(cleaned_salary_str)
        if 'Tới' or 'Tá»›i' in salary_str:
            max_salary = salary
        elif 'Trên' or 'TrÃªn' in salary_str:
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

    df['min_salary','max_salary','unit'] = pd.DataFrame(salary_list)

    # 3. Xử lý cột address để tách thành city và district
    address_list = []
    for address_str in df['address']:
        result = split_address(address_str)
        address_list.append(result)

    df['city', 'address'] = pd.DataFrame(address_list)

    # 4. Chuẩn hóa job_title để gom nhóm các vị trí tương tự (ví dụ: "Software Engineer", "Developer", "Programmer" có thể gom vào một nhóm)
    job_group_list = []
    for job_group_str in df['address']:
        result = split_address(job_group_str)
        job_group_list.append(result)

    df['job_group'] = pd.DataFrame(job_group_list)

# print(add_salary('Trên 10.5  triệu'))
# print(add_salary('Tới 50 triệu'))
# print(add_salary('10 - 30,5 triệu'))
# print(add_salary('10.52 USD'))

# print(split_address('Hà Nội: Cầu Giấy'))
# print(split_address('Hồ Chí Minh'))
# print(split_address('Toàn Quốc'))

# print(group_job_tile('Business Analyst'))
# print(group_job_tile('Nhân Viên Lập Trình Phần Mềm - Thu Nhập Từ 10 - 20 Triệu'))
# print(group_job_tile('Nhello'))