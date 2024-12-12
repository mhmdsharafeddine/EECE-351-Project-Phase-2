import base64
from socket import *
import ssl
import requests
import threading
import sqlite3
import json
import datetime
import random
import os
import sys
from PyQt5.QtWidgets import QApplication, QSpinBox, QTextEdit, QScrollArea, QTableWidgetItem, QFileDialog, QTableWidget, QMessageBox, QComboBox, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton
import PyQt5.QtGui as qtg
clients = {}

def handle_client(client,addr,rcv):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    #cursor.execute("CREATE TABLE Customers(customerUsername TEXT UNIQUE, customerMail TEXT UNIQUE, customerPassword text, customerName text, currency text)")
    #cursor.execute("CREATE TABLE Products(owner_name text, product_name text, price real, decription text, image text, quantity int, buyer text, sum text, number text)")
    #db.commit()
    
    try:
        client.send("No".encode())
        message=client.recv(1024).decode()
        while(message=="Register" or message=="Login"):
                print(f"Recieved this message: {message}")
                if(message=="Register"):
                    username=register(client)
                    print(username)
                    message="stop"
                    clients[username] = rcv
                    if username!=None:
                            view_products(username,client)
                            while True:
                                message=client.recv(1024).decode()
                                print("this is message :",message)
                                if message:
                                    if message=="Add product":
                                        add_product(client,username)
                                        print("Done adding")
                                    elif message== "Remove product":
                                        remove_product(client,username)
                                    elif message=="View products of":
                                        product_of(username,client)
                                        print("Done VPF")
                                    elif message=="View my customers":
                                        my_Customers(username,client)
                                        print("Done VMC")
                                    elif message=="Buy product":
                                        buy_product(username,client)
                                        print("Done Buying")
                                    elif message=="View picture of a specific product of a buyer":
                                        picture(client)
                                    elif message == "Chat":
                                        print(f"[NEW CONNECTION] {addr}: {username} connected.")
                                        sendusers()
                                    elif message == "getip":
                                        ipsender()
                                    elif message=="Search":
                                        Search(username,client)
                                        print("Done Searching")
                                    elif message=="Logout":
                                         break
                                    elif message=="refresh":
                                         view_products(username,client)
                                         print("refreshed")
                                    elif message=="Chat with AI":
                                        ChatWithAI(client)
                                    if message!="refresh":
                                        view_products(username,client)
                                        print("Done")
                elif(message=="Login"):
                    username=login(client)
                    print(username)
                    message="stop"
                    clients[username] = rcv
                    if username!=None:
                            view_products(username,client)
                            while True:
                                message=client.recv(1024).decode()
                                print("this is message :",message)
                                if message:
                                    if message=="Add product":
                                        add_product(client,username)
                                        print("Done adding")
                                    elif message== "Remove product":
                                        remove_product(client,username)
                                    elif message=="View products of":
                                        product_of(username,client)
                                        print("Done VPF")
                                    elif message=="View my customers":
                                        my_Customers(username,client)
                                        print("Done VMC")
                                    elif message=="Buy product":
                                        buy_product(username,client)
                                        print("Done Buying")
                                    elif message=="View picture of a specific product of a buyer":
                                        picture(client)
                                    elif message == "Chat":
                                        print(f"[NEW CONNECTION] {addr}: {username} connected.")
                                        sendusers()
                                    elif message == "getip":
                                        ipsender()
                                    elif message=="Search":
                                        Search(username,client)
                                        print("Done Searching")
                                    elif message=="Logout":
                                         client.close()
                                         break
                                    elif message=="refresh":
                                         view_products(username,client)
                                         print("refreshed")
                                    elif message=="Chat with AI":
                                        ChatWithAI(client)
                                    if message!="refresh":
                                        view_products(username,client)
                                        print("Done")
                if username == None:
                    message=client.recv(1024).decode()
                
    except Exception as e:
        print(f"Error:{e}")

    finally:

        try:
            if username in clients:
                del clients[username]
            client.close()
            print(f"[DISCONNECTED] {addr} ({username})")
        except Exception as e:
            print(f"Error during cleanup: {e}")



