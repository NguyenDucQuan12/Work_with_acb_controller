import ipaddress
import queue
import socket
import pprint
from uhppoted import uhppote
import threading
import time

MY_HOSTNAME = socket.gethostname()  # Lấy tên laptop

# Lấy địa chỉ IPv4 là chuỗi ký tự "169.254.254.254"
MY_IP_ADDR = socket.gethostbyname_ex(MY_HOSTNAME)[2]  # Tất cả danh sách địa chỉ ipv4
# MY_IP_ADDR = socket.gethostbyname(MY_HOSTNAME)  # Địa chỉ ipv4 thấp nhất, ví dụ 10.239.xx.xx với 169.254.xx.xx thì sẽ lấy 10.239.xx.xx
print(MY_IP_ADDR)

class Person():
    """
    Class này là điều khiển controller ACB-004, đầu đọc thẻ từ sẽ kết nối tới bộ điều khiển và bộ điều khiển sẽ kết nối với máy tính bằng ethernet.
    Các tham số để kết nối với bộ điều khiển:
    S/N: là dãy số được ghi phía trên bộ điều khiển
    host_addr: là địa chỉ ip của máy tính.
    Và các tham số mặc định khác.
    """

    def __init__(self, function=None):
        controller = 423138650  # controller serial number
        host_port = 60001  # port on which to listen for events
        self.host_addrs = [ipaddress.IPv4Address(ip) for ip in MY_IP_ADDR]  # Danh sách địa chỉ IP

        bind_addr = '0.0.0.0'  # either INADDR_ANY (0.0.0.0) or the host IPv4 address
        #  bind_addr thay thế cho str(ip) nếu muốn lắng nghe tất cả địa chỉ trên 1 dải mạng, nếu có 2 mạng ethernet cùng cắm vào máy tính trở lên thì ko nên dùng
        # u = uhppote.Uhppote(str(ip), broadcast_addr, listen_addr, debug)
        broadcast_addr = '255.255.255.255:60000'  # broadcast address
        listen_addr = f'0.0.0.0:{host_port}'  # listen on all interfaces
        debug = False
        
        # Tạo hàng đợi để lưu giá trị của thẻ từ
        self.event_queue = queue.Queue()
        self.max_queue_size = 10  # Giới hạn số lượng trong hàng đợi
        self.lock = threading.Lock()
        self.id_card = None

        # Thực hiện hàm này mỗi khi nhận được sự kiện quẹt thẻ
        self.function = function 

        # Lặp qua tất cả các địa chỉ IP và thử kết nối
        self.controller_connected = False
        for ip in self.host_addrs:
            try:
                u = uhppote.Uhppote(str(ip), broadcast_addr, listen_addr, debug)
                self.set_listener(u, controller, ip, host_port)
                if self.controller_connected:
                    print(f"Đã kết nối tới controller qua IP {ip}")
                    break  # Nếu kết nối thành công, thoát khỏi vòng lặp
            except Exception as e:
                print(f"Lỗi khi kết nối tới controller qua IP {ip}: {e}")
                continue  # Nếu kết nối lỗi, thử với IP tiếp theo
        
        if not self.controller_connected:
            print("Không thể kết nối tới controller với bất kỳ địa chỉ IP nào!")

        # Khởi tạo thread lắng nghe sự kiện quẹt thẻ
        self.thread = threading.Thread(target=self.listen, args=(u,), name="Listen Swipe Card")
        self.thread.daemon = True
        self.thread.start()

        # Khởi tạo luồng xử lý sự kiện sau khi quẹt thẻ
        self.processing_thread = threading.Thread(target=self.process_events, name="Process After Swipe Card")
        self.processing_thread.daemon = True  # Đảm bảo luồng sẽ tự động kết thúc khi chương trình chính kết thúc
        self.processing_thread.start()

    def set_listener(self, u, controller, address, port):
        try:
            response = u.set_listener(controller, address, port)
            self.controller_connected = True
        except Exception as e:
            self.controller_connected = False
            print(f"Lỗi khi kết nối tới controller: {e}")
             
    # Lắng nghe sự kiện quẹt thẻ
    def listen(self, u):
        u.listen(self.onEvent)

    # Xử lý sự kiện với hàng đợi
    def onEvent(self, event):
        if event:
            if self.event_queue.qsize() >= self.max_queue_size:
                print('Phát hiện cố tình quẹt thẻ nhanh: id quẹt thẻ %s', event.event_card)
            else:
                self.event_queue.put(event)

    # Hàm này xử lý sự kiện sau khi quẹt thẻ
    def process_events(self):
        while self.controller_connected:
            if not self.event_queue.empty():
                event = self.event_queue.get()
                try:
                    self.function(event)
                    with self.lock:
                        self.id_card = event.event_card
                except Exception as e:
                    print(f"Lỗi khi xử lý sự kiện quẹt thẻ: {e}", exc_info=True)
                finally:
                    self.event_queue.task_done()
            else:
                time.sleep(0.1)  # Chờ một chút trước khi kiểm tra lại

    # Lấy giá trị id thẻ (dãy số nằm phía sau thẻ nhân viên)
    def get_id_card(self):
        return self.id_card

def display(event):
    print(f"{event.event_card} đã quẹt thẻ với thông tin: ")
    pprint.pprint(event.__dict__, indent=2, width=1)

if __name__ == '__main__':
    person = Person(function=display)
    while True:
        pass
