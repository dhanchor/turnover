# -*-coding:utf-8 -*-
from flask import Flask,render_template,request,session,redirect,url_for
from flask_login import LoginManager,login_required,login_user,UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
import json
import mysql.connector
import datetime
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin):
    #def __init__(self,username,password):
    #    self.username=username
    #    self.passowrd=password
    
    def is_authenticated(self):
        return True
    
    def is_actice(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return '1'

@login_manager.user_loader
def load_user(user_id):
    user=User()
    return user

@app.route('/',methods=['GET', 'POST'])
@login_required
def index():
    #dept = session.get('emp_dept')
    dept=session.get('dept_sn')
    user_name = session.get('emp_name')
    return render_template('index.html',dept=dept,user_name=user_name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    user1=request.values.get('user')
    password=request.values.get('password')
    if user1:
        mydb=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
        mycur=mydb.cursor(dictionary=True)
        query_emp='select a.emp_sn,a.name,a.password,b.name as dept_name,b.dept_sn \
                  from dic_user a inner join dic_dept b \
                  where a.emp_dept_sn=b.dept_sn and a.emp_sn=%s'
        mycur.execute(query_emp%user1)
        emp_result=mycur.fetchone()
        if emp_result is not None:
            emp_sn=emp_result['emp_sn']
            emp_name=emp_result['name']
            hashpw=emp_result['password']
            emp_dept=emp_result['dept_name']
            dept_sn=emp_result['dept_sn']
            if check_password_hash(hashpw,password):
                session['emp_dept'] = emp_dept
                session['dept_sn'] = dept_sn
                session['emp_name'] = emp_name
                session['emp_sn']=emp_sn
                user=User()
                login_user(user)
                #redirect(url_for('index'))
                return '1'
            else:
                return '0'
        else:
            return '0'
    return render_template('login.html')
  
@app.route('/zy_shift_turnover',methods=['GET', 'POST'])
@login_required
def zy_shift_turnover():
    #dept = session.get('emp_dept')
    #user_name = session.get('emp_name')
    mydb=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
    get_turnover_id_cur=mydb.cursor(dictionary=True)
    query_turnover_id='select shift_id as id,shift_id as text,shift_id as url from zy_shift_turnover'
    get_turnover_id_cur.execute(query_turnover_id)
    a=get_turnover_id_cur.fetchall()
    turnover_id_json=json.dumps([{'id': i['id'], 'text': i['text'],'url':i['url']} for i in a], indent=4)
    return turnover_id_json

@app.route('/turnover/<id>',methods=['GET','POST'])
@login_required
def turnover(id):
    session['shift_id'] = id
    return render_template('turnover.html',id=id)

@app.route('/get_patient_list',methods=['GET','POST'])
@login_required
def get_patient_list():
    #user_sn = session.get('emp_sn')
    shift_id= session.get('shift_id')
    get_patient_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
    get_patient_cur=get_patient_db.cursor(dictionary=True,buffered=True)
    get_patient_total_cur=get_patient_db.cursor(dictionary=True,buffered=True)
    page=request.values.get('page')
    rows=request.values.get('rows')
    offset=int(rows)*(int(page)-1)
    query='select a.patient_id,a.bed_no,a.name,a.sex,a.age,a.inpatient_no,a.admiss_diag_str,a.shift_content,\
          a.focus,b.shift_emp_sn,b.succession_emp_sn \
          from patient_list a inner join zy_shift_turnover b \
          where a.shift_id=b.shift_id and a.shift_id=%s limit %s,%s'
    get_patient_cur.execute(query,(shift_id,offset,int(rows)))
    get_patient_total_cur.execute('select count(*) as record_count from patient_list a inner join zy_shift_turnover b where a.shift_id=b.shift_id and a.shift_id=%s'%shift_id)  
    patient_list_result=get_patient_cur.fetchall() 
    patient_list_total=get_patient_total_cur.fetchall()
    for a in patient_list_total:
        total=a['record_count']
    patient_list_json = json.dumps({'total':total,'rows':[{'patient_id':i['patient_id'],'bed_no':i['bed_no'],'name':i['name'],'sex':i['sex'],'age':i['age'],'inpatient_no':i['inpatient_no'],\
                                                       'admiss_diag_str':i['admiss_diag_str'],'shift_content':i['shift_content'],'focus':i['focus']} for i in patient_list_result]},indent=4)
    get_patient_cur.close()
    get_patient_total_cur.close()
    get_patient_db.close()
    return patient_list_json

@app.route('/creat_shift_id',methods=['GET','POST'])
@login_required
def creat_shift_id():
    #user1=request.values.get('user')
    emp_sn = session.get('emp_sn')
    dept = session.get('emp_dept')
    user_name = session.get('emp_name')
    create_shift_id_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
    create_shift_id_cur=create_shift_id_db.cursor(dictionary=True,)
    now_time=datetime.datetime.now()
    shift_date=datetime.datetime.strftime(now_time,'%Y-%m-%d %H:%M:%S')
    date_str=datetime.datetime.strftime(now_time,'%Y%m%d%H%M%S')
    shift_id_result=emp_sn+date_str
    add_shift_id='insert into zy_shift_turnover (shift_id,shift_emp_sn,shift_date) values(%s,%s,%s)'
    create_shift_id_cur.execute(add_shift_id,(shift_id_result,emp_sn,shift_date))
    create_shift_id_db.commit()
    create_shift_id_cur.close()
    create_shift_id_db.close()
    
        
    shift_id_json=json.dumps({'currt_id':shift_id_result},indent=4)
    
    return shift_id_json

@app.route('/get_patient',methods=['GET','POST'])
@login_required
def get_patient():
    pass
        
    
    

if __name__ == '__main__':
    app.run(host = '192.168.199.203',debug = True)
    
    