def picture(client):
   with sqlite3.connect('Customers.db') as db:
    cursor=db.cursor()
    info=client.recv(1024).decode()
    info=json.loads(info)
    username=info["username"]
    product=info["product"]
    cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\" and product_name=\"{product}\"")
    x=cursor.fetchone()
    if(x==None):
        client.send("Invalid".encode())
    else:
        client.send("Good".encode())
        cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\" and product_name=\"{product}\"") 
        image=cursor.fetchone()[4]
        print(image)
        file=open(image,"rb")
        data=file.read()
        size=os.stat(image).st_size
        client.send(str(size).encode())
        client.send(data)
        file.close()

def register(client):
    with sqlite3.connect('Customers.db') as db:
        cursor=db.cursor()
        client.send("Ready to register".encode())
        info=client.recv(1024).decode('utf-8')
        info=json.loads(info)
        name=info['name']
        username=info['username']
        email=info["email"]
        password=info["password"]
        currency=info["currency"]
        currency=currency[0:4]
        try:
            cursor.execute("INSERT INTO Customers values(?,?,?,?,?)", (username,email,password,name,currency))
            client.send("Registration complete".encode())
            cursor.execute(f"SELECT * FROM Customers WHERE customerMail = \"{email}\"")
            return (cursor.fetchone()[0])
        except sqlite3.IntegrityError:
            client.send("Either email or username exists".encode())
            return None


##WORK ON LOGIN
def login(client):
    with sqlite3.connect('Customers.db') as db:
        cursor=db.cursor()
        client.send("Ready to login".encode())
        info=client.recv(1024).decode()
        info=json.loads(info)
        username=info["username"]
        password=info["password"]
        cursor.execute("SELECT * FROM Customers WHERE customerUsername = ? AND customerPassword = ?", (username, password))
        found=cursor.fetchone()
        if found:
            client.send("Login complete".encode())
            cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
            return (cursor.fetchone()[0])
        else:
            client.send("Error".encode())
            return None



def add_product(client,username):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    r=client.recv(1024).decode()
    print(r)
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    curr=cursor.fetchone()[4]
    client.send("yey".encode())
    if (r=="Old"):
        info=client.recv(1024).decode()
        info=json.loads(info)
        product_name1=info["product_name"]
        cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\" and product_name = \"{product_name1}\"")
        x=cursor.fetchone()
        if (x!=None):
            q=x[5]+1
            cursor.execute(f"UPDATE Products SET quantity=\"{q}\" WHERE owner_name = \"{username}\" and product_name=\"{product_name1}\"")
            db.commit()
            client.send("Quantity was increased successfully".encode())
        else:
            client.send("No such product".encode())
    else:
        info=client.recv(1024).decode()
        info=json.loads(info)
        product_name1=info["product_name"]
        price1=info["price"]
        if(curr!="USD"):
            price2=convert(curr,"USD",float(price1))
            print(price2)
        description=info["description"]
        image=info["image"]
        cursor.execute("INSERT INTO Products values(?,?,?,?,?,?,?,?,?)", (username,product_name1,price2,description,"server_"+image,1,"Not bought yet",0,0))
        db.commit()
        image_server(client,image)
        client.send("Done image transfer".encode())

def image_server(client,image):
    file=open("server_"+image,'wb')
    image_data=client.recv(8000000)
    file.write(image_data)
    file.close()


