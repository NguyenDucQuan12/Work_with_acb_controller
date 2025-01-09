from setuptools import setup

setup(
    name='acbcontroller', # Tên thư viện mà ta muốn lưu lại với tên mới hoặc viết lại tên cũ
    version='0.0.1',  # Phiên bản
    description='Thu vien dung de ket noi toi bo dieu khien ACB 004', # Mô tả thư viện này làm gì
    author='Nguyen Duc Quan',  # Tên người viết ra thư viện này
    packages=['uhppoted'],  # Chỉ rõ tên thư mục chứa mã nguồn
    package_dir={'uhppoted': 'Code/uhppoted'},  # Đường dẫn tới thư mục chứa mã nguồn
    include_package_data=True,
    install_requires=[], # Các thư viện khác mà thư viện này cần thêm
)
"""
Nếu thư viện cần phụ thuộc bên ngoài, thêm chúng vào mục install_requires trong tệp setup.py

install_requires=[
    'requests>=2.25.1',
    'numpy>=1.21.0'
]

"""