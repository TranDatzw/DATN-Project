import sys
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QSizePolicy, QLabel, QVBoxLayout, QWidget, QLineEdit, QMessageBox

from PyQt5.QtCore import pyqtSlot, QFile, QTextStream
from sidebar import Ui_MainWindow
from PyQt5 import QtSql
from db_main import *
from functools import partial
from keyboard import KeyboardWidget

# import model
from keras.layers import AveragePooling2D
from keras.applications.mobilenet_v2 import MobileNetV2
from keras.layers import Input, Flatten, Dense, Dropout
from keras.models import Model

# end import model

#*** serial 

# import serial
# ser = serial.Serial(
#     port = '/dev/ttyS0',
#     baudrate = 9600,
#     parity = serial.PARITY_NONE,
#     stopbits = serial.STOPBITS_ONE,
#     bytesize = serial.EIGHTBITS,
#     timeout = 1
#     )

#*** endserial

def get_model():
    model_mobilenet_conv = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

    # Đóng băng các lớp của MobileNetV2
    for layer in model_mobilenet_conv.layers:
        layer.trainable = False

    # Tạo mô hình
    x = model_mobilenet_conv.output
    x = AveragePooling2D(pool_size=(4, 4))(x)
    x = Flatten(name="flatten")(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.5)(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.5)(x)
    output = Dense(7, activation='softmax')(x)

    # Compile
    my_model = Model(inputs=model_mobilenet_conv.input, outputs=output)
    my_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return my_model

# Tải trọng số của mô hình đã được huấn luyện
my_model = get_model()
my_model.load_weights('final_model.hdf5')

classes =  ['Táo', 'Chuối', 'Thanh long', 'Ổi', 'Xoài', 'Cam', 'Thơm']



i = 0
# variable 
num = 1
mydb = MY_DB()
#


