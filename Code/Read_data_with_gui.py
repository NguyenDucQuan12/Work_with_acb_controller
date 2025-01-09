import ipaddress
import datetime
import queue
import socket
import threading
from uhppoted import uhppote
import time
import tkinter as tk
from tkinter import Tk, Label, Button, StringVar, Entry, Frame, messagebox

# Cắm 2 dây ethernet vào cùng 1 máy tính sẽ gây ra hiện tượng timeout khi cố gắng kết nối đến controller
# Vì vậy hãy cắm tất cả vào 1 switch và lấy duy nhất 1 dây ethernet cắm vào máy tính

MY_HOSTNAME = socket.gethostname()  # Tên laptop
MY_IP_ADDR = socket.gethostbyname(MY_HOSTNAME)  # Địa chỉ IPV4
json_filename = "Config/controller.json"

class Controller:
    """
    Class này kết nối tới `controller ACB-004` thông qua ethernet  

    Các hàm chính:
    - `set_listener`: Kết nối tới bộ điều khiển
    - `listen`: Lắng nghe sự kiện quẹt thẻ
    - `onEvent`: Nhận và xử lý sự kiện quẹt thẻ
    - `process_events`: Lấy và xử lý các sự kiện trong hàng đợi
    - `get_id_card`: Lấy giá trị thẻ từ của người vừa quẹt
    """
    
    def __init__(self, function=None):
        self.load_config()
        self.initialize_controller(function)

    def load_config(self):
        """
        Lấy các giá trị mặc định để kết nối tới bộ điều khiển
        """
        self.controller_connected = False
        self.host_port = 60001  # port on which to listen for events

        self.bind_addr = '0.0.0.0'  # either INADDR_ANY (0.0.0.0) or the host IPv4 address
        self.broadcast_addr = '255.255.255.255:60000'  # either the broadcast address for INADDR_ANY or the host IP broadcast address
        self.listen_addr = f'0.0.0.0:{self.host_port}'  # either INADDR_ANY (0.0.0.0) or the host IP IPv4 address
        
        self.host_addr = ipaddress.IPv4Address(MY_IP_ADDR)  # Chuyển đổi IP từ string
        self.debug = False

    def initialize_controller(self, function):
        """
        Tạo kết nối tới Controller  
        Tạo một hàng đợi chứa các giá trị id thẻ để xử lý lần lượt  
        
        - `function`: Là hàm sẽ thực thi mỗi khi có dữ liệu đến controller 
        """
        self.uhppote_instance = uhppote.Uhppote(self.bind_addr, self.broadcast_addr, self.listen_addr, self.debug)
        # Tạo hàng đợi để tránh trường hợp quẹt thẻ nhiều lần cùng lúc làm nghẽn
        self.event_queue = queue.Queue()
        self.max_queue_size = 4
        self.lock = threading.Lock()
        self.id_card = None

        self.function = function

    def connect_controller(self, serial_number):
        """
        Kết nối tới Controller và khởi chạy 2 luồng:  
        - `start_listener_thread`
        - `start_processing_thread`
        """
        self.controller_connected, error = self.set_listener(self.uhppote_instance, serial_number, self.host_addr, self.host_port)
        if self.controller_connected:
            self.start_listener_thread()
            self.start_processing_thread()
        
        return self.controller_connected, error

    def disconnect_controller(self):
        """
        Dừng luồng lắng nghe an toàn.
        """
        if self.listener_thread.is_alive():
            self.controller_connected = False  # Dừng vòng lặp trong luồng listen
            self.uhppote_instance._udp.close()  # Đóng socket trong lớp UDP
            self.listener_thread.join()  # Đợi luồng dừng hoàn toàn

    def set_listener(self, u, controller, address, port):
        """
        Kết nối Controller
        """
        try:
            response = u.set_listener(controller, address, port)
            self.controller_connected = True
            error = None
        except Exception as e:
            self.controller_connected = False
            error = e
        finally:
            return self.controller_connected, error

    def start_listener_thread(self):
        """
        Tạo luồng lắng nghe sự kiện quẹt thẻ để tránh gây xung đột với luồng chính
        """
        self.listener_thread = threading.Thread(target=self.listen, args=(self.uhppote_instance,), name="Listen Swipe Card")
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def start_processing_thread(self):
        """
        Tạo luồng thực hiện hàm khi có sự kiện quẹt thẻ
        """
        self.processing_thread = threading.Thread(target=self.process_events, name="Process After Swipe Card")
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def listen(self, u):
        """
        Lắng nghe sự kiện quẹt thẻ
        """
        u.listen(self.onEvent)

    def onEvent(self, event):
        """
        Thêm giá trị `id card` nhận được khi có người quẹt thẻ vào hàng đợi để xử lý lần lượt
        """
        if event:
            if self.event_queue.qsize() >= self.max_queue_size:
                # print('Phát hiện cố tình quẹt thẻ nhiều lần: id quẹt thẻ %s', event.event_card)
                self.event_queue.put(2001)
            else:
                # print('Quẹt thẻ hợp lệ: id quẹt thẻ %s', event.event_card)
                self.event_queue.put(event)

    def process_events(self):
        """
        Khởi chạy `function` mỗi khi có người quẹt thẻ
        """
        while self.controller_connected:
            if not self.event_queue.empty():
                event = self.event_queue.get()
                if event == 2001:
                    id_card = 2001
                else:
                    id_card = event.event_card
                try:
                    self.function(id_card)
                    # Trả về giá trị id card để xử lý tiếp
                    with self.lock:
                        self.id_card = id_card
                except Exception as e:
                    print(f"Lỗi khi xử lý sự kiện quẹt thẻ: {e}", exc_info=True)
                finally:
                    self.event_queue.task_done()
            else:
                time.sleep(0.1)

    def get_id_card(self):
        return self.id_card


