import socket
import base64
import os
import json
import re
import time
class Receive:
    def getData(self,response, start, end,type):
        start_index = response.find(start) + len(start)
        end_index = response.find(end, start_index)
        subject=response[start_index:end_index]
        if type=="img":
            subject = subject.replace(b"\r\n", b"")
        else:
            subject_part = subject.strip()
            # Giả sử chuỗi có thể nằm trong nhiều dòng, cần nối chúng lại
            subject_lines = subject_part.split(end)
            subject = b" ".join(subject_lines).decode("utf-8")
        return subject
    def getSubject(self,response):
        return self.getData(response,b'Subject:',b'\r\n',"normal")
    def getAddress(self,response):
        return self.getData(response,b'From:',b'\r\n',"normal")
    def getText(self,response):
        return self.getData(response,b"Content-Transfer-Encoding: 7bit",b"--====","normal")
    def moveToFolder(self,id_mail, file_name, email_content): 
        curr_file=os.path.dirname(__file__)                    
        save_folder = os.path.join(curr_file, file_name)
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        # Tiến hành lưu trữ email vào thư mục
        email_file_path = os.path.join(save_folder, f"{id_mail}.txt")
        with open(email_file_path, "w", encoding="utf-8") as email_file:
            email_file.write(email_content)
    
    def info_emails(self,file):
        with open(file, 'r') as contentFile:
            content=contentFile.read()
        encoded_text = content.replace('\n', '\r\n').encode('utf-8')
        address=self.getAddress(encoded_text)
        subject=self.getSubject(encoded_text)
        return address, subject
   
    def getfileName(self,data):
        attachment_matches = re.finditer(r"Content-Disposition: attachment; filename=(.+)\n\n", data)

        # Danh sách để lưu trữ các tên file
        attached_files = []

        for match in attachment_matches:
            attachment_name = match.group(1)
            attached_files.append(attachment_name)
        return attached_files
    def selectSaveFolder(self,link):
        # Kiểm tra xem thư mục tồn tại chưa, nếu chưa thì tạo mới
        curr_file=os.path.dirname(__file__)                    
        save_folder = os.path.join(curr_file, link)
        print(save_folder)
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
            print(f"Created folder: {save_folder}")
        else:
            print(f"Using existing folder: {save_folder}")
        return save_folder

    def getAttachData(self,response, start):
        start_index = response.find(start) + len(start)

        subject_part = response[start_index:].strip()

        subject_part = subject_part.replace(b"\r\n", b"")
        return subject_part

    def getAttachFile(self,desired_filename,attached_files,data,save_folder):
        for i in desired_filename:
                for j in attached_files:
                    if j == '\"'+i+'\"':
                        
                        attachment_data=self.getAttachData(data,f'Content-Disposition: attachment; filename="{i}"\r\n\r\n'.encode())
                        try:
                            decoded_data = base64.b64decode(attachment_data)
                            print("valid base64.")
                        except Exception as e:
                            print(f"Error decoding base64: {e}")

                        # Lưu tệp đính kèm
                        filename = os.path.join(save_folder, f"{i}")
                        with open(filename, 'wb') as file:
                            file.write(decoded_data)
                            break  # Đã tìm thấy tệp tin, có thể thoát khỏi vòng lặp
                else:
                # Nếu đến đây, không tìm thấy tệp tin mong muốn
                    print(f"Attachment with filename '{i}' not found.")
    def print_email(self,id_email, folder):
        curr_file=os.path.dirname(__file__)
        save_folder = os.path.join(curr_file, f"{folder}\{id_email}.txt")
        with open(save_folder, 'r') as contentFile:
            content=contentFile.read()
        # print(content)

        encoded_text = content.replace('\n', '\r\n').encode('utf-8')
        text=self.getText(encoded_text)
        print(f"Nội dung email {id_email}:\n",text)

        file=self.getfileName(content)
        if file:
            print("Trong email này có attached file: ")
            for i in file:
                print(i, " ")
            answer = input("ban co muon tai file khong: ") 
            if(answer == "co"):
                pathFile = input("nhap duong dan file: ") 
                numOfFile= int(input("nhap so file muon tai: "))
                desired_filename=[]
                for i in range(0,numOfFile):
                    name = input("nhap file muon tai: ") 
                    pathFile = self.selectSaveFolder(pathFile)
                    print(pathFile)
                    desired_filename.append(name)
                self.getAttachFile(desired_filename,file,encoded_text,pathFile)
            

    def getNameFile(self,filePath):
        file_name, file_extension = os.path.splitext(os.path.basename(filePath))
        return file_name
    def is_email_read(self,filepath, subject):
        # Read the content of the file
        try:
            with open(filepath, 'r') as file:
                list_read = json.load(file)
                file_list = os.listdir(subject)
                for file_name in file_list:
                    file_path = os.path.join(subject, file_name)
                    extracted_email_id,file_extension = os.path.splitext(os.path.basename(file_path))
                    #print(extracted_email_id)
                    address, infor_subject = self.info_emails(file_path)
                    if extracted_email_id in list_read:
                        print(f"{extracted_email_id}. < {address} >, < {infor_subject} > ")
                    else:
                        print(f"{extracted_email_id}.(chưa đọc) < {address} >, < {infor_subject} > ")
        except FileNotFoundError:
            # If the file does not exist, create a new one
            print("File does not exist. Creating a new one and marking email as read.")

        # Write the updated list back to the file
        with open(filepath, 'w') as file:
            json.dump(list_read, file)
    def match_rules(self,object,listKeys,ruleName,i,email_content):
        for key in listKeys:
            if key in object:
                self.moveToFolder(i,ruleName,email_content)
                return True
        return False
    #response là data chưa được decode   
    def catogorizeEmails(self,response,i): 
        #đọc file config
        with open("config.json", 'r') as config_file:
            config_data = json.load(config_file)   
        email_content=response.decode()
        address=self.getAddress(response)
        subject=self.getSubject(response)
        text=self.getText(response)
        isFiltered= False
        for filter_rule in config_data['filters']:                    
            if 'subject' in filter_rule:
                isFiltered=self.match_rules(subject,filter_rule['subject'],filter_rule['folder'],i,email_content)
                if isFiltered==True:
                    break
            elif 'address' in filter_rule:
                isFiltered=self.match_rules(address,filter_rule['address'],filter_rule['folder'],i,email_content)
                if isFiltered==True:
                    break
            elif 'spam_words' in filter_rule:
                for word in filter_rule['spam_words']:
                    if (word in text) or (word in subject):                    
                        self.moveToFolder(i,filter_rule['folder'],email_content)                    
                        isFiltered=True
                        break
        if isFiltered==True:
            return
        self.moveToFolder(i,"INBOX",email_content)   
    
