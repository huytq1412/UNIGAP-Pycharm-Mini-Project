import unittest
import pandas as pd
from source.transform import add_salary, split_address, group_job_tile, cleaning_data
from pandas.testing import assert_frame_equal

class Test_CleaningData(unittest.TestCase):
    def setUp(self):
        # Create sample dataframe
        self.sample_data = pd.DataFrame({
            'job_title': [
                'Chuyên Viên Business Analyst',
                'Thực tập sinh .NET',
                'Lập trình viên Java',
                'Kế toán tổng hợp'
            ],
            'salary': [
                '10 - 20 triệu',
                'Thoả thuận',
                'Trên 2000 USD',
                'Tới 15 triệu'
            ],
            'address': [
                'Hà Nội: Cầu Giấy',
                'Hồ Chí Minh',
                'Hà Nội: Thanh Xuân: Hải Dương',
                12345  # Not datatype string
            ]
        })

        # Create expected dataframe
        self.expected_data = pd.DataFrame({
            'job_title': [
                'Chuyên Viên Business Analyst',
                'Thực tập sinh .NET',
                'Lập trình viên Java',
                'Kế toán tổng hợp'
            ],
            'salary': [
                '10 - 20 triệu',
                'Thoả thuận',
                'Trên 2000 USD',
                'Tới 15 triệu'
            ],
            'address': [
                'Hà Nội: Cầu Giấy',
                'Hồ Chí Minh',
                'Hà Nội: Thanh Xuân: Hải Dương',
                12345
            ],
            # Result from add_salary()
            'min_salary': [10000000, None, 2000, None],
            'max_salary': [20000000, None, None, 15000000],
            'unit': ['VND', None, 'USD', 'VND'],  # 'Thoả thuận' return None
            # Result from split_address()
            'city': ['Hà Nội', 'Hồ Chí Minh', 'Hà Nội', None],  # '12345' return None
            'district': ['Cầu Giấy', None, 'Thanh Xuân', None],  # '12345' return None
            # Result from group_job_title()
            'job_group': [
                'Business Analyst',
                'Intern',
                'Java Developer',
                'Other'
            ]
        })

    def tearDown(self):
        del self.sample_data
        del self.expected_data

    # 1. Test function add_salary()
    def test_add_salary_range_vnd(self):
        # Test salary range 'X - Y triệu' (VND)
        result = add_salary('10 - 20 triệu')
        expected = (10000000.0, 20000000.0, 'VND')
        self.assertEqual(result, expected)

    def test_add_salary_range_usd(self):
        # Test salary range 'X - Y USD'
        result = add_salary('500 - 1000 USD')
        expected = (500.0, 1000.0, 'USD')
        self.assertEqual(result, expected)

    def test_add_salary_agreement(self):
        # Test salary 'Thoả thuận'
        result = add_salary('Thoả thuận')
        expected = (None, None, None)
        self.assertEqual(result, expected)

    def test_add_salary_from(self):
        # Test salary from 'Trên X'
        result = add_salary('Trên 500 USD')
        expected = (500.0, None, 'USD')
        self.assertEqual(result, expected)

    def test_add_salary_to(self):
        # Test salary to 'Tới X'
        result = add_salary('Tới 15 triệu')
        expected = (None, 15000000.0, 'VND')
        self.assertEqual(result, expected)

    def test_add_salary_invalid_input(self):
        # Test input 'non-string' datatype
        result = add_salary(123456)
        expected = (None, None, None)
        self.assertEqual(result, expected)

    # 2. Test function split_address()
    # Separation rules Address = City:District
    def test_split_address_full(self):
        # Test full address 'City: District'
        result = split_address('Hà Nội: Cầu Giấy')
        expected = ('Hà Nội', 'Cầu Giấy')
        self.assertEqual(result, expected)

    def test_split_address_city_only(self):
        # Test partial address
        result = split_address('Hồ Chí Minh')
        expected = ('Hồ Chí Minh', None)
        self.assertEqual(result, expected)

    def test_split_address_complex(self):
        # Test complicated address, take only the first two elements
        result = split_address('Hà Nội: Thanh Xuân: Hải Dương')
        expected = ('Hà Nội', 'Thanh Xuân')
        self.assertEqual(result, expected)

    def test_split_address_invalid_input(self):
        # Test input 'non-string' datatype
        result = split_address(12345)
        expected = (None, None)
        self.assertEqual(result, expected)

    # 3. Test function group_job_tile()
    def test_group_job_tile_order_intern(self):
        # Test order: 'Intern' must have priority over '.NET'
        result = group_job_tile('Thực tập sinh .NET')
        self.assertEqual(result, 'Intern')

    def test_group_job_tile_order_java(self):
        # Test order: 'Java Developer' must have priority over 'Software Engineer'
        result = group_job_tile('Senior Java Developer (Lập trình viên)')
        self.assertEqual(result, 'Java Developer')

    def test_group_job_tile_no_match(self):
        # Test 'Other' group
        result = group_job_tile('Kế toán')
        self.assertEqual(result, 'Other')

    # 4. Test function cleaning_data()
    def test_cleaning_data_integration(self):
        cleaning_data(self.sample_data)

        # Sort the dataframes for ease of comparison
        self.sample_data = self.sample_data[sorted(self.sample_data.columns)]
        self.expected_data = self.expected_data[sorted(self.expected_data.columns)]

        assert_frame_equal(self.sample_data, self.expected_data, check_dtype=False)

if __name__ == '__main__':
    unittest.main()