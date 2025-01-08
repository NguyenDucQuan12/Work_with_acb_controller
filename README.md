# Hướng dẫn cách lấy dữ liệu từ đầu đọc thẻ `IDTECK` từ bộ điều khiển `ACB-004 Controller`
# Mục lục

[I. Bối cảnh](#i-bối-cảnh)

[II. Đầu đọc thẻ IDTECK IP10](#ii-đầu-đọc-thẻ-idteck-ip10)
- [1. Sản phẩm](#1-sản-phẩm)
- [2. Sơ đồ kết nối](#2-sơ-đồ-kết-nối)

[III. Bộ điều khiển ACB-004](#iii-bộ-điều-khiển-acb---004)
- [1. Sản phẩm](#1-sản-phẩm-1)
- [2. Sơ đồ kết nối](#2-sơ-đồ-kết-nối-1)
- [3. Phần mềm Access Control](#3-phần-mềm-access-control)
    - [1. Một số mật khẩu cần lưu ý của phần mềm Access Control](#1-một-số-mật-khẩu-cần-lưu-ý-của-phần-mềm-access-control)
    - [2. Kết nối ACB-004 với Access Control](#2-kết-nối-acb-004-với-access-control)
    - [3. Kiểm tra dữ liệu quẹt thẻ](#3-kiểm-tra-dữ-liệu-quẹt-thẻ)
- [4. Một số lỗi khi sử dụng ACB-004](#4-một-số-lỗi-khi-sử-dụng-acb-004)
    - [1. Cách nhận biết lỗi](#1-cách-nhận-biết-lỗi)
    - [2. Thời gian không khớp với hiện tại](#2-thời-gian-không-khớp-với-hiện-tại)
    - [3. Không thể xem được chức năng Monitor](#3-không-thể-xem-được-chức-năng-monitor)

[IV. Đọc dữ liệu từ bộ điều khiển bằng Python](#iv-đọc-dữ-liệu-từ-bộ-điều-khiển-bằng-python)
- [1. Thư viện Uhppoted](#1-thư-viện-uhppoted)


# I. Bối cảnh

Tôi cần biết được một số thông tin mỗi khi có người quẹt thẻ từ vào đầu đọc thẻ từ.  

![alt text](Image/swipe_card_reader.jpg)

# II. Đầu đọc thẻ IDTECK IP10
## 1. Sản phẩm

Đây là đầu đọc thẻ từ mà tôi đang sử dụng `IDTECK IP10`.  

![alt text](Image/IDTECK_IP10.JPG)

## 2. Sơ đồ kết nối
Ta có sơ đồ kết nối của đầu đọc thẻ như sau:  

![alt text](Image/connection_diagram_idteck.png)

Ta chỉ phục vụ mục đích lấy dữ liệu mỗi khi có người quẹt thẻ nên ta chỉ cần quan tâm tới các dây sau:  

> Red: Là nguồn vào 12V (Cực dương)  
> Black: Là nguồn vào 0V (Cực âm)  
> Green: Data 0 out  
> White: Data 1 out  
> Brown: RS232 (Nếu dùng RS232)  

Ta cần có nguồn 12V để cung cấp cho đầu đọc thẻ này, tuy nhiên bộ điều khiển `ACB-004` có sẵn nguồn 12V nên ta không cần kết nối nguồn khác nữa.  

# III. Bộ điều khiển ACB - 004
## 1. Sản phẩm
Để đọc được dữ liệu từ bộ điều khiển thì tôi lựa chọn bộ điều khiển `ACB-004` để lấy dữ liệu.  

![alt text](Image/acb_004_controller.png)

Nó có thể kết nối tới 4 đầu đọc thẻ cùng 1 lúc. Ta kết nối nó như sau.  

## 2. Sơ đồ kết nối
Cấp nguồn 12V cho bộ điều khiển ở vị trí `access power supply` ta tiến hành đấu nối dây như hướng dẫn trên bảng mạch gồm:  

> GND: Là nguồn 0V (Cực âm)  
> +12V: Là nguồn 12V (Cực dương)  

Xem hình ảnh minh họa bên dưới (dây nâu là +12V, dây xanh là 0V)

![alt text](Image/access_power_supply.JPG)

Kết nối với đầu đọc thẻ từ tại 4 vị trí `Access reader` như hướng dẫn trên bảng mạch gồm:  

> 12V: Là nguồn 12V cho đầu đọc thẻ (Tương ứng với dây đỏ của IDTECK)  
> 0V: Là nguồn 0V cho đầu đọc thẻ (Tương ứng với dây đen của IDTECK)  
> D1: Là Data 1 out (Tương ứng với dây trắng của IDTECK)  
> D0: Là Data 0 out (Tương ứng với dây xanh của IDTECK)  
> LED: Hình như là chức năng đổi màu của đầu đọc thẻ từ (Mình không sử dụng nên chưa tìm hiểu nó có chức năng gì)  

Để chi tiết hơn có thể tham khảo cách đấu nối ở hình ảnh bên dưới:  

![alt text](Image/access_reader_connect.JPG)

Theo thứ tự dây `Đỏ`, `Đen`, `Trắng`, `Xanh lá cây` như hình ảnh bên trên  

## 3. Phần mềm Access Control
Bộ điều khiển này có phần mềm riêng để có thể cấu hình bộ điều khiển cũng như kiểm tra các tác vụ liên quan đến bộ điều khiển. Tải phần mềm về [tại đây](Setup/Software-ACB-001-002-004.rar).  
Giải nén nó ra và chạy tệp tin `setup.exe` như hình bên dưới:  

![alt text](Image/install_access_control.png)

Sau khi cài đặt xong sẽ có một phần mềm tên là `Access Control`.  

### 1. Một số mật khẩu cần lưu ý của phần mềm Access Control
Mở phần mềm đó lên và đăng nhập với thông tin như sau:  

![alt text](Image/login_access_control.png)

> User Name: `abc`  
> Password: `123`  

Sau khi đăng nhập sẽ vào giao diện chính như sau:  

![alt text](Image/access_control_home_paper.png)

Để sử dụng chức năng `Tool --> Extended Function` ta cũng cần cung cấp mật khẩu.  

![alt text](Image/tool_access_control.png)

> Password: `5678`  

Sau đó mở ra giao diện tool với một số chức năng ta có thể dùng như bên dưới:  

![alt text](Image/extended_function.png)

Mặc định khi tải về thì phần mềm chỉ được dùng thử. Sau khi hết hạn bạn sẽ không thể truy cập được nữa. Ta sẽ đăng ký bằng cách vào `Help --> About --> Register` dựa trên một số thông tin sau:  

![alt text](Image/register_access_control.png)

> Company Nam: `s4a`  
> Building Company: `s4a`  
> Register Code: `2004`  

Như vậy chỉ cần ấn nút `OK` để khởi động lại chương trình là đã đăng ký thành công.  

![alt text](Image/register_access_control_success.png)

Còn một mật khẩu cuối cùng nữa đấy là tệp tin `ICCard3000: Microsoft Access Database (.mdb)` để xem dữ liệu.  

![alt text](Image/iCCard300_password.png)

> Mật khẩu sẽ là: `168168`  

### 2. Kết nối acb-004 với access control

Ta cắm dây ethernet từ cổng TCP/IP của `ACB-004` vào máy tính.  

![alt text](Image/access_reader_connect.JPG)

Nếu cắm thành công thì ta sẽ thấy đèn màu xanh phía bên phải `cổng TCP/IP` sáng màu. Và khi quẹt thẻ thì đèn màu cam sẽ nhấp nháy báo hiệu đã truyền/nhận tín hiệu.  
Tiếp theo vào phần mềm `Access Control` và tìm kiếm controller bằng cách dùng chức năng `Add Controller By Searching` như hình ảnh bên dưới:  

![alt text](Image/add_contronller_by_search.png)

Sau khi thêm bộ điều khiển xong thì bạn vào `Configuration` và chọn `Controller` để xem danh sách các bộ điều khiển đã thêm vào.  

![alt text](Image/add_contronller_success.png)

Như hình ảnh bên trên tôi đã thêm bộ điều khiển `ACB-004` của mình thành công. Nó sẽ cho chúng ta một số thông tin về bộ điều khiển mà ta cần lưu ý như sau:  

> SN: Serial number  
> IP: Địa chỉ IP của controller  
> Port: Cổng kết nối  

Để chỉnh sửa bộ điều khiển thì ta nhấn đúp vào bộ điều khiển đó.  

![alt text](Image/configuaration_controller.png)

Ta chỉ nên thay đổi địa chỉ IP của bộ điều khiển sao cho cùng dải mạng với máy tính là được, các thông số khác để nguyên.  

### 3. Kiểm tra dữ liệu quẹt thẻ
Để xem thông tin dữ liệu khi quẹt thẻ, ta vào chức năng `Operation` như hình ảnh dưới đây:  

![alt text](Image/monitoring_swipe_record.png)

Ta vào `Operation` sau đó ấn `Select All` để chọn hết các cửa và ấn `Monitor` để quan sát sự kiện quẹt thẻ.  
Khi đó mỗi khi ta đưa thẻ gần đầu đọc thẻ đủ để nhận tín hiệu thì dữ liệu sẽ được hiển thị tại ô bên dưới. Thông tin sẽ được hiển thị tại cột `Infor`.  
Như vậy ta đã có thể xác nhận được rằng hệ thống đã hoạt động ổn định, chuyển sang bước tiếp theo là đọc dữ liệu bằng `python`.  

## 4. Một số lỗi khi sử dụng ACB-004
### 1. Cách nhận biết lỗi
Ta có thể nhận biết có lỗi bằng cách quan sát các đèn `LED trên bảng mạch (LED indicator)` của bộ điều khiển như hình dưới đây:  

![alt text](Image/acb_004_controller.png)

Đèn dưới cùng màu đỏ, có tên `ERR` nó sẽ sáng nhẹ hoặc nhấp nháy thì báo hiệu lỗi. Một số lỗi phổ biến mà mình từng gặp dưới đây.  

### 2. Thời gian không khớp với hiện tại
Đây là lỗi mình thường xuyên gặp nhất (Và nó cũng không ảnh hưởng gì hệ thống cả ngoài thời gian sai), chỉ cần mất điện hoặc nguồn điện không ổn định, khiến cho bộ điều khiển không được cung cấp điện. Sau đó khởi động lại bộ điều khiển thì đèn báo `ERR` sáng lên.  

Cách khắc phục là ta sẽ vào phần mềm `Access Control` để điều chỉnh lại thời gian cho bộ điều khiển.  

![alt text](Image/adjust_time_in_access_control.png)

Ta vào `Operation` sau đó chọn `Select All` để chọn hết cửa và nhấn vào chức năng `Adjust Time` để cập nhật lại thời gian của bộ điều khiển. Nếu thành công nó sẽ báo xanh như vị trí số 3 ở trên.  

### 3. Không thể xem được chức năng Monitor
Lỗi này khiến khi mình sử dụng chức năng `monitor` sẽ không xem được sự kiện quẹt thẻ. Dấu hiện nhận biết là hình cánh cửa không mở ra và có màu xanh như bình thường. Thay vào đó là nó có hình như dưới đây.  

![alt text](Image/No_information.png)

Để sửa lỗi này thì các bạn cũng tương tự như thời gian. Tuy nhiên các bạn không dùng chức năng `Adjust Time` mà sử dụng chức năng `Check`.  

![alt text](Image/No_information.png)

Nó sẽ mở ra cửa sổ mới và bạn nhấn vào chức năng `Auto configuration ...`. Sau đó nó sẽ tự động sửa lỗi.  

![alt text](Image/No_information.png)

# IV. Đọc dữ liệu từ bộ điều khiển bằng Python

## 1. Thư viện uhppoted

![alt text](Image/uhppoted_github.png)

Để kết nối được với bộ điều khiển `ACB-004` ta sử dụng thư viện `Uhppoted`. Có thể tham khảo chi tiết [tại đây](https://github.com/uhppoted/uhppoted-python).  
Ta cài đặt thư viện này bằng câu lệnh sau:  

```python 
pip install uhppoted
```

![alt text](Image/install_uhppoted_using_pip.png)

Ta đã cài đặt thành công thư viện `uhppoted` trong môi trường ảo. Để tham khảo về cách làm việc với môi trường ảo thì tìm hiểu tại repository [Virtual_enviroment_python](https://github.com/NguyenDucQuan12/virtual_environment_python).  

## 2. Kết nối với bộ điều khiển ACB-004 bằng python

