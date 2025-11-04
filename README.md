Mở file readme để xem cấu trúc của project

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
├── tests/
│   ├── __init__.py
│   ├── test_transform.py     # Unit test hàm trong transform.py
│   └── test_load.py          # Unit test hàm trong load.py
├── .env                      # Các biến môi trường (không đẩy lên git)
├── .gitignore                # File loại trừ khi đẩy lên git
├── requirements.txt          # Các thư viện cần cài
└── runETL.sh                 # File bash để chạy file main
