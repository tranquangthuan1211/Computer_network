import socket
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import os
import json
class Send: 
    def get_file_extension(self,file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower()

    def send_email(self,receiver, fileSend, ccMails, bccMails,subject,content):
        with open("config.json", 'r') as config_file:
            config_data = json.load(config_file)
        # Thông tin tài khoản email
        #sender_email = "tranquangthuan132@gmail.com"
        sender_email="abc@gmail.com"
        receiver_email = receiver
        password = "12112004"
        smtp_server = config_data['smtp_server']
        smtp_port = config_data['smtp_port']  
        # Tạo đối tượng MIMEMultipart
        message = MIMEMultipart()
        message["From"] = sender_email
        if receiver in bccMails:
            message["To"] = receiver_email
        else: 
            message["To"] =",".join(ccMails)
        message["Subject"] = subject
        message.attach(MIMEText(content, "plain"))

        for filePath in fileSend:
            if self.get_file_extension(filePath) == '.png':
                # Đính kèm ảnh
                with open("anhDeMo.png", "rb") as attachment:
                    image = MIMEImage(attachment.read(), name="dot.png")
                    image["Content-Disposition"] = f'attachment; filename="{attachment.name}"'
                    message.attach(image)
            elif self.get_file_extension(filePath) == '.docx':
                # Đính kèm file
                with open("test.docx", "rb") as file:
                    attachment = MIMEApplication(file.read(), name="test.docx")
                    attachment["Content-Disposition"] = f'attachment; filename="{file.name}"'
                    message.attach(attachment)

        # Tạo kết nối socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((smtp_server, smtp_port))

            # Nhận phản hồi từ server
            response = client_socket.recv(1024).decode()
            print(response)

            # Gửi lệnh EHLO để bắt đầu phiên làm việc
            client_socket.sendall(b'EHLO example.com\r\n')
            response = client_socket.recv(1024).decode()
            print(response)

            # Xác thực tài khoản email
            client_socket.sendall(b'AUTH LOGIN\r\n')
            response = client_socket.recv(1024).decode()
            print(response)

            # Gửi tên đăng nhập và mật khẩu dưới dạng Base64
            client_socket.sendall(base64.b64encode(sender_email.encode()) + b'\r\n')
            response = client_socket.recv(1024).decode()
            print(response)

            client_socket.sendall(base64.b64encode(password.encode()) + b'\r\n')
            response = client_socket.recv(1024).decode()
            print(response)

            # Gửi lệnh MAIL FROM và RCPT TO cho người nhận chính
            client_socket.sendall(f'MAIL FROM: <{sender_email}>\r\n'.encode())
            response = client_socket.recv(1024).decode()
            print(response)

            client_socket.sendall(f'RCPT TO: <{receiver_email}>\r\n'.encode())
            response = client_socket.recv(1024).decode()
            print(response)

            # Gửi lệnh DATA để bắt đầu gửi nội dung email
            client_socket.sendall(b'DATA\r\n')
            response = client_socket.recv(1024).decode()
            print(response)
            message_size_bytes = len(message.as_string().encode())
            message_size_kb = message_size_bytes / 1024  # Chuyển đổi dung lượng sang kilobytes

            if( message_size_kb > 3000):
                client_socket.sendall(b'\r\n.\r\n')
                print('kich thuoc qua lon khong the gui !!!')
                client_socket.sendall(b'QUIT\r\n')
                response = client_socket.recv(1024).decode()
                print(response)
            else:
            # Gửi nội dung email
                print(message_size_kb)
                client_socket.sendall(message.as_string().encode())
                client_socket.sendall(b'\r\n.\r\n')
                response = client_socket.recv(1024).decode()
                print(response)

                # Gửi lệnh QUIT để đóng kết nối
                client_socket.sendall(b'QUIT\r\n')
                response = client_socket.recv(1024).decode()
                print(response)

                print("Email sent successfully.")
