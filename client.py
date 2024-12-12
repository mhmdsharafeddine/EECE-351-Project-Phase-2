import threading as thread
import sys
import json
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox,QComboBox,QSpinBox,QTabWidget, QTextEdit,QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import socket
import google.generativeai as ai
from PyQt5.QtGui import QFont
import os
from PIL import Image
from colorama import init, Fore, Style, Back
from datetime import datetime
import io
currentchat = ""
olderchat = ""
nametouse= ""
messageid = 0
socket_lock = thread.Lock()
savedChat_lock = thread.Lock()
savedchat = {}
desplayedmessage = {}
# Server connection
HOST = '127.0.0.1'  # Update with the correct host if needed
PORT =int(input("Please enter a Port Number: "))
client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try: 
    client.connect((HOST, PORT))
    API_KEY = 'AIzaSyCQAnoAGDqCebJBUotcnQz8ttllnVyb9pM'
    ai.configure(api_key=API_KEY)

    # Create the generative model and chat instance
    model = ai.GenerativeModel("gemini-pro")
    chat = model.start_chat()
    
except Exception as e:
    print(f"Erorr: {e}")
    client.close()
recievesock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
recievesock.bind(('127.0.0.1',0))
recievesock.listen(100)
(ip,port) = recievesock.getsockname()
client.send(json.dumps((ip,port)).encode())


def recvmsg():
    global recievesock
    global messageid
    while True:
        try:
            try:
                conn,addr = recievesock.accept()
            except Exception as e:
                print(e)
            newmsg = conn.recv(1024).decode()
            other = newmsg.split("~")[0]
            with savedChat_lock:
                if other in savedchat:
                    messageid +=1
                    savedchat[other].append((newmsg.split("~")[1],0,messageid))
                else:
                    messageid +=1
                    savedchat[other] = [(newmsg.split("~")[1],0,messageid)]
        except Exception as e:
            print(e)

class FirstScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        # Welcome message
        title = QLabel("Welcome to AUB's New Shop!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # ComboBox for selecting Register or Login
        self.comboBox = QComboBox(editable=False)
        self.comboBox.setGeometry(200, 150, 150, 30)
        font = QFont('Arial', 10) 
        self.comboBox.setFont(font)
        self.comboBox.addItem("Register")
        self.comboBox.addItem("Login")
        layout.addWidget(self.comboBox)
        
        # Button for action
        self.button = QPushButton("Proceed")
        self.button.setGeometry(200, 150, 150, 30)
        font = QFont('Arial', 10) 
        self.button.setFont(font)
        self.button.clicked.connect(self.on_button_click)  # Single dynamic connection
        layout.addWidget(self.button)

        self.setLayout(layout)
        
    def on_button_click(self):
        if self.comboBox.currentText() == "Register":
            self.go_to_signup()
        elif self.comboBox.currentText() == "Login":
            self.go_to_login()
    def go_to_login(self):
        self.main_window.switch_to_login()

    def go_to_signup(self):
        self.main_window.switch_to_signup()

# Signup form
class Signup(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Sign Up")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Name")
        layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Email")
        layout.addWidget(self.email_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        title = QLabel("Please enter your preferred currency:")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        self.comboBox = QComboBox(editable=False)
        self.comboBox.setGeometry(200, 150, 150, 30)
        font = QFont('Arial', 10) 
        self.comboBox.setFont(font)
        self.comboBox.addItem("USD (United States Dollars)")
        self.comboBox.addItem("EUR (Euros)")
        self.comboBox.addItem("CAD (Canadian Dollars)")
        self.comboBox.addItem("LBP (Lebanese Pounds)")
        layout.addWidget(self.comboBox)
        signup_button = QPushButton("Sign Up")
        signup_button.clicked.connect(self.signup)
        layout.addWidget(signup_button)

        self.setLayout(layout)

    def signup(self):
            name = self.name_input.text()
            email = self.email_input.text()
            username = self.username_input.text()
            password = self.password_input.text()
            currency=self.comboBox.currentText()
            # Start the registration process
            client.send("Register".encode())
            response = client.recv(1024).decode()
            print(response)
            # Input user details
            if response == "Ready to register":
                data={"name": name,
                "email": email,
                "username": username,
                "password": password,
                "currency":currency}
                data=json.dumps(data)
                client.send(data.encode())
                x=client.recv(1024).decode()
                if(x=="Registration complete"):
                    QMessageBox.information(self, "Success", x)
                    global nametouse
                    nametouse = username
                    self.main_window.switch_to_main_app()
                elif(x=="Either email or username exists"):
                    self.handle_existing_user(x)
                else:
                    QMessageBox.warning(self, "Failed", x)
    def handle_existing_user(self, message):
        reply = QMessageBox.question(
            self,
            "Account Exists",
            f"{message}\nTry logging in?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.main_window.switch_to_login()
        else:
            QMessageBox.information(self, "Retry", "Please try signing up with a different username or email.")

##WORK ON LOGIN
class Login(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        client.send("Login".encode())
        a=client.recv(1024).decode()
        print(a)
        command = {"username": username, "password": password}
        command=json.dumps(command)
        client.send(command.encode())
        #if a== "Ready to login":
        j=client.recv(1024).decode()
        print(j)
        if(j=="Error"):
            self.handle_error(j)
        elif(j=="Login complete"):
                QMessageBox.information(self, "Logged in", j)
                global nametouse
                nametouse = username
                self.main_window.switch_to_main_app()

        else:
            QMessageBox.warning(self, "Failed",j)
    def handle_error(self, message):
         reply = QMessageBox.question(
             self,
             "Either username or password is wrong",
             f"{message}\nTry signing up?",
             QMessageBox.Yes | QMessageBox.No,
         )

         if reply == QMessageBox.Yes:
             self.main_window.switch_to_signup()
         else:
             QMessageBox.information(self, "Retry", "Please check your username and password.")

# Main application screen
class MainAppScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.sendsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.user_widgets = {}
        self.main_window = main_window
        main_layout=QVBoxLayout()
        t= thread.Thread(target=recvmsg)
        t.start()
        self.tab_widget = QTabWidget()    
        self.layout = QVBoxLayout()
        self.product_tab = QWidget()
        layout=self.layout    
        self.username_label = QLabel("Welcome!")
        self.username_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.username_label)

        
        button4 = QPushButton("Add Product")
        button4.clicked.connect(self.Add_Product)
        layout.addWidget(button4)

        button1 = QPushButton("Buy Products")
        button1.clicked.connect(self.Buy_Products)
        layout.addWidget(button1)
        
        
        button3 = QPushButton("View products of")
        button3.clicked.connect(self.View_products_of)
        layout.addWidget(button3)
        
        button5 = QPushButton("Search for product")
        button5.clicked.connect(self.Search_for_product)
        layout.addWidget(button5)
        
        button6=QPushButton("View Picture of Certain Product")
        button6.clicked.connect(self.Start_View_Picture)
        layout.addWidget(button6)
        
        button2 = QPushButton("View my Customers")
        button2.clicked.connect(self.View_my_Customers)
        layout.addWidget(button2)
        
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)
        
        self.product_tab.setLayout(layout)
        self.tab_widget.addTab(self.product_tab, "Products")
        
        self.chatbot_tab = QWidget()
        self.chatbot_layout = QVBoxLayout()
        self.chatbot_label = QLabel("Welcome to AUB Bouqtique AI Chatbot")
        self.chatbot_label.setAlignment(Qt.AlignCenter)
        self.chatbot_label2 = QLabel('Please type "bye" in order to return to main page and please mention the products name as much as you can when asking about a product')
        self.chatbot_label2.setAlignment(Qt.AlignCenter)
        self.chatbot_layout.addWidget(self.chatbot_label)
        self.chatbot_layout.addWidget(self.chatbot_label2)
        button_AI = QPushButton("Press to start chatting with AI bot")
        button_AI.clicked.connect(self.Start_AI_Chat)
        self.chatbot_layout.addWidget(button_AI)
        self.chatbot_tab.setLayout(self.chatbot_layout)
        self.tab_widget.addTab(self.chatbot_tab, "Chatbot")
        
        
        
        self.View_tab = QWidget()
        self.View_layout = QVBoxLayout()
        self.View_label = QLabel("Products :")
        d1=client.recv(1024).decode()
        print("yes")
        self.View_label.setAlignment(Qt.AlignCenter)
        self.View_layout.addWidget(self.View_label)
        
        if(d1=="No"):
            print(d1)
        elif(d1=="No products on server"):
            print(d1)
        else:
            print("json")
        
        
        if (d1=="No products on server"):
            title = QLabel(d1)
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: bold;")
            layout.addWidget(title)       
        elif(d1!= "No"):
            title = QLabel("Products: ")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: bold;")
            self.View_layout.addWidget(title) 
            d=json.loads(d1)
            for key in d:
                self.View_layout.addWidget(QLabel(key+ ":" +str(d[key])))
        
        button = QPushButton("Refresh")
        button.clicked.connect(self.button1)
        
        self.View_layout.addWidget(button)
        self.View_tab.setLayout(self.View_layout)
        self.tab_widget.addTab(self.View_tab, "View") 



                
        '''----------------------------------------------------'''








        self.ChatWidget = QWidget()
        self.Hlayout = QHBoxLayout(self.ChatWidget)
        self.Chatlayout = QVBoxLayout()
        self.users = QtWidgets.QGroupBox(self.ChatWidget)
        self.userslayout = QVBoxLayout(self.users)
        self.ChatWidget.setLayout(self.Hlayout)

        
        self.users.setTitle("Users")


        self.user2 = QtWidgets.QScrollArea(self.users)
        self.userslayout.addWidget(self.user2)
        self.user2.setWidgetResizable(True)

        self.userslayout.addWidget(self.user2)

        self.follow = QtWidgets.QPushButton(self.users)
        self.follow.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.follow.setMaximumWidth(200)
        self.users.setMaximumWidth(250)
        self.userslayout.addWidget(self.follow)
        self.follow.setText("follow")
        self.Hlayout.addWidget(self.users)

        self.user_container = QtWidgets.QWidget()
        self.users_layoutcontainer = QtWidgets.QVBoxLayout(self.user_container)
        self.user2.setWidget(self.user_container)
        

        self.chatting  = QtWidgets.QGroupBox(self.ChatWidget)
        self.chatting.setTitle("Chat bocs")
        self.chat_layout = QtWidgets.QVBoxLayout(self.chatting)

        self.messages = QtWidgets.QScrollArea(self.chatting)
        self.messages.setWidgetResizable(True)


        self.messages_container = QtWidgets.QWidget()
        self.messages_layout = QtWidgets.QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(QtCore.Qt.AlignTop)
        self.messages.setWidget(self.messages_container)
        
        self.typing = QtWidgets.QLineEdit(self.ChatWidget)
        self.typing.setPlaceholderText("please put ur message ")

        self.send = QtWidgets.QPushButton(self.ChatWidget)
        self.send.setText("press me")

        self.chat_layout.addWidget(self.messages)
        self.chat_layout.addWidget(self.typing)
        self.chat_layout.addWidget(self.send)
        self.Hlayout.addWidget(self.chatting)



        self.tab_widget.addTab(self.ChatWidget,"Chat")
        
        '''---------------------------------------------------------------------'''  
        
        
        
        
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
        self.tab_widget.currentChanged.connect(self.tab_change)
        self.send.clicked.connect(self.sendmessage)
    

    def getip(self,user):
        global currentchat
        global olderchat
        if len(user) <1:
            return 
        with socket_lock:
            olderchat = currentchat
            currentchat = user
            if self.sendsocket and currentchat != olderchat:
                self.sendsocket.close()
            client.send("getip".encode("utf-8"))
            client.send(user.encode())

            ipaddress =  json.loads(client.recv(1024).decode())
            print(f"ipaddress   {ipaddress}")
        

        try:
            self.sendsocket =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except Exception as e:
            print("error ", e)

        try:
            self.sendsocket.connect((ipaddress[0],int(ipaddress[1])))
        except Exception as e:
            print("error " ,e)
        return (ip,port)
        
    def sendmessage(self):
        global messageid
        message = self.typing.text()
        global nametouse
        print(nametouse)
        with socket_lock:
            final = nametouse+"~"+message
            self.sendsocket.send(final.encode("utf-8"))
            self.typing.clear()
            with savedChat_lock:
                if currentchat in savedchat:
                    messageid +=1
                    savedchat[currentchat].append((message,1,messageid))
                    print("yes")
                    return
                messageid +=1
                savedchat[currentchat] = [(message,1,messageid)]
                print("yes_")
    

    

    def updatedchat(self,user):
        global savedchat
        global desplayedmessage
        global olderchat
        if len(user) < 1:
            return
        if user!= olderchat and len(user) > 0 and len(olderchat)>0 :
            for i in reversed(range(self.messages_layout.count())):
                widget = self.messages_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            desplayedmessage[olderchat] = set([])
        
        if user not in savedchat:
            return
        messages = savedchat[user]
        try:
            for message in messages:
                if user in desplayedmessage and message[2] not in desplayedmessage[user]:
                    message_label = QtWidgets.QLabel(message[0])
                    message_label.setStyleSheet(
                        '''Qlabel {
                        background-color: #99ccff;
                        color: black;
                        border-radius: 10px;
                        margin: 5px

                        }

                        '''
                    )

                    message_label.setWordWrap(True)
                    if message[1] == 1:
                        self.messages_layout.addWidget(message_label,alignment=QtCore.Qt.AlignmentFlag.AlignRight)
                    else:
                        self.messages_layout.addWidget(message_label,alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
                    desplayedmessage[user].add(message[2])
        except Exception as e:
            print(e)
    





                
            









    def showusers(self):
        global nametouse
        client.send("Chat".encode())
        new = set(json.loads(client.recv(1024).decode()))
        current = set(self.user_widgets.keys())
        for user in current - new:
            widget = self.user_widgets.pop(user)
            self.users_layoutcontainer.removeWidget(widget)
            widget.deleteLater()
        for user in new - current:
            user_widget = QtWidgets.QPushButton(user)
            user_widget.setStyleSheet("border: 3px solid black; padding 4px;")
            if user!= nametouse:

                self.users_layoutcontainer.addWidget(user_widget)

                user_widget.clicked.connect(lambda : self.getip(user))
                user_widget.clicked.connect(lambda : self.updatedchat(user))
                tt = client.recv(1024).decode()
                print("shooww" , tt)
        
                self.user_widgets[user] = user_widget
        




        
    def tab_change(self):
        currentindex = self.tab_widget.currentIndex()

        if self.tab_widget.widget(currentindex) == self.ChatWidget:

            self.showusers()



     
    def button1(self):
        client.send("refresh".encode())
        self.main_window.switch_to_main_app()
     
    def Start_AI_Chat(self):
        self.main_window.switch_to_AI_Chat()        
    
    def Buy_Products(self):
       self.main_window.switch_to_Buy_Product()
    
    def View_my_Customers(self):
        self.main_window.switch_to_Customers()
        
    def Add_Product(self):
        self.main_window.switch_to_Add_Product()
        
    def View_products_of(self):
        self.main_window.switch_to_View_Product_of_name()
        
    def Start_View_Picture(self):
        self.main_window.switch_to_View_Picture()    
    
    def Search_for_product(self):
        self.main_window.switch_to_Search()
    
    
    def set_username(self, username):
        self.username_label.setText(f"Welcome, {username}")

    def logout(self):
        client.send("Logout".encode())
        client.close()
        QApplication.quit()
        self.main_window.close()

class Add(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Add Product")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        new1 = QPushButton("Add new")
        new1.clicked.connect(self.main_window.switch_to_new)
        layout.addWidget(new1)
        
        new1 = QPushButton("Add old")
        new1.clicked.connect(self.main_window.switch_to_old)
        layout.addWidget(new1)
        self.setLayout(layout)
        
               
class w(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Add Product")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Enter product name")
        layout.addWidget(self.product_name)
        
        self.price = QSpinBox(value=0, maximum=1000000, minimum=0 , singleStep=1, prefix="Price is ")
        layout.addWidget(self.price)
        
        self.description = QLineEdit()
        self.description.setPlaceholderText("Put Description")
        layout.addWidget(self.description)
        
        self.image = QLineEdit()
        self.image.setPlaceholderText("Enter image name")
        layout.addWidget(self.image)
        
        
        
        
        a = QPushButton("Add")
        a.clicked.connect(self.add)
        layout.addWidget(a)
        self.setLayout(layout)
        
    def add(self):
           pm=self.product_name.text()
           p=self.price.value()
           desc=self.description.text()
           im=self.image.text()
           x=False
           try:
               if (im[-5:]== ".jpeg" or im[-4:]==".png" or im[-4:]==".jpg"):
                   with open(im, 'rb') as file:
                       image_data=file.read()
                       file.close()
                       x=True
               else:
                   x=False
                   self.handle_error("Wrong Input")
           except:
                   x=False
                   self.handle_error("No Such Image")
           if(x):
               client.send("Add product".encode())
               
               client.send("new".encode())
               r=client.recv(1024).decode()
               info={"product_name":pm , "price":p , "description":desc , "image":im}
               info=json.dumps(info)
               client.send(info.encode())
               self.image_client(im)
               print(client.recv(1024).decode())
               self.main_window.switch_to_Done()
   
    def image_client(self,image):
        with open(image, 'rb') as file:
            image_data=file.read()
            client.send(image_data)
        file.close()
           
    def handle_error(self, message):
        if (message=="No such image"):
          reply = QMessageBox.question(self,"No such image",
              f"{message}\nWould you like to try agian.",
              QMessageBox.Yes | QMessageBox.No,
          )

          if reply == QMessageBox.No:
              client.send("Nothing".encode())
              self.main_window.switch_to_main_app()
          else:
              QMessageBox.information(self, "Retry", "Please Retry")
        else:
            reply = QMessageBox.question(self,"Wrong input",
                f"{message}\nWould you like to try agian.",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.No:
                client.send("Nothing".encode())
                self.main_window.switch_to_main_app()
            else:
                QMessageBox.information(self, "Retry", "Please Retry")
           
class old(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Add Product")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Enter product name")
        layout.addWidget(self.product_name)
        
        a = QPushButton("Add")
        a.clicked.connect(self.add)
        layout.addWidget(a)
        self.setLayout(layout)
        
    def add(self):
        
        client.send("Add product".encode())
        client.send("Old".encode())
        y=client.recv(1024).decode()
        pm=self.product_name.text()
        
        
        info={"product_name":pm}
        info=json.dumps(info)
        client.send(info.encode())
        r=client.recv(1024).decode()
        if(r=="No such product"):
             self.handle_error(r)
        else:
             self.main_window.switch_to_Done()
    
    
    def handle_error(self,message):
        reply = QMessageBox.question(self,"No such product",
            f"{message}\nWould you like to try agian.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            self.main_window.switch_to_main_app()
        else:
            QMessageBox.information(self, "Retry", "Please Retry")
            d=client.recv(1024).decode()
            self.main_window.switch_to_old()
        
class Done(QWidget):
    def __init__ (self, main_window):
        self.a="Thankyou"
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        title = QLabel(self.a)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        self.button = QPushButton("Done")
        self.button.setGeometry(200, 150, 150, 30)
        font = QFont('Arial', 10) 
        self.button.setFont(font)
        self.button.clicked.connect(self.on_button_click)
        layout.addWidget(self.button)
        self.setLayout(layout)
    
    def on_button_click(self):
        self.main_window.switch_to_main_app()
        
class Buy1(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Buy Product")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        
        
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Enter product name")
        layout.addWidget(self.product_name)
        
        button1 = QPushButton("Buy")
        button1.clicked.connect(self.button_clicked)
        layout.addWidget(button1)
        self.setLayout(layout)

    def button_clicked(self):
        pm=self.product_name.text()
        client.send("Buy product".encode())
        r=client.recv(1024).decode()
        client.send(pm.encode())
        d=client.recv(1024).decode()
        if (d=="No such product"):
            self.main_window.switch_to_Not_Found()
        else:
            self.main_window.switch_to_Found()
                
class Not_found(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Product Not Found!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        button1 = QPushButton("Try agian")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        
        button2 = QPushButton("Exit")
        button2.clicked.connect(self.button2_clicked)
        layout.addWidget(button2)
        self.setLayout(layout)
        
    def button1_clicked(self):
        d=client.recv(1024).decode()
        self.main_window.switch_to_Buy_Product()
    
    def button2_clicked(self):
        self.main_window.switch_to_main_app()

class Found(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window
        d=client.recv(1024).decode()
        d1=json.loads(d)
        self.d1={}
        
        layout = QVBoxLayout()

        title = QLabel("Choose the option you want")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        for key in d1:
            for x in d1[key]:
                layout.addWidget(QLabel(key+ ":" +str(x)))
                
        self.comboBox = QComboBox(editable=False)
        self.comboBox.setGeometry(200, 150, 150, 30)
        font = QFont('Arial', 10) 
        self.comboBox.setFont(font)
        for key in d1:
            self.comboBox.addItem(key)
        layout.addWidget(self.comboBox)
        
        
        button1 = QPushButton("Buy")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        
        button2 = QPushButton("Exit")
        button2.clicked.connect(self.button2_clicked)
        layout.addWidget(button2)
        self.setLayout(layout)
        
    def button1_clicked(self):
        k=self.comboBox.currentText()
        client.send(k.encode())
        r=client.recv(1024).decode()
        self.main_window.switch_to_Would()
    
    def button2_clicked(self):
        client.send("Empty".encode())
        self.main_window.switch_to_main_app()

class Bought(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Thank you for your purchase")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        button1 = QPushButton("Buy another product?")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        
        button2 = QPushButton("Exit")
        button2.clicked.connect(self.button2_clicked)
        layout.addWidget(button2)
        self.setLayout(layout)
        
    def button1_clicked(self):
        d=client.recv(1024).decode()
        self.main_window.switch_to_Buy_Product()
    
    def button2_clicked(self):
        self.main_window.switch_to_main_app()


class Rate(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Please Rate")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        
        layout.addWidget(QLabel("Rate the product from 1 to 10."))
        
        self.rate = QSpinBox(value=0, maximum=10, minimum=0 , singleStep=1)
        layout.addWidget(self.rate)
        
        button1 = QPushButton("Rate")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        self.setLayout(layout)
        
    def button1_clicked(self):
        a=client.recv(1024).decode()
        r=self.rate.value()
        client.send(str(r).encode())
        d=client.recv(1024).decode()
        self.main_window.switch_to_Bought()
    
    def button2_clicked(self):
        self.main_window.switch_to_Bought()

class Would(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Would You like to rate the Product")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        button1 = QPushButton("Yes")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        
        button2 = QPushButton("No")
        button2.clicked.connect(self.button2_clicked)
        layout.addWidget(button2)
        self.setLayout(layout)
        
    def button1_clicked(self):
        client.send("Yes".encode())
        self.main_window.switch_to_Rate()
    
    def button2_clicked(self):
        client.send("No".encode())
        self.main_window.switch_to_Bought()


class Product_of_name(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("View Products of a Specifice User")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        
        self.user_name = QLineEdit()
        self.user_name.setPlaceholderText("Enter the owner username")
        layout.addWidget(self.user_name)
        
        
        button1 = QPushButton("Search")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        
        self.setLayout(layout)
    def button1_clicked(self):
        client.send("View products of".encode())
        r=client.recv(1024).decode()
        u=self.user_name.text()
        client.send(u.encode())
        r1=client.recv(1024).decode()
        client.send("thnx".encode())
        if(r1=="There is no such user"):
            self.main_window.switch_to_No_Username()
        else:
            self.main_window.switch_to_Show()

class Show(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        r=client.recv(1024).decode()
        layout = QVBoxLayout()

        title = QLabel("Products are:")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        if(r=="This user has no products for sale."):
            title2 = QLabel("This user has no products for sale.")
            layout.addWidget(title2)
        else:
            d1=json.loads(r)
            for key in d1:
                layout.addWidget(QLabel(key+ ":" +str(d1[key])))
        
        button1 = QPushButton("Done")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        self.setLayout(layout)
    
    def button1_clicked(self):
        self.main_window.switch_to_main_app()

class No_Username(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("This Username Was Not Found!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        button1 = QPushButton("Try agian")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        
        button2 = QPushButton("Exit")
        button2.clicked.connect(self.button2_clicked)
        layout.addWidget(button2)
        self.setLayout(layout)
        
    def button1_clicked(self):
        d=client.recv(1024).decode()
        self.main_window.switch_to_View_Product_of_name()
    
    def button2_clicked(self):
        self.main_window.switch_to_main_app()


class Customers(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window
        d1=client.recv(1024).decode()
        
        layout = QVBoxLayout()
        if (d1=="You have no products."):
            title = QLabel(d1)
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: bold;")
            layout.addWidget(title)       
        else:
            title = QLabel("Your customers are: ")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: bold;")
            layout.addWidget(title) 
            d=json.loads(d1)
            for key in d:
                if d[key]=="Not bought yet":
                    layout.addWidget(QLabel(key+ ":" +d[key]))
                else:
                    x=d[key]
                    layout.addWidget(QLabel(key+ ":" +str(x)))
                    
        self.button = QPushButton("Done")
        self.button.setGeometry(200, 150, 150, 30)
        font = QFont('Arial', 10) 
        self.button.setFont(font)
        self.button.clicked.connect(self.on_button_click)
        layout.addWidget(self.button)
        self.setLayout(layout)
    
    def on_button_click(self):
        self.main_window.switch_to_main_app()
       
       
class Search(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Search")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        
        
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Enter product name")
        layout.addWidget(self.product_name)
        
        button1 = QPushButton("Search")
        button1.clicked.connect(self.button_clicked)
        layout.addWidget(button1)
        self.setLayout(layout)
    
    def button_clicked(self):
        client.send("Search".encode())
        r=client.recv(1024).decode()
        pm=self.product_name.text()      
        client.send(pm.encode())
        d=client.recv(1024).decode()
        if(d=="No such product"):
            self.main_window.switch_to_No_Product()
        else:
            d1=json.loads(d)
            self.main_window.switch_to_Yes_Prodcut(d1)
        

class No_Product(QWidget):
    def __init__ (self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Product Not Found!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        button1 = QPushButton("Try agian")
        button1.clicked.connect(self.button1_clicked)
        layout.addWidget(button1)
        
        button2 = QPushButton("Exit")
        button2.clicked.connect(self.button2_clicked)
        layout.addWidget(button2)
        self.setLayout(layout)
        
    def button1_clicked(self):
        d=client.recv(1024).decode()
        self.main_window.switch_to_Search()
    
    def button2_clicked(self):
        self.main_window.switch_to_main_app()

class Yes_Product(QWidget):
    def __init__ (self, main_window, d1):
        super().__init__()
        self.main_window = main_window
        
        layout = QVBoxLayout()

        title = QLabel("Result")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)       
        
        for key in d1:
            for x in d1[key]:
                layout.addWidget(QLabel(key+ ":" +str(x)))
                
        
        button1 = QPushButton("Done")
        button1.clicked.connect(self.button2_clicked)
        layout.addWidget(button1)
        self.setLayout(layout)
        
    def button2_clicked(self):
        self.main_window.switch_to_main_app()

class Chat_AI(QWidget):
    def __init__ (self, main_window, Table):
        super().__init__()
        self.main_window = main_window
        self.Table=Table
        
        layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        # User Input
        
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.return_button = QPushButton("Return")
        self.send_button.clicked.connect(self.send_message1)
        self.return_button.clicked.connect(self.Return)
        layout.addWidget(self.user_input)
        layout.addWidget(self.send_button)
        layout.addWidget(self.return_button)

        self.chat_display.append("Chatbot: Welcome to AUB Boutique! How can I help you?")
        self.setLayout(layout)
    
    def send_message1(self):
        print("ok")
        x=self.Table
        system_message = f"""
You are a chatbot for AUB Boutique. Your job is to provide product recommendations and answer questions in a very short and concise manner, always keeping your responses to 1-2 sentences only.

Key instructions:
1. Always recommend specific items from the product list provided in the table below. Do not recommend items outside of this table.
2. When you recommend a product, and the customer asks about something about this specific product avoid referencing or mixing information from other products. 
3. The table of products you must use for all recommendations and answers is as follows:

    {x}
    
4. Include aggregate statistics about the product (e.g., how many people bought it) if available, but do not reveal personal buyer information like names.
5. Be concise and limit your answers to 1-2 sentences, ideally 1 line.
6. Ensure all responses are consistent and relevant to the customer's inquiries, without introducing unrelated information or errors.

Always maintain brevity and clarity while assisting customers with product recommendations and inquiries, and ensure that follow-up questions about recommended products are answered accurately and based on the provided table.
"""


        chat.send_message(system_message)
        user_message = self.user_input.text().strip()
        if not user_message:
            QMessageBox.warning(self, "Empty Input", "Please enter a message.")
            return

        self.chat_display.append(f"You: {user_message}")
        self.user_input.clear()

        try:
            response = chat.send_message(user_message)
            self.chat_display.append(f"Chatbot: {response.text.strip()}")
        except Exception as e:
            self.chat_display.append(f"Chatbot: Sorry, an error occurred: {str(e)}")
    
    def Return(self):
        self.main_window.switch_to_main_app()

class View_Picture(QWidget):
    def __init__(self,main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Please enter the username and name of product")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        layout.addWidget(self.username_input)
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("Enter Product")
        layout.addWidget(self.product_input)
        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.view_picture)
        layout.addWidget(proceed_button)
        self.setLayout(layout)
    def view_picture(self):
        print("nehna hon sorna")
        username = self.username_input.text()
        product=self.product_input.text()
        client.send("View picture of a specific product of a buyer".encode())
        data={"username": username,
        "product": product}
        data=json.dumps(data)
        client.send(data.encode())
        response=client.recv(1024).decode()
        print(response)
        if(response=="Invalid"):
            self.handle_error(response)
        elif response=="Good":
            if response=="Good":
                print("lak heyy")
                size=int(client.recv(1024).decode())
                data=client.recv(size)
                self.main_window.switch_to_View_Picture_2(data)
                #THIS SHOWS THE IMAGE INCASE MA ZABATET NHOTA BEL WINDOW
                
                #image = Image.open(io.BytesIO(data))
                #image.show() 
                #self.main_window.switch_to_main_app()
            
            
    def handle_error(self,message):
          reply = QMessageBox.question(
              self,
              "Error",
              f"{message}\nTry again?",
              QMessageBox.Yes | QMessageBox.No,
          )

          if reply == QMessageBox.Yes:
              k=client.recv(1024).decode()
              QMessageBox.information(self, "Retry", "Please retry")  
          else:
              self.main_window.switch_to_main_app()

class View_Picture2(QWidget):
    def __init__(self, main_window, data):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        # Save the image data
        temp_image_path = r"test_image.png"
        with open(temp_image_path, "wb") as f:
            f.write(data)
        label = QLabel(self)
         
        # loading image
        pixmap = QPixmap(temp_image_path)
        label.setPixmap(pixmap)
        layout.addWidget(label)
        # Add Return button
        self.return_button = QPushButton("Return")
        self.return_button.clicked.connect(self.Return2)
        layout.addWidget(self.return_button)

        self.setLayout(layout)

    def Return2(self):
        self.main_window.switch_to_main_app()


# Main application window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AUB Boutique ")
        self.setGeometry(200, 200, 600, 300)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.initial_screen = FirstScreen(self)
        self.signup_form = Signup(self)
        self.login_form = Login(self)
        self.main_app_screen=MainAppScreen(self)
        self.stacked_widget.addWidget(self.main_app_screen)
        
        
        
        
        self.Add_Product_form=Add(self)
        self.old_form=old(self)
        self.w_form=w(self)
        self.do_form=Done(self)
        
        
        
        self.Buy1_form=Buy1(self)
        self.Not_found_form=Not_found(self)
        self.Bought_form=Bought(self)
        
        
        self.Product_of_name_form=Product_of_name(self)
        self.No_Username_form=No_Username(self)
        
        self.Would_form=Would(self)
        self.Rate_form=Rate(self)
        
        self.Search_form=Search(self)
        self.No_Product_form=No_Product(self)
        
        self.View_Picture_form=View_Picture(self)
        
        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.signup_form)
        self.stacked_widget.addWidget(self.login_form)
        self.stacked_widget.addWidget(self.Add_Product_form)
        self.stacked_widget.addWidget(self.w_form)
        self.stacked_widget.addWidget(self.old_form)
        self.stacked_widget.addWidget(self.do_form)
        self.stacked_widget.addWidget(self.Buy1_form)
        self.stacked_widget.addWidget(self.Not_found_form)
        
        self.stacked_widget.addWidget(self.Bought_form)
        self.stacked_widget.addWidget(self.Product_of_name_form)
        self.stacked_widget.addWidget(self.No_Username_form)
        self.stacked_widget.addWidget(self.Rate_form)
        self.stacked_widget.addWidget(self.Would_form)
        self.stacked_widget.addWidget(self.Search_form)
        self.stacked_widget.addWidget(self.No_Product_form)
        self.stacked_widget.addWidget(self.View_Picture_form)
        self.stacked_widget.setCurrentWidget(self.initial_screen)
        

    def switch_to_login(self):
        self.stacked_widget.setCurrentWidget(self.login_form)

    def switch_to_signup(self):
        self.stacked_widget.setCurrentWidget(self.signup_form)
    
    
    #Add product
    def switch_to_Add_Product(self):
        self.stacked_widget.setCurrentWidget(self.Add_Product_form)
    def switch_to_new(self):
        self.stacked_widget.setCurrentWidget(self.w_form)
    def switch_to_old(self):
        self.stacked_widget.setCurrentWidget(self.old_form)    
        
    
    
    #Buy product
    def switch_to_Buy_Product(self):
        self.stacked_widget.setCurrentWidget(self.Buy1_form)
    def switch_to_Not_Found(self):
        self.stacked_widget.setCurrentWidget(self.Not_found_form)
    def switch_to_Found(self):
        Found_form=Found(self)
        self.stacked_widget.addWidget(Found_form)
        self.stacked_widget.setCurrentWidget(Found_form)
    def switch_to_Bought(self):
        self.stacked_widget.setCurrentWidget(self.Bought_form)
    def switch_to_Rate(self):
        self.stacked_widget.setCurrentWidget(self.Rate_form)
    def switch_to_Would(self):
        self.stacked_widget.setCurrentWidget(self.Would_form)
    
    
    
    #View product of
    def switch_to_View_Product_of_name(self):
        self.stacked_widget.setCurrentWidget(self.Product_of_name_form)
    def switch_to_No_Username(self):
        self.stacked_widget.setCurrentWidget(self.No_Username_form)
    def switch_to_Show(self):
        Show_form=Show(self)
        self.stacked_widget.addWidget(Show_form)
        self.stacked_widget.setCurrentWidget(Show_form)
    
    
    #Search
    def switch_to_Search(self):
        self.stacked_widget.setCurrentWidget(self.Search_form)
    def switch_to_No_Product(self):
        self.stacked_widget.setCurrentWidget(self.No_Product_form)
    def switch_to_Yes_Prodcut(self,d1):
        Yes_Product_form=Yes_Product(self,d1)
        self.stacked_widget.addWidget(Yes_Product_form)
        self.stacked_widget.setCurrentWidget(Yes_Product_form)
    
    
    #Customers
    def switch_to_Customers(self):
        client.send("View my customers".encode())
        Customers_form=Customers(self)
        self.stacked_widget.addWidget(Customers_form)
        self.stacked_widget.setCurrentWidget(Customers_form)
        
    
    
    
    def switch_to_Done(self):
        self.stacked_widget.setCurrentWidget(self.do_form)
    
    def switch_to_main_app(self):
        self.stacked_widget.removeWidget(self.main_app_screen)
        self.main_app_screen=MainAppScreen(self)
        self.stacked_widget.addWidget(self.main_app_screen)
        self.stacked_widget.setCurrentWidget(self.main_app_screen)
         
         
         #self.stacked_widget.addWidget(main_app1_screen)
         #self.stacked_widget.setCurrentWidget(main_app2_screen)

    def switch_to_initial(self):
        self.stacked_widget.setCurrentWidget(self.initial_screen)
    #Chat Bot
    def switch_to_AI_Chat(self):
        client.send("Chat with AI".encode())
        Table=client.recv(10000).decode()
        print(Table)
        client.send("Thanks".encode())
        Chat_AI_form=Chat_AI(self,Table)
        self.stacked_widget.addWidget(Chat_AI_form)
        self.stacked_widget.setCurrentWidget(Chat_AI_form)
    
    def switch_to_View_Picture(self):
        self.stacked_widget.setCurrentWidget(self.View_Picture_form)
    def switch_to_View_Picture_2(self,data):
        View_Picture_2_form=View_Picture2(self,data)
        self.stacked_widget.addWidget(View_Picture_2_form)
        self.stacked_widget.setCurrentWidget(View_Picture_2_form)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
