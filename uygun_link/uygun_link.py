from flask import Flask, render_template,request,flash
import requests
from bs4 import BeautifulSoup
import smtplib
import time
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "**"       # Your secret key

app.config["MYSQL_HOST"] = "localhost"           # Your databases informations
app.config["MYSQL_USER"] = "root"  
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = ""

mysql = MySQL(app)

@app.route("/")
def entry_page():
    return render_template("einstein.html",page_title="Uygun Link")



@app.route("/info",methods = ["POST","GET"])  

def info():

    if request.method == "POST":
        link = request.form["link"]
        user_price = int(request.form["fiyat"])
        user_mail = request.form["reciever"]

        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(link,reciever,fiyat) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(link,user_mail,user_price))
        mysql.connection.commit()
        cursor.close

    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"}



    def check_price():   
        page = requests.get(link,headers=headers)
        soup = BeautifulSoup(page.content,"html.parser")
        global title
        title = soup.find(id="product-name").get_text().strip()
        title = title[0:18]
        print(title)
        span = soup.find(id = "offering-price")
        content = span.attrs.get("content")
        price = float(content)
        print(price)

        if(price < user_price):
            send_mail(title)
        
    def send_mail(title):                                
        sender = "your gmail"   # You should give your gmail informations here
        try:
            server = smtplib.SMTP("smtp.gmail.com",587)     
            server.ehlo()
            server.starttls()
            server.login(sender,"your password")    # and here

            subject = title + " istedigin fiyata dustu!"
            body = """
            Istedigin Urunun Fiyati Dustu 
            Simdi bu linkten urunu satin alabilirsin ==> """ + link
            mailContent = f"To:{user_mail}\nFrom:{sender}\nSubject:{subject}\n\n{body}"
            server.sendmail(sender,user_mail,mailContent)
            print("Mail Basariyla Gonderildi")
        except smtplib.SMTPException as e:
            print(e)
        finally:
            server.quit()

    while(1):                           
        check_price()
        time.sleep(1)
        break  
    
    

    return render_template("result.html",page_title = "Sonuç Ekranı",result = "Bizi Seçtiğiniz İçin Teşekkürler!",urun_linki = link, urun_fiyat = user_price,mail_adresi = user_mail)  
  
app.run()



