Cấu trúc của mini project

```
Mini Project/
├── data/
│   └── data.csv              # File dữ liệu CSV 
├── source/
│   ├── __init__.py
│   ├── transform.py          # Yêu cầu 1
│   ├── load.py               # Yêu cầu 2
│   ├── ETL.py                # Yêu cầu 2
│   ├── report.py             # Yêu cầu 3
│   └── main.py               # File main
├── test/
│   ├── __init__.py
│   ├── test_transform.py     # Unit test hàm trong transform.py
│   └── test_load.py          # Unit test hàm trong load.py
├── .env                      # Các biến môi trường (không đẩy lên git)
│                               Bao gồm các biến để kết nối PostgreSQL(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS),
│                                       DATA_PATH(đường dẫn lưu file csv),
│                                       REPORT_PATH(đường dẫn kết xuất các report)
├── .gitignore                # File loại trừ khi đẩy lên git
├── requirements.txt          # Các thư viện cần cài
└── runETL.sh                 # File bash để sử dụng cron tạo lịch tự động chạy pipeline
```
