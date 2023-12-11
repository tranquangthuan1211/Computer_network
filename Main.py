from ClientReceive import Receive
from ClientSend import Send
import threading
import time

# Create an instance of Receive
clientReceive = Receive()
def receive_email_thread(Receive):
    Receive.receive_email("tranquangthuan132@gmail.com", "12112004")
   

if __name__ == "__main__":
    while(True):
        p1 = threading.Thread(target=receive_email_thread, args=(clientReceive,))
        p1.start()
        n = int(input("input your choose!!! "))
        if(n == 1):
            clientSend = Send()
            listReceive = ["tranquangthuan132@gmail.com"]
            pathFiles = []
            ccEmails = []
            bccEmails = []
            subject = ""
            content = ""
            while(True):
                print("Đây là thông tin soạn email: (nếu không điền vui lòng nhấn enter để bỏ qua ")
                print(f"To: {listReceive}")
                print(f"CC: {ccEmails}")
                print(f"BCC: {bccEmails}")
                print(f"Subject: {subject}")
                print(f"Content: {content}")

                infor = str(input())
                if(infor == ''):
                    break
                else:
                    print("Nhập danh sách người nhận (cách address cách nhau bởi dấu space")
                    listReceive=input("To: ")
                    cc=input("CC: ")
                    bcc=input("BCC: ")
                    listReceive = list(map(str, listReceive.split()))
                    ccEmails=list(map(str, cc.split()))
                    bccEmails=list(map(str, bcc.split()))
                    subject = input("Subject: ")
                    content = input("Content: ")
            ccEmails = listReceive + bccEmails + ccEmails
            print(ccEmails)
            file = int(input("Có gửi kèm file (1. có, 2. không): "))
            if(file == 1):
                numberFile = int(input("Số lượng file muốn gửi: "))
                for i in range (0,numberFile):
                    pathFile = str(input(f"Cho biết đường dẫn file thứ {i + 1}"))
                    pathFiles.append(pathFile)
            for receiver in ccEmails:
                clientSend.send_email(receiver,pathFiles,ccEmails,bccEmails,subject,content)
        elif(n == 2):
            while True:
                time.sleep(1)
                print("Đây là danh sách folder của bạn!!")
                print("1. Inbox ")
                print("2. Project")
                print("3. Important")
                print("4. Work")
                print("5. Spam")
                n = input("Bạn muốn xem phòng email trong folder nào: (nhấn enter để thoát ra ngoai) ")
                if n == "":
                    break
                elif n == "1":
                    clientReceive.is_email_read("filePath.txt", "INBOX")
                    clientReceive.Read_content("INBOX")
                elif n == "2":
                    clientReceive.is_email_read("filePath.txt", "PROJECT")
                    clientReceive.Read_content("PROJECT")
                elif n == "3":
                    clientReceive.is_email_read("filePath.txt", "IMPORTANT")
                    clientReceive.Read_content("IMPORTANT")
                elif n == "4":
                    clientReceive.is_email_read("filePath.txt", "WORK")
                    clientReceive.Read_content("WORK")
                elif n == "5":
                    clientReceive.is_email_read("filePath.txt", "SPAM")
                    clientReceive.Read_content("SPAM")
        elif (n == 3):
            break
    