class MainWindow(QMainWindow):
    # global flag_menu
    flag_menu = False
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.keyboard_widget = None  # Initialize keyboard_widget attribute as None
        self.ui.btn_home.setChecked(True)
        # self.username1 = ""
        # self.password1 = ""
        self.id_lineedit = QtWidgets.QLineEdit()
        self.name_lineedit = QtWidgets.QLineEdit()
        self.price_lineedit = QtWidgets.QLineEdit()
        self.dialog = None  # Khởi tạo dialog là None

    # keyboard
        self.ui.lb_username.mousePressEvent = lambda event: self.get_username_login()
        self.ui.lb_password.mousePressEvent = lambda event: self.get_password_login()
        self.ui.lb_username_rg.mousePressEvent = lambda event: self.get_username_create()
        self.ui.lb_password_rg.mousePressEvent = lambda event: self.get_password_create()
        self.ui.lb_password_rga.mousePressEvent = lambda event: self.get_passworda_create()
        self.ui.lb_username_c.mousePressEvent = lambda event: self.get_username_change()
        self.ui.lb_old_password_c.mousePressEvent = lambda event: self.get_passwordo_change()
        self.ui.lb_new_password_c.mousePressEvent = lambda event: self.get_passwordn_change()
        self.ui.edit_search_tb.mousePressEvent = lambda event: self.get_input_search()
        self.id_lineedit.mousePressEvent = lambda event: self.get_id_update()
        self.name_lineedit.mousePressEvent = lambda event: self.get_name_update()
        self.price_lineedit.mousePressEvent = lambda event: self.get_price_update()

    #


    ## database
        mydb.connect()
        mydb.openDB()
        mydb.create_products_table()
        mydb.create_userdata_table()
        mydb.create_bill_table()

    ## table_database
        self.ui.table_widget.setColumnWidth(0, 150)  # Đặt kích thước cột 0 là 100
        self.ui.table_widget.setColumnWidth(1, 400)  # Đặt kích thước cột 1 là 200
        self.ui.table_widget.setColumnWidth(2, 250)  # Đặt kích thước cột 2 là 150
        self.ui.btn_show.clicked.connect(self.show_data)
        self.ui.btn_search_tb.clicked.connect(self.search_data)
        self.ui.btn_cgPrice.clicked.connect(self.update_data)
        self.ui.table_widget.itemSelectionChanged.connect(self.GET_ITEM_BY_SELECT)

    ## login
        self.ui.btn_password_c.clicked.connect(self.changePassword)
        self.ui.btn_create.clicked.connect(self.registerAccount)
    ## opencv2
        self.ui.btn_start.clicked.connect(self.start_capture_video)
        self.ui.btn_stop.clicked.connect(self.stop_capture_video)
        self.ui.btn_get_bill.clicked.connect(self.get_bill)
        self.ui.btn_recognition.clicked.connect(self.recognition_video)
        self.thread = {}
    
    ## change opencv2
        self.ui.btn_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.btn_stop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def closeEvent(self, event):
        self.stop_capture_video()
    def stop_capture_video(self):
        if hasattr(self, 'thread') and self.thread.get(1) is not None:
            self.thread[1].stop()
            self.thread[1].wait()  # Chờ đến khi luồng dừng hoàn toàn
            del self.thread[1]  # Xóa luồng khỏi từ điển
    def start_capture_video(self):
        if hasattr(self, 'thread') and self.thread.get(1) is not None:
            self.stop_capture_video()
        self.thread[1] = capture_video(index=1)
        self.thread[1].start()
        self.thread[1].signal.connect(self.show_wedcam)

    def show_wedcam(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.ui.lb_cv2.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(830, 600, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
    def get_bill(self):
        self.generate_invoice()
        mydb.delete_bill_data()

    def recognition_video(self):
        global i
        if hasattr(self, 'thread') and self.thread.get(1) is not None:
            cv_img = self.thread[1].current_frame
            if cv_img is not None:
                # Resize
                test_image = cv2.resize(cv_img, dsize=(224, 224))
                test_image = test_image.astype('float') * 1. / 255
                # Chuyển thành tensor
                test_image = np.expand_dims(test_image, axis=0)

                # Dự đoán
                result = my_model.predict(test_image)

                # Sắp xếp các xác suất dự đoán theo thứ tự giảm dần
                sorted_indexes = np.argsort(result[0])[::-1]
                top_classes_index = sorted_indexes[:3]  # Lấy ba vật có xác suất cao nhất
                predictions = []
                # Hiển thị thông tin về ba vật có xác suất dự đoán cao nhất
                for j, index in enumerate(top_classes_index):
                    prediction = classes[index]
                    probability = round(result[0][index], 3)
                    predictions.append((prediction, probability))
                    print(f"Predicted object {j + 1}: {prediction} (Probability: {probability})")

                # Tăng giá trị của biến đếm
                i += 1    
                return self.select_predict(predictions)

    def select_predict(self, predictions):
        Form = QtWidgets.QWidget()
        dialog = QtWidgets.QDialog(Form)
        dialog.setWindowTitle("Chon San Pham")
        dialog.setModal(True)
        layout = QtWidgets.QVBoxLayout(dialog)

        # Create labels and buttons
        for prediction, probability in predictions:
            label = QtWidgets.QLabel(f"Probability: {probability}")
            layout.addWidget(label)
            button = QtWidgets.QPushButton(prediction)
            layout.addWidget(button)
            button.clicked.connect(partial(self.handle_button_click, prediction=prediction))
        
        dialog.exec_()

        # Move the dialog to the center of the screen
        # Move the dialog to the center of the screen
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        dialog.move(int((resolution.width() / 2) - (dialog.frameSize().width() / 2)),
                    int((resolution.height() / 2) - (dialog.frameSize().height() / 2)))

    def get_weight(self):
        weight = 0.33333333333333333333333
        return round(weight, 3)
        # flag_weight = False  # Cờ để kiểm tra xem đã nhận được giá trị trọng lượng hay chưa
        # ser.reset_input_buffer()  # Xóa dữ liệu còn lại trong bộ đệm của cổng Serial
        # while True:
        #     if ser.in_waiting > 0:
        #         data = ser.readline().decode().strip()
        #         if data:
        #             serial_weight = float(data)
        #             #print("Received data:", serial_weight)
        #             flag_weight = True
        #             continue  # Tiếp tục vòng lặp để đọc và xử lý tất cả dữ liệu còn lại
        #     if flag_weight:
        #         break
        # return serial_weight  # Trả về giá trị trọng lượng cuối cùng

    def Note_Price(self, id, prediction):
        Form = QtWidgets.QWidget()
        weight = self.get_weight()
        print(weight)
        price = mydb.get_price(id)  # Lấy giá từ cơ sở dữ liệu, bạn cần cài đặt hàm get_price() tương ứng trong lớp mydb
        total_price = price * weight
        rounded_total_price = round(total_price, 2)
        mydb.save_to_bill(prediction, weight, price, rounded_total_price)
        QtWidgets.QMessageBox.information(Form, "Tính giá", f"Tổng giá: {rounded_total_price}")  

#    ['Táo', 'Chuối', 'Thanh long', 'Ổi', 'Xoài', 'Cam', 'Thơm']
    def handle_button_click(self, prediction):
        print(prediction)
        if prediction == "Táo":
            # Xử lý cho dự đoán 1
            self.Note_Price(1, prediction)
            print("Đã chọn dự đoán 1")
        elif prediction == "Chuối":
            # Xử lý cho dự đoán 2
            self.Note_Price(2, prediction)
            print("Đã chọn dự đoán 2")
        elif prediction == "Thanh long":
            # Xử lý cho dự đoán 3
            self.Note_Price(3, prediction)
            print("Đã chọn dự đoán 3")
        elif prediction == "Ổi":
            # Xử lý cho dự đoán 4
            self.Note_Price(4, prediction)
            print("Đã chọn dự đoán 4")
        elif prediction == "Xoài":
            # Xử lý cho dự đoán 5
            self.Note_Price(5, prediction)
            print("Đã chọn dự đoán 5")
        elif prediction == "Cam":
            # Xử lý cho dự đoán 6
            self.Note_Price(6, prediction)
            print("Đã chọn dự đoán 6")
        elif prediction == "Thơm":
            # Xử lý cho dự đoán 7
            self.Note_Price(7, prediction)
            print("Đã chọn dự đoán 7")
        else:
            # Xử lý cho trường hợp khác (nếu cần)
            print("Dự đoán không hợp lệ")

    ##
    def generate_invoice(self):
        # Lấy thông tin từ cơ sở dữ liệu "bill"
        invoice_data = mydb.get_bill_data()
        total_price_all = self.calculate_total_price_all()
        self.bill = self.InvoiceWindow(invoice_data, total_price_all)
        self.bill.show()   
    ##
    
    class InvoiceWindow(QMainWindow):
        def __init__(self, invoice_data, total_price_all):
            super().__init__()

            self.setWindowTitle("Hóa đơn")
            self.resize(545, 300)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            layout = QVBoxLayout()
            central_widget.setLayout(layout)

            title_label = QLabel("Hóa đơn:")
            layout.addWidget(title_label)

            # Tạo bảng dữ liệu
            table = QtWidgets.QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Sản phẩm", "Khối lượng", "Giá", "Tổng giá"])

            # Thêm dữ liệu vào bảng
            table.setRowCount(len(invoice_data))
            for row, item in enumerate(invoice_data):
                product_name = item[1]
                weight = item[2]
                price = item[3]
                total_price = item[4]

                # Đặt giá trị cho từng ô trong bảng
                table.setItem(row, 0, QtWidgets.QTableWidgetItem(product_name))
                table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(weight)))
                table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(price)))
                table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(total_price)))

            layout.addWidget(table)

            total_price_label = QLabel(f"Tổng giá tất cả sản phẩm: {total_price_all}")
            layout.addWidget(total_price_label, alignment=Qt.AlignRight)
            # Move the dialog to the center of the screen
            resolution = QtWidgets.QDesktopWidget().screenGeometry()
            self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                        int((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def calculate_total_price_all(self):
        invoice_data = mydb.get_bill_data()
        total_price_all = 0
        for item in invoice_data:
            total_price_all += item[4]  # Sử dụng item[4] để lấy giá trị total_price
        return round(total_price_all, 3)

    ## table_database
    def GET_ITEM_BY_SELECT(self):
        self.select_row = self.ui.table_widget.currentRow()
        if self.select_row != -1:
            self.id = int(self.ui.table_widget.item(self.select_row,0).text())
        print(self.id)

    def show_data(self):
        self.result = mydb.select_all()
        self.ui.table_widget.setRowCount(0)
        for row_num, row_data in enumerate(self.result):
            self.ui.table_widget.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                self.ui.table_widget.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(col_data)))

    def search_data(self):
        keyword = self.ui.edit_search_tb.text()
        result = mydb.sqlquerytitlesearch(keyword)
        self.ui.table_widget.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.ui.table_widget.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                self.ui.table_widget.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(col_data)))

    def create_dialog(self):
        self.dialog = QtWidgets.QDialog(self)  # Gán giá trị cho self.dialog
        self.dialog.setWindowTitle("Cập nhật giá")
        self.dialog.setModal(True)

        layout = QtWidgets.QVBoxLayout(self.dialog)

        id_label = QtWidgets.QLabel("ID:")
        # self.id_lineedit = QtWidgets.QLineEdit()
        # name_label = QtWidgets.QLabel("Tên:")
        # # self.name_lineedit = QtWidgets.QLineEdit()
        price_label = QtWidgets.QLabel("Giá:")
        # self.price_lineedit = QtWidgets.QLineEdit()

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        layout.addWidget(id_label)
        layout.addWidget(self.id_lineedit)
        # layout.addWidget(name_label)
        # layout.addWidget(self.name_lineedit)
        layout.addWidget(price_label)
        layout.addWidget(self.price_lineedit)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.dialog.accept)
        button_box.rejected.connect(self.dialog.reject)

    def update_data(self):
        if self.dialog is not None and self.dialog.isVisible():
            return  # Không thực hiện cập nhật nếu dialog đang hiển thị

        if self.dialog is None:
            self.create_dialog()  # Tạo dialog nếu chưa được khởi tạo
    
        if self.dialog is not None and self.dialog.isHidden():
            self.dialog.setEnabled(True)  # Kích hoạt lại dialog khi keyboard_widget ẩn đi
            self.dialog.show()  # Hiển thị dialog nếu nó tồn tại và đang bị ẩn

        if self.dialog is not None and self.dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.update_product()


    
    # def update_product(self):
    #     id = int(self.id_lineedit.text())
    #     name = self.name_lineedit.text()
    #     price = float(self.price_lineedit.text())

    #     mydb.update_by_id(id, name, price)
    #     self.show_data()
    def update_product(self):
        id = int(self.id_lineedit.text())
        # name = self.name_lineedit.text()
        price = float(self.price_lineedit.text())

        mydb.update_by_id(id, price)
        self.show_data()

    # tinh gia     
    def calculate_price(self, weight):
        price = mydb.get_price(self.id)  # Lấy giá từ cơ sở dữ liệu, bạn cần cài đặt hàm get_price() tương ứng trong lớp mydb
        total_price = price * weight
        return total_price
    
    ##end table_database

    ## register
    def on_btn_register_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(5)

    def registerAccount(self):
        usernamerg = self.ui.lb_username_rg.text()
        passwordrg = self.ui.lb_password_rg.text()
        passwordagain = self.ui.lb_password_rga.text()
        if mydb.sql_registerAccount(usernamerg, passwordrg, passwordagain) == 0:
            self.ui.stackedWidget.setCurrentIndex(0)
            QMessageBox.information(self, "Register", "Register successful!")
        elif mydb.sql_registerAccount(usernamerg, passwordrg, passwordagain) == 1:
            QMessageBox.information(self, "Register", "Failed to register account:")
            self.ui.stackedWidget.setCurrentIndex(5)
        else:
            QMessageBox.information(self, "Register", "Passwords do not match!")
            self.ui.stackedWidget.setCurrentIndex(5)
    ## endregister    

    ## login

    def on_btn_signin_clicked(self):
        if self.checkUser() == True:
            self.flag_menu = True
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.btn_camera.setChecked(True)

    def checkUser(self):
        username1 = self.ui.lb_username.text()
        password1 = self.ui.lb_password.text()
        print(username1, password1)
        if mydb.sql_checkUser(username1, password1) == False:
            QMessageBox.warning(self, "Login", "Login failed!")
            self.ui.stackedWidget.setCurrentIndex(0)
        return mydb.sql_checkUser(username1, password1)
    
    def on_btn_logout_clicked(self):
        self.flag_menu = False
        self.ui.stackedWidget.setCurrentIndex(0)
        self.stop_capture_video()
        # Xóa nội dung trong QLabel
        self.ui.lb_username.clear()
        self.ui.lb_password.clear()


    ##change pass
    def changePassword(self):
        username = self.ui.lb_username_c.text()
        old_password = self.ui.lb_old_password_c.text()
        new_password = self.ui.lb_new_password_c.text()
        if mydb.sql_changePassword(username, old_password, new_password) == 0:
            QMessageBox.information(self, "Change Password", "Change pass successfully!")
            print("Change pass successfully")
        elif mydb.sql_changePassword(username, old_password, new_password) == 1:
            QMessageBox.information(self, "Change Password", "Failed to change password!")
            print("Failed to change password!")
        elif mydb.sql_changePassword(username, old_password, new_password) == 2:
            QMessageBox.information(self, "Change Password", "Incorrect current password!")
            print("Incorrect current password!")
        else :
            QMessageBox.information(self, "Change Password", "Invalid username!")
            print("Invalid username!")
    ##
    # keyboard
    def keyboardpage(self, line_edit, thong_tin):
        if self.dialog is not None and self.dialog.isVisible():
            self.dialog.hide()  # Ẩn dialog nếu nó đang hiển thị

        if self.keyboard_widget is None or self.keyboard_widget.line_edit != line_edit:
            self.keyboard_widget = KeyboardWidget(thong_tin)
            self.keyboard_widget.back_button.clicked.connect(self.handle_back_button)
            self.keyboard_widget.enter_button.clicked.connect(lambda: self.handle_enter_button(line_edit, thong_tin))
            self.keyboard_widget.line_edit = line_edit  # Lưu trữ line_edit
            self.center_widget(self.keyboard_widget)  # Hiển thị keyboard_widget ở giữa màn hình
            self.keyboard_widget.show()  # Hiển thị tiện ích bàn phím
        else:
            if not self.keyboard_widget.isVisible():
                self.center_widget(self.keyboard_widget)  # Hiển thị keyboard_widget ở giữa màn hình
                self.keyboard_widget.raise_()  # Đưa keyboard_widget lên trên cùng
                self.keyboard_widget.show()

    def center_widget(self, widget):
        # Lấy kích thước của màn hình
        screen_geometry = QApplication.instance().desktop().availableGeometry()
        screen_center = screen_geometry.center()
        # Lấy kích thước widget
        widget_geometry = widget.frameGeometry()
        widget_center = widget_geometry.center()
        # Tính toán vị trí mới cho widget
        new_position = screen_center - widget_center
        widget.move(new_position)

    def handle_back_button(self):
        if self.keyboard_widget is not None:
            self.keyboard_widget.close()  # Close the keyboard widget

    def handle_enter_button(self, line_edit, thong_tin):
        if self.keyboard_widget is not None:
            text = self.keyboard_widget.get_text()  # Lấy văn bản từ keyboard_widget
            line_edit.setText(text)  # Gán văn bản vào line_edit (lb_username hoặc lb_password)
            self.keyboard_widget.close()  # Đóng keyboard_widget
        if thong_tin == "id update" or thong_tin == "name update"  or thong_tin == "price update":
            self.dialog.show()

        
    def get_username_login(self):
        print("get_username_login")
        self.username1 = self.ui.lb_username  # Lưu giá trị của line_edit vào self.username1
        self.keyboardpage(self.username1, "username")

    def get_password_login(self):
        print("get_password_login")
        self.password1 = self.ui.lb_password  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.password1, "password")

    def get_username_create(self):
        print("get_username_create")
        self.usernamerg = self.ui.lb_username_rg  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.usernamerg, "username")

    def get_password_create(self):
        print("get_password_create")
        self.passwordrg = self.ui.lb_password_rg  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.passwordrg, "password")
    
    def get_passworda_create(self):
        print("get_passworda_create")
        self.passwordagain = self.ui.lb_password_rga  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.passwordagain, "password again")

    def get_username_change(self):
        print("get_username_change")
        self.username = self.ui.lb_username_c  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.username, "username")

    def get_passwordo_change(self):
        print("get_passwordo_change")
        self.old_password = self.ui.lb_old_password_c  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.old_password, "password old")
    
    def get_passwordn_change(self):
        print("get_passwordn_change")
        self.new_password = self.ui.lb_new_password_c  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.new_password, "password new")

    def get_input_search(self):
        print("get_input_search")
        self.search_text = self.ui.edit_search_tb  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.search_text, "input search")

    def get_id_update(self):
        print("get_id_update")
        self.id_text = self.id_lineedit  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.id_text, "id update")

    def get_name_update(self):
        print("get_name_update")
        self.name_text = self.name_lineedit  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.name_text, "name update")

    def get_price_update(self):
        print("get_price_update")
        self.price_text = self.price_lineedit  # Lưu giá trị của line_edit vào self.password1
        self.keyboardpage(self.price_text, "price update")


    ## endkeyboard

     ## Function for searching
    def on_btn_search_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(5)
        search_text = self.ui.input_search.text().strip()
        if search_text:
            self.ui.lb_search.setText(search_text)

    ## functions for changing menu page
    def on_btn_home_toggled(self):
        if self.flag_menu == False:
            self.ui.stackedWidget.setCurrentIndex(0)
        else:
            self.ui.stackedWidget.setCurrentIndex(6)

    def on_btn_camera_toggled(self):
        if self.flag_menu == True:
            self.ui.stackedWidget.setCurrentIndex(1)
        else:
            self.ui.stackedWidget.setCurrentIndex(0)

    def on_btn_order_toggled(self):
        if self.flag_menu == True:
            self.ui.stackedWidget.setCurrentIndex(2)
        else:
            self.ui.stackedWidget.setCurrentIndex(0)

    def on_btn_account_toggled(self):
        if self.flag_menu == True:
            self.ui.stackedWidget.setCurrentIndex(3)
        else:
            self.ui.stackedWidget.setCurrentIndex(0)

## opencv2
class capture_video(QThread):
    signal = pyqtSignal(np.ndarray)

    def __init__(self, index):
        self.index = index
        self.cap = None  # Biến instance để lưu trạng thái camera
        self.current_frame = None  # Thêm thuộc tính current_frame
        print("start threading", self.index)
        super(capture_video, self).__init__()

    def run(self):
        self.cap = cv2.VideoCapture(0)  # Mở camera
        while True:
            ret, cv_img = self.cap.read()
            if ret:
                self.current_frame = cv_img  # Lưu trữ hình ảnh hiện tại
                self.signal.emit(cv_img)

    def stop(self):
        print("stop threading", self.index)
        if self.cap is not None:
            self.cap.release()  # Giải phóng camera
        self.terminate()
##

def closeWindow():
    global mydb
    mydb.disconnect()
    print("Close App!!!")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(closeWindow)
    ## loading style file
    with open("style.qss", "r") as style_file:
        style_str = style_file.read()
    app.setStyleSheet(style_str)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