def view_products(username,client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    curr=cursor.fetchone()[4]
    cursor.execute(f"SELECT * FROM Products WHERE quantity > 0")
    x=cursor.fetchone()
    if (x!=None):
        D={}
        i=0
        if(int(x[8])==0):
            z=0
        else:
            z=float(x[7])/int(x[8])
        if(curr!="USD"):
            p=convert("USD",curr,float(x[2]))
        else:
            p=x[2]
        D["1"]=[(x[0],x[1],p,x[3],x[5],str(z))]
        i=1;
        while True:
            try:
                x=cursor.fetchone()
                i+=1
                if(int(x[8])==0):
                    z=0
                else:
                    z=float(x[7])/int(x[8])
                if(curr!="USD"):
                    p=convert("USD",curr,float(x[2]))
                else:
                    p=x[2]
                D[str(i)]=[(x[0],x[1],p,x[3],x[5],str(z))]
            except:
                break
        if(D=={}):
            return client.send("No products on server".encode())
        d1=json.dumps(D)
        client.send(d1.encode())
        
    else:
        client.send("No products on server".encode())
        
        
def view_certain_product(username,name):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    curr=cursor.fetchone()[4]
    cursor.execute(f"SELECT * FROM Products WHERE  product_name = \"{name}\" and quantity > 0")
    x=cursor.fetchone()
    if (x!=None):
        D={}
        i=0
        if(x[0]!=username):
            if(x[0]!=username):
                i+=1
                if(int(x[8])==0):
                    z=0
                else:
                    z=float(x[7])/int(x[8])
            if(curr!="USD"):
                p=convert("USD",curr,float(x[2]))
            else:
                p=x[2]
            D["1"]=[(x[0],x[1],p,x[3],x[5],str(z))]
            i=1;
        while True:
            try:
                x=cursor.fetchone()
                if(x[0]!=username):
                    i+=1
                    if(int(x[8])==0):
                        z=0
                    else:
                        z=float(x[7])/int(x[8])
                    if(curr!="USD"):
                        p=convert("USD",curr,float(x[2]))
                    else:
                        p=x[2]
                    D[str(i)]=[(x[0],x[1],p,x[3],x[5],str(z))]
            except:
                break
        if(D=={}):
            return "No such product"
        d1=json.dumps(D)
        return d1
        
    else:
        return "No such product"

def buy_product(username,client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    emaill=cursor.fetchone()[1]
    client.send("yey".encode())
    print("yey")
    name=client.recv(1024).decode()
    d1=view_certain_product(username,name)
    client.send(d1.encode())
    if(d1!="No such product"):
        client.send(d1.encode())
        choice=client.recv(1024).decode()
        if(choice!="Empty"):
            d1=json.loads(d1)
            q=d1[choice][0][4]-1
            n=d1[choice][0][0]
            
            cursor.execute(f"SELECT * FROM Products WHERE  owner_name = \"{n}\" and product_name=\"{name}\"")
            b=cursor.fetchone()[6]
            if (b=="Not bought yet"):
                b1=[username]
                b2=json.dumps(b1)
                
            else:
                b1=json.loads(b)
                if username not in b1:
                    b1.append(username)
                b2=json.dumps(b1)
            
            cursor.execute("UPDATE Products SET quantity = ?, buyer = ? WHERE owner_name = ? AND product_name = ?",(q, b2, n, name))
            db.commit()
            #email(emaill)
            client.send("Rate".encode())
            if(client.recv(1024).decode()=="Yes"):
                client.send("a".encode())
                r=client.recv(1024).decode()
                cursor.execute(f"SELECT * FROM Products WHERE  owner_name = \"{n}\" and product_name=\"{name}\"")
                x=cursor.fetchone()
                r1=float(r)+float(x[7])
                s1=1+int(x[8])
                r1=str(r1)
                s1=str(s1)
                cursor.execute(f"UPDATE Products SET sum=\"{r1}\", number=\"{s1}\" WHERE owner_name = \"{n}\" and product_name=\"{name}\"")
                db.commit()
                print("done")
                client.send("done".encode())


def product_of(username,client):
    client.send("recieved".encode())
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    us=client.recv(1024).decode()
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    curr=cursor.fetchone()[4]
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{us}\"")
    x=cursor.fetchone()
    if (x!=None):
        cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{us}\"")
        x=cursor.fetchone()
        if (x!=None):
            D={}
            if(int(x[8])==0):
                z=0
            else:
                
                z=float(x[7])/int(x[8])
            if(curr!="USD"):
                p=convert("USD",curr,float(x[2]))
            else:
                p=x[2]
            D[x[1]]=(p,x[3],x[5],str(z))
            
            while True:
                try:
                    u=cursor.fetchone()
                    if(int(u[8])==0):
                        z=0
                    else:
                        z=float(u[7])/int(u[8])
                    if(curr!="USD"):
                        p=convert("USD",curr,float(u[2]))
                    else:
                        p=x[2]
                    D[u[1]]=(p,u[3],u[5],str(z))
                except:
                    break
            d1=json.dumps(D)
            client.send(d1.encode())
            r=client.recv(1024).decode()
            print(r+"1")
            client.send(d1.encode())
        else:
            client.send("This user has no products for sale.".encode())
            r=client.recv(1024).decode()
            print(r+"2")
            client.send("This user has no products for sale.".encode())
    else:
        client.send("There is no such user".encode())
        r=client.recv(1024).decode()
        print(r+"3")