class App:
    def __init__(self):

        self.root = Tk()
        self.root.title("Quản lý quẹt thẻ")
        self.root.geometry("500x400")

        self.connected = False

        # Cấu hình cửa sổ phần mềm theo dạng lưới (4x1)
        # Cấu hình các cột có kích thước là như nhau
        self.root.columnconfigure((0),weight=1, uniform="a")
        # Cấu hình các hàng có kích thước phù hợp 
        self.root.rowconfigure((0,1,3),weight=1, uniform="a")
        self.root.rowconfigure(2,weight=3, uniform="a")

        
        self.label = Label(self.root, text="Vui lòng chỉ kết nối 1 cổng ethernet tất cả", font=("Arial", 16))
        self.label.grid(row=0, column=0, sticky= tk.NSEW)

        self.id_card_var = StringVar()
        self.id_card_label = Label(self.root, textvariable=self.id_card_var, font=("Arial", 14), fg="blue")
        self.id_card_label.grid(row=1, column=0, sticky= tk.NSEW)

        self.sn_frame = Frame(self.root)
        self.sn_frame.grid(row=2, column=0, sticky= tk.NSEW)

        # Cấu hình frame nhập serial number theo dạng lưới (4x1)
        self.sn_frame.columnconfigure((0,1,2,3),weight=1, uniform="a")
        self.sn_frame.rowconfigure((0,1),weight=1, uniform="a")

        self.sn_label = Label(self.sn_frame, text="Serial Number Controller: ", font=("Arial", 12))
        self.sn_label.grid(row=0, column=0, columnspan=2, sticky= tk.NSEW)

        self.sn_var = StringVar()
        self.sn_var.set("423138650")

        self.sn_entry = Entry(self.sn_frame, font=("Arial", 12), textvariable=self.sn_var)
        self.sn_entry.grid(row=0, column=2, padx=5)

        self.information_label = Label(self.sn_frame, text="Chức năng ngắt kết nối chưa hoàn thiện, lỗi thì khởi động lại app", font=("Arial", 12), fg="green")
        self.information_label.grid(row=1, column=0, columnspan= 4, sticky= tk.NSEW)

        self.connect_frame = Frame(self.root)
        self.connect_frame.grid(row=3, column=0, sticky= tk.NSEW)

        self.connect_button = Button(self.connect_frame, text="Kết nối", command=self.connect_controller, font=("Arial", 12), activebackground="lightblue")
        self.connect_button.pack(padx=40, side=tk.LEFT)

        self.disconnect_button = Button(self.connect_frame, text="Ngắt kết nối", command=self.disconnect_controller, font=("Arial", 12))
        self.disconnect_button.pack(padx=40, side=tk.RIGHT)
        self.disconnect_button.config(bg="gray", state="disabled")

        self.controller = Controller(function=self.display_id_card)
        self.root.mainloop()

    def display_id_card(self, id_card):
        if id_card == 2001:
            messagebox.showwarning("Cảnh báo", f"Sống chậm lại, quẹt thẻ từ từ thôi")
            return
        today = str(datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y"))
        self.id_card_var.set(f"Thời gian: {today}  ID thẻ: {id_card}")
        self.label.config(text="Thẻ đã được quẹt")
        self.root.update()

    def connect_controller(self):
        # Lấy giá trị serial number của bộ điều khiển
        serial_number_controller = self.sn_entry.get()

        # Kiểm tra nếu serial_number không phải là số
        if not serial_number_controller.isdigit():
            self.information_label.config(text=f"✗ Serial number phải là số", fg="red")
            messagebox.showerror("Lỗi", "Serial number phải là số")
            return

        serial_number_controller = int(serial_number_controller)

        self.connected, error = self.controller.connect_controller(serial_number_controller)

        # Nếu kết nối thành công tới bộ điều khiển thì ẩn nút kết nối và hiện nút ngắt kết nối
        if self.connected:
            self.information_label.config(text=f"✔ Đã Kết nối tới bộ điều khiển: {serial_number_controller}", fg="green")
            self.connect_button.config(bg="gray", state="disable")
            self.disconnect_button.config(bg="white", state="normal")
        else:
            self.information_label.config(text=f"✗ Vui lòng kiểm tra lại serial number và kết nối lại", fg="red")
            if error is not None:
                messagebox.showerror("Lỗi", f"Không thể kết nối tới controller: {error}")

    def disconnect_controller(self):
        self.controller.disconnect_controller()
        self.information_label.config(text=f"✔ Đã ngắt kết nối tới bộ điều khiển", fg="green")
        self.connect_button.config(bg="white", state="normal")
        self.disconnect_button.config(bg="gray", state="disable")

if __name__ == '__main__':
    app = App()
