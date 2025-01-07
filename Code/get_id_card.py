import ipaddress
import logging
import queue
import socket
from uhppoted import uhppote
import threading
from pprint import pprint
import time
# from gui.semaphore_module import semaphore
import json

# Cắm 2 dây ethernet vào cùng 1 máy tính sẽ gây ra hiện tượng timeout khi cố gắng kết nối đến controller
# Vì vậy hãy cắm tất cả vào 1 switch và lấy duy nhất 1 dây ethernet cắm vào máy tính
logger = logging.getLogger(__name__)
MY_HOSTNAME = socket.gethostname() # Tên laptop
MY_IP_ADDR = socket.gethostbyname(MY_HOSTNAME) # Địa chỉ IPV4
json_filename = "src/controller/controller.json"

class Person():
    
    """
    Class này là điều khiển controller ACB-004, đầu đọc thẻ từ sẽ kết nối tới bộ điều khiển và bộ điều khiển sẽ kết nối với máy tính bằng ethernet
    Các tham số để kết nối với bộ điều khiển:
    S/N: là dãy số được ghi phía trên bộ điều khiển
    host_addr: là địa chỉ ip của máy tính
    Và các tham số mặc định khác
    
    Các hàm:
    set_listener: Thực hiện chức năng kết nối tới bộ điều khiển
    
    listen: Được chạy trong một luồng riêng biệt, luôn lắng nghe sự kiện quẹt thẻ, nếu có người quẹt thẻ thì nó sẽ nhận giá trị
    
    onEvent: Sẽ nhận các giá trị về thẻ từ mà người quẹt thẻ: id card, ... và đưa giá trị đó vào hàng đợi để xử lý, để biết thêm thông tin thì chạy lệnh này: pprint(event.__dict__, indent=2, width=1)
    
    process_events: Hàm này cũng được chạy trong một luồng riêng biệt, sẽ lấy các giá trị trong hàng đợi và xử lý nó lần lượt.
    
    get_id_card: Lấy ra giá trị thẻ của người vừa quẹt để có thể phân tích, lưu trữ, hiển thị, ...
    """
    
    def __init__(self, controller= None, host_addr = None, function=None):
        
        # Lấy các thông số về bộ điều khiển acb-004, default là giá trị mặc định, không thay đổi
        with open(json_filename, 'r') as inside:
            data = json.load(inside)
            controller = data['Controller_1']['S/N']
            # host_addr = data['IP_Computer']['IP_computer']
            host_port = data['Default']['host_port'] 
            bind_addr = data['Default']['bind_addr']
            broadcast_addr = data['Default']['broadcast_addr']
            listen_addr = data['Default']['listen_addr']
            
        host_addr = ipaddress.IPv4Address(MY_IP_ADDR) # Định dạng ip máy tính
        debug = False
        
        # Tạo hàng đợi để lưu giá trị của thẻ từ 
        self.event_queue = queue.Queue()
        self.max_queue_size = 4  # Giới hạn số lượng trong hàng đợi
        self.lock = threading.Lock()
        self.id_card = None
        
        # Thực hiện hàm này mỗi khi nhận được sự kiện quẹt thẻ
        self.function = function 
        
        # Kết nối với Controller
        u = uhppote.Uhppote(bind_addr, broadcast_addr, listen_addr, debug)
        self.set_listener(u, controller, host_addr, host_port)
        
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
            logger.info(response)
            self.controller_connected = True
        except Exception as e:
            # Khi có tham số exc_info thì nó sẽ hiển thị chi tiết lỗi xảy ra
            logger.error(f"Lỗi khi kết nối tới controller: {e}", exc_info=True)
             
    # Lắng nghe sự kiện quẹt thẻ
    def listen(self, u):
        u.listen(self.onEvent)

    # Xử lý sự kiện với hàng đợi
    def onEvent(self, event):
        # Thêm sự kiện quẹt thẻ vào hàng đợi
        # Mỗi khi quẹt thẻ sẽ mở CSDL và thực hiện thao tác ghi vào CSDL, nếu quẹt thẻ quá nhanh thì nó sẽ gây ra xung đột giữa các cursor cảu SQL Server
        # Vì vậy cần cho vào hàng đợi để có thể xử lý lần lượt, ko gây ra xung đột
        if event:
            if self.event_queue.qsize() >= self.max_queue_size:
                logger.warning('Phát hiện cố tình quẹt thẻ nhanh: id quẹt thẻ %s', event.event_card)
            else:
                logger.info('Quẹt thẻ hợp lệ: id quẹt thẻ %s', event.event_card)
                self.event_queue.put(event)
                
    # Hàm này xử lý sự kiện sau khi quẹt thẻ
    def process_events(self):
        while self.controller_connected:
            if not self.event_queue.empty():
                event = self.event_queue.get()
                try:
                    self.function(event.event_card)
                    with self.lock:
                        self.id_card = event.event_card
                    # print("Số luồng sau khi quẹt thẻ:", threading.active_count())
                    # print(threading.enumerate())
                except Exception as e:
                    # Khi có tham số exc_info thì nó sẽ hiển thị chi tiết lỗi xảy ra
                    logger.warning(f"Lỗi khi xử lý sự kiện quẹt thẻ: {e}", exc_info=True)
                finally:
                    self.event_queue.task_done()
            else:
                time.sleep(0.1)  # Chờ một chút trước khi kiểm tra lại
    
    # # Hàm này xử lý sự kiện quẹt thẻ bằng cách mở thêm luồng mới mỗi khi có người qruetj thẻ, tuy nhiên nếu cố tình quẹt quá nhanh, mở nhiều luồng sẽ gây ra hiện tượng lỗi ghi dữ liệu vào db
    # def onEvent(self,event):
    #     # Nếu có sự kiện quẹt thẻ thì event nhận giá trị
    #     if event:
    #         # 2 lệnh dưới sẽ in ra toàn bộ thông tin có trong thẻ
    #         # pprint(event.__dict__, indent=2, width=1)
    #         # print(event.event_card)
            
    #         # Đây là sử dụng luồng, nếu số lượng luồng mở quá nhiều thì chương trình tự đóng, vì vậy dùng semaphore để giới hạn luồng được mở
    #         # Không dùng join để đợi luồng này, bởi như vậy sẽ làm delay các quá trình còn lại, không giải quyết được vấn đề vượt CPU
    #         if semaphore.acquire(blocking=False):
    #             get_license_in_thread = threading.Thread(target=self.function, args=(event.event_card,))
    #             get_license_in_thread.start()
    #             # Chờ luồng kết thúc, sử dụng join()
    #             # get_license_in_thread.join()
    #             print("số luồng sau khi quẹt thẻ:", threading.active_count())
    #             print(threading.enumerate())
    #             self.id_card = event.event_card
    #         else:
    #             print("đã mở tối đa luồng cho phép")
                
    #         # Đây là không sử dụng luồng, nếu CPU>20% gây ra hiện tượng lag ( quẹt thẻ với tần suất 2s cho 1 lần quẹt)
    #         # self.function(event.event_card)
    #         # self.id_card = event.event_card
    
    # Lấy giá trị id thẻ (dãy số nằm phía sau thẻ nhân viên)
    def get_id_card(self):
        return self.id_card

if __name__ == '__main__':
    person = Person()
    for i in range(20):
        time.sleep(1)