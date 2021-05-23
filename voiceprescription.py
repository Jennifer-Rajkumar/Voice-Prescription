# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, render_template, request
import speech_recognition as sr
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask_mongoengine import MongoEngine
import fitz,os
import pymongo

app=Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'Prescriptions',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

a=""
b=""
c=""
aadharid=""
name=""
age=""
address=""
email=""
date=""
newFilename=""
oldPatient=False
medicines=[]
x=[]
y=[]
z=[]

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Prescriptions"]
mycol = mydb["drugs"]

@app.route("/")
def home():
    global email,newFilename
    email=""
    newFilename=""
    return render_template("home.html")

@app.route("/prescribe")
def prescribe():
    return render_template("prescription.html")

class User(db.Document):
    aadharid=db.StringField()
    name= db.StringField()
    age=db.StringField()
    address=db.StringField()
    email =db.StringField()
    pdfs=db.ListField()
    def to_json(self):
        return {"aadharid": self.aadharid,
                "name": self.name,
                "age": self.age,
                "address": self.address,
                "email": self.email,
                "pdfs": self.pdfs}
    
class Drugs(db.Document):
    name=db.StringField()
    medicine=db.ListField()

@app.route("/history")
def history():
    return render_template("history.html")
    
@app.route("/search", methods=['POST','GET'])
def search():
    try:
        user=User.objects(aadharid=request.form['aadharid']).get_or_404()
        return render_template("history.html",pdfs=user.pdfs,error=False)
    except:
        print("not found")
    return render_template("history.html",error=True)

@app.route("/check", methods=['POST'])
def check():
    global name,date,age,address,email,aadharid,oldPatient,a,b,c,medicines
    try:
        user=User.objects(aadharid=request.form['aadharid']).get_or_404()
        oldPatient=True
        aadharid=user.aadharid
        name=user.name
        age=user.age
        address=user.address
        email=user.email
    except:
        aadharid=request.form['aadharid']
        a=""
        b=""
        c=""
        aadharid=""
        name=""
        age=""
        address=""
        email=""
        date=""
        newFilename=""
        oldPatient=False
        medicines=[]
        print("not found")
    return render_template("prescription.html",disease=a,medicine=b,dosage=c,name=name,age=age,address=address,date=date,email=email,aadharid=aadharid)

@app.route("/confirmDetails", methods=['POST'])
def confirmDetails():
    global name,date,age,address,email,aadharid
    aadharid=request.form['aadharid']
    name=request.form['name']
    age=request.form['age']
    address=request.form['address']
    email=request.form['email']
    date=request.form['date']
    a=""
    b=""
    c=""
    return render_template("prescription.html",disease=a,medicine=b,dosage=c,name=name,age=age,address=address,date=date,email=email,aadharid=aadharid)

@app.route("/disease")
def record1():
    global a,b,c
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("Say")
        audio=r.listen(source)
    b=""
    c=""
    try:
        listofwords=(r.recognize_google(audio)).split()
        a=" ".join(listofwords)
        print(listofwords)
    except:
        print("Couldn't recognize")
        a="record again!"
    return render_template("prescription.html",disease=a,medicine=b,dosage=c,name=name,age=age,address=address,date=date,email=email,aadharid=aadharid)

@app.route("/medicine")
def record2():
    global a,b,c
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("Say")
        audio=r.listen(source)
    c=""
    try:
        listofwords=(r.recognize_google(audio)).split()
        b=" ".join(listofwords)
        print(listofwords)
    except:
        print("Couldn't recognize")
        b="record again!"
    return render_template("prescription.html",medicine=b,disease=a,dosage=c,name=name,age=age,address=address,date=date,email=email,aadharid=aadharid)

@app.route("/dosage")
def record3():
    global a,b,c
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("Say")
        audio=r.listen(source)
    try:
        listofwords=(r.recognize_google(audio)).split()
        c=" ".join(listofwords)
        print(listofwords)
    except:
        print("Couldn't recognize")
        c="record again!"
    return render_template("prescription.html",dosage=c,disease=a,medicine=b,name=name,age=age,address=address,date=date,email=email,aadharid=aadharid)

@app.route("/recommend", methods=['POST'])
def recommend():
    global medicines, a
    medicines=[]
    dis=request.form['disease'].lower()
    a=dis
    print(Drugs.objects)

    for obj in Drugs.objects(name=dis):
        medicines=obj.medicine
    print(medicines)
    b=""
    c=""
    return render_template("prescription.html",meds=medicines,dosage=c,disease=a,medicine=b,name=name,age=age,address=address,date=date,email=email,aadharid=aadharid)