# ------------------------------------------------------------------------------------------------------------------------------

    def receive_email(self,recieve,password):
        time.sleep(1)
    # Thông tin tài khoản email
        username = recieve
        password = password
        with open("config.json", 'r') as config_file:
            config_data = json.load(config_file)
        pop3_server = config_data['pop3_server']
        pop3_port = config_data['pop3_port']  

        # Tạo kết nối socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((pop3_server, pop3_port))
            
            # Nhận phản hồi từ server
            response = client_socket.recv(1024).decode()
            print(response)
            
            # Gửi lệnh login
            client_socket.sendall(b'CAPA\r\n')
            response = client_socket.recv(1024).decode()
            print(response)

            # Xác thực tài khoản email
            client_socket.sendall(f'USER {username}\r\n'.encode())
            response = client_socket.recv(1024).decode()

            client_socket.sendall(f'PASS {password}\r\n'.encode())
            response = client_socket.recv(1024).decode()
            
            # Chọn hộp thư
            client_socket.sendall(b'LIST\r\n')
            response = client_socket.recv(1024).decode()
            print(response)
        

            # Lấy danh sách ID của các email
            email_ids = [id for id in response.split() if id.isdigit()]
            email_ids = email_ids[::2]
        
            for i, email_id in enumerate(email_ids):
                # Gửi lệnh RETR để lấy nội dung của email
                #is_email_read("filePath.txt",email_id)
                print(email_id)
                try:
                    with open("fileDownload.txt", 'r') as file:
                        list_read = json.load(file)
                        if email_id in list_read:
                           print("da tai")
                           continue
                        with open("fileDownload.txt", 'w') as file:
                            list_read.append(email_id)
                            json.dump(list_read, file)
                except FileNotFoundError:
                    print("File does not exist. Creating a new one and marking email as read.")
                client_socket.sendall(f'RETR {email_id}\r\n'.encode())
                response = client_socket.recv(3400000024)
                self.catogorizeEmails(response,email_id)
            # client_socket.sendall(f'RETR {12}\r\n'.encode())
            # response = client_socket.recv(3400000024)
            #print(response)         
            #self.save_png(response,13)


        # Gửi lệnh QUIT để đóng kết nối
            client_socket.sendall(b'QUIT\r\n')
            response = client_socket.recv(1024).decode()

            print("Email received successfully.")
        
# ---------------------------------------------------------------------------------------------------------------------
    def Read_content(self,folder):
        while True:
            list_read = []
            n = input("Bạn muốn đọc Email thứ mấy: (hoặc nhấn enter để thoát ra ngoài, hoặc nhấn 0 để xem lại danh sách email)") 
            if n == "0":
                self.is_email_read("filePath.txt", folder)
            elif n == '':
                break
            else: 
                with open("filePath.txt", 'r') as file:
                    list_read = json.load(file)

                    if n in list_read:
                        self.print_email(n,folder)
                    else:
                        list_read.append(n)
                        self.print_email(n,folder)
            with open("filePath.txt", 'w') as file:
                json.dump(list_read, file)
# p.receive_email("tranquangthuan132@gmail.com","12112004")
# while(True):
#     print("Đây là danh sách folder của bạn!!")
#     print("1. Inbox ")
#     print("2. Project")
#     print("3. Important")
#     print("4. Work")
#     print("3. Spam")
#     n = input("Bạn muốn xem phòng email trong folder nào: (nhấn enter để thoát ra ngoai) ")
#     if(n == ""):
#         break
#     elif n == "1":
#         p.is_email_read("filePath.txt","INBOX")
#     elif n == "2":
#         p.is_email_read("filePath.txt","PROJECT")
#     elif n == "3":
#         print(1)
#         p.is_email_read("filePath.txt","IMPORTANT")
#         p.Read_content("IMPORTANT")
        
#     elif n == "4":
#         p.is_email_read("filePath.txt","WORK")
#     elif n == "5": 
#         p.is_email_read("filePath.txt","SPAM")
#         p.Read_content("SPAM")
        