def Search(username,client):
    client.send("Ready".encode())
    name=client.recv(1024).decode()
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    curr=cursor.fetchone()[4]
    cursor.execute(f"SELECT * FROM Products WHERE  product_name = \"{name}\"")
    x=cursor.fetchone()
    i=0
    D={}
    while x!=None:
        try:
            if(int(x[8])==0):
                z=0
            else:
                z=float(x[7])/int(x[8])
            if(curr!="USD"):
                p=convert("USD",curr,float(x[2]))
            else:
                p=x[2]
            D[str(i)]=[(x[0],x[1],p,x[3],x[5],str(z))]
            i+=1
            x=cursor.fetchone()
        except:
            break
    if(D=={}):
        client.send("No such product".encode())
    else:
        d1=json.dumps(D)
        client.send(d1.encode())    
    

def ChatWithAI(client):
    with sqlite3.connect('Customers.db') as db:
        cursor=db.cursor()
        table_name="Products"
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        database_content = {}
        column_names = [description[0] for description in cursor.description]
        database_content[table_name] = [dict(zip(column_names, row)) for row in rows]
        database_string = json.dumps(database_content, indent=4)
        client.send(database_string.encode())
        client.recv(1024).decode()
        print("DATA BASE SENT")



def my_Customers(username,client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\"")
    x=cursor.fetchone()
    
    if (x!=None):
        cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\"")
        D={}
        while True:
            try:
                u=cursor.fetchone()
                if(u[6]=="Not bought yet"):
                    D[u[1]]=u[6]
                else:
                    D[u[1]]=json.loads(u[6])
            except:
                break
        d1=json.dumps(D)
        client.send(d1.encode())
    else:
        client.send("You have no products.".encode())



def convert(changeThisCurrency,toThisCurrency,amount):
    url = "https://api.currencybeacon.com/v1/convert"
    params = {"from": changeThisCurrency,"to": toThisCurrency,"amount": amount}
    api_key = "AezCTetI6q1BPBESpSzHZzX0hkZ6mUC0"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["response"]["value"]
    else:
        print("Error:", response.status_code, response.text)





def ipsender():
    t = json.dumps(clients[client.recv(1024).decode()]).encode()
    print("this is  t ",t)
    client.send(t)
    print(t)

def sendusers():
    global clients
    client.send(json.dumps(list(clients.keys())).encode())




port=int(input("Please enter a Port Number: "))
server=socket(AF_INET,SOCK_STREAM)
server.bind(("127.0.0.1",port))
server.listen(5)
print("Server started listening...")
while True:
    client,addr=server.accept()
    #chatsocket,address = server.accept()

    rcv  = json.loads(client.recv(1024).decode())
    print(f"Accepted connection from {addr}")
    client_thread=threading.Thread(target=handle_client,args=(client,addr,rcv))
    client_thread.start()

server.close()