@app.route("/add", methods=['POST','GET'])
def add():
    global medicines
    medicines=[]
    x.append(request.form['disease'])
    y.append(request.form['medicine'])
    z.append(request.form['dosage'])
    for obj in Drugs.objects(name=x[len(x)-1]):
        medicines=obj.medicine
    if len(medicines)==0:
        mycol.insert_one({"name":x[len(x)-1],"medicine":[y[len(y)-1]]})
    else:
        if y[len(y)-1] not in medicines:
            drugs=Drugs.objects(name=a).get_or_404()
            l=drugs.medicine
            l.append(y[len(y)-1])
            drugs.medicine=l
            drugs.save()
    return render_template('prescription.html',name=name,age=age,address=address,date=date,email=email,aadharid=aadharid,error=True)

@app.route("/assignMed/<med>")
def assignMed(med):
    global b
    b=request.view_args['med']
    c=""
    return render_template("prescription.html",meds=medicines,dosage=c,disease=a,medicine=b,name=name,age=age,address=address,date=date,email=email,aadharid=aadharid)


@app.route("/createPDF", methods=['POST'])
def createPDF():
    global oldPatient,newFilename,name,date,age,address,email,aadharid,medicines
    pdf=FPDF()
    pdf.add_page()
    pdf.set_font("Arial",size=24)
    pdf.set_text_color(0,128,128)
    pdf.cell(200,20,txt="JenGold Hospital", ln=1,align="C")
    pdf.set_text_color(0,0,0)
    pdf.set_font("Arial",size=12)
    pdf.cell(100,10,txt="Dr. Name Degree",ln=0,align="L")
    pdf.cell(100,10,txt="Phone Number: 123456789     ",ln=1,align="R")
    pdf.cell(100,10,txt="Address: 20,ABC Street,Chennai", ln=0,align="L")
    pdf.cell(100,10,txt="Mail ID: jengoldhospital@gmail.com     ",ln=1,align="R")
    pdf.line(0, 55, 250, 55)
    pdf.set_font("Arial",size=14)
    pdf.cell(200,10,txt="",ln=1)
    pdf.cell(65,10,txt="Date: "+date,ln=0,align="L")
    pdf.cell(65,10,txt="Name: "+name,ln=0,align="C")
    pdf.cell(65,10,txt="Age: "+age, ln=1,align="R")
    pdf.cell(200,10,txt="",ln=1)
    for i in range(0,len(x)):
        pdf.cell(65,10,txt=x[i], ln=0,align="L")
        pdf.cell(65,10,txt=y[i], ln=0,align="C")
        pdf.cell(65,10,txt=z[i], ln=1,align="R")

    if not oldPatient:
        pdfs=[name+" "+date]
        user = User(aadharid=aadharid,name=name,age=age,address=address,email=email,pdfs=pdfs)
        user.save()
    else:
        user=User.objects(aadharid=aadharid).get_or_404()
        l=user.pdfs
        l.append(name+" "+date)
        user.pdfs=l
        user.save()
    newFilename=name+" "+date
    pdf.output(newFilename+"1.pdf")
    input_file = newFilename+"1.pdf"
    output_file = newFilename+".pdf"
    img_file = request.form['signimage']
    
    image_rectangle = fitz.Rect(450,720,550,820)
    
    file_handle = fitz.open(input_file)
    first_page = file_handle[0]
    
    first_page.insertImage(image_rectangle, filename=img_file)
    
    file_handle.save(output_file)  
    file_handle.close()
    os.remove(newFilename+"1.pdf")
    
    a=""
    b=""
    c=""
    name=""
    date=""
    address=""
    age=""
    aadharid=""
    medicines=[]
    oldPatient=False
    return render_template("preview.html",filename=newFilename)

@app.route("/sendPDF")
def sendPDF():
    global newFilename
    email_user = 'jenn18cs030@rmkcet.ac.in'
    email_password = '04.07.2000' 
    email_send = email
    
    
    subject = 'Prescription'+'-'+newFilename
    
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject
    
    body = 'Hi there, sending this email from JenGold Hospital'
    msg.attach(MIMEText(body,'plain'))
    
    attachment =open('%s.pdf' %newFilename,'rb')
    
    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+newFilename+".pdf")
    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user,email_password)
    
    
    server.sendmail(email_user,email_send,text)
    server.quit()
    return render_template("preview.html")

if __name__ == '__main__':
    app.run()

