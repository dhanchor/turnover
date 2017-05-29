# -*-coding:utf-8 -*-
from flask import Flask,render_template,request,session,redirect,url_for
from flask_login import LoginManager,login_required,login_user,UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
import json
import mysql.connector
import datetime
import sys
import pymssql

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
    emp_sn = session.get('emp_sn')
    if (emp_sn):
        mysql_selectShiftId_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
        mysql_selectShiftId_cur=mysql_selectShiftId_db.cursor(dictionary=True)
        selectShiftId_sql='select shift_id as id,shift_id as text,shift_id as url \
                          from zy_shift_turnover \
                          where shift_emp_sn=%s'
        mysql_selectShiftId_cur.execute(selectShiftId_sql%emp_sn)
        empShiftId=mysql_selectShiftId_cur.fetchall()
        empShiftId_json=json.dumps([{'id': i['id'], 'text': i['text'],'url':i['url']} for i in empShiftId], indent=4)
        return empShiftId_json

@app.route('/turnover/<id>',methods=['GET','POST'])
@login_required
def turnover(id):
    session['shift_id'] = id
    return render_template('turnover.html',id=id)

@app.route('/get_patient_list',methods=['GET','POST'])
@login_required
def get_patient_list():
    shift_id= session.get('shift_id')
    get_patient_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
    get_patient_cur=get_patient_db.cursor(dictionary=True,buffered=True)
    get_patient_total_cur=get_patient_db.cursor(dictionary=True,buffered=True)
    page=request.values.get('page')
    rows=request.values.get('rows')
    offset=int(rows)*(int(page)-1)
    query='select a.id,a.patient_id,a.bed_no,a.name,a.sex,a.age,a.inpatient_no,a.admiss_diag_str,a.shift_content,\
          a.focus,b.shift_emp_sn,a.admiss_times,a.patient_status,a.succession_emp_sn \
          from patient_list a inner join zy_shift_turnover b \
          where a.shift_id=b.shift_id and a.shift_id=%s and a.is_deleted=\'0\' limit %s,%s'
    get_patient_cur.execute(query,(shift_id,offset,int(rows)))
    get_patient_total_cur.execute('select count(*) as record_count from patient_list a inner join zy_shift_turnover b where a.shift_id=b.shift_id and a.shift_id=%s'%shift_id)  
    patient_list_result=get_patient_cur.fetchall() 
    patient_list_total=get_patient_total_cur.fetchall()
    for a in patient_list_total:
        total=a['record_count']
    patient_list_json = json.dumps({'total':total,'rows':[{'id':i['id'],'patient_id':i['patient_id'],'bed_no':i['bed_no'],'name':i['name'],'sex':i['sex'],'age':i['age'],'inpatient_no':i['inpatient_no'],\
                                                       'admiss_diag_str':i['admiss_diag_str'],'shift_content':i['shift_content'],'focus':i['focus'],'admiss_times':i['admiss_times'],\
    'patient_status':i['patient_status'],'succession_emp_sn':i['succession_emp_sn']} for i in patient_list_result]},indent=4)
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
#@login_required
def get_patient():
    bed_no=request.values.get('bedno')
    emp_dept_sn= session.get('dept_sn')
    #emp_dept_sn=request.values.get('dept_sn')
    with pymssql.connect(server='172.16.100.16',user='sa',password='sql',database='hiszy') as getPatient_report_conn:
        with getPatient_report_conn.cursor(as_dict = True) as getPatient_report_cur:
            getPatient_sql='SELECT p.patient_id,b.bed_no,p.admiss_times,p.name,sex=s.name,age = dbo.GetPatientAge(p.birthday, GETDATE()),p.inpatient_no,p.admiss_diag_str\
                           FROM   dbo.zy_in_patient p(NOLOCK)\
                           INNER JOIN dbo.zy_bed b(NOLOCK)\
                           ON  p.ward = b.ward_sn\
                           AND p.bed_no = b.bed_no\
                           INNER JOIN dbo.dic_sex_code s(NOLOCK)\
                           ON  p.sex = s.code\
                           INNER JOIN dbo.dic_dept_code d(NOLOCK)\
                           ON  p.dept = d.dept_sn\
                           INNER JOIN (SELECT DISTINCT ward_sn,ward_name\
                           FROM   dbo.zy_ward_define(NOLOCK)) w\
                           ON  p.ward = w.ward_sn\
                           WHERE CHARINDEX(b.bed_status, \'2,9\') > 0 and b.bed_no = %s AND p.ward = %s' 
            getPatient_report_cur.execute(getPatient_sql,(bed_no,emp_dept_sn))
            mssql_getPatient=getPatient_report_cur.fetchall()
            if getPatient_report_cur.rowcount==0:
                return '0'
    patientinfo_json=json.dumps(mssql_getPatient,indent=4)
    return patientinfo_json
    '''     
    if mssql_getPatient is not None:
        mysql_insertPatient_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
        mysql_insertPatient_cur=mysql_insertPatient_db.cursor(dictionary=True)
        insertPatient_sql='insert into patient_list (patient_id,bed_no,name,sex,age,inpatient_no,admiss_diag_str,\
                          admiss_times) values (%s,%s,%s,%s,%s,%s,%s,%s)'
        mysql_insertPatient_cur.execute(insertPatient_sql,(mssql_getPatient['patient_id'],mssql_getPatient['bed_no'],mssql_getPatient['name'],\
                                                           mssql_getPatient['sex'],mssql_getPatient['age'],mssql_getPatient['inpatient_no'],\
        mssql_getPatient['admiss_diag_str'],mssql_getPatient['admiss_times']))
        mysql_insertPatient_db.commit()
        mysql_insertPatient_cur.close()
        mysql_insertPatient_db.close()
        patientinfo_json=json.dumps(mssql_getPatient,indent=4)
        return patientinfo_json
    else:
        return '0'
    '''
@app.route('/save_patient',methods=['POST'])
@login_required
def save_patient():
    if request.method=='POST':
        bed_no=request.values.get('bedno')
        inpatient_no=request.values.get('inpatientno')
        patient_id=request.values.get('patientid')
        patient_status=request.values.get('patientstatus')
        name=request.values.get('name')
        sex=request.values.get('sex')
        age=request.values.get('age')
        admiss_diag_str=request.values.get('admiss_diag_str')
        admiss_times=request.values.get('admiss_times')
        succession_emp_sn=request.values.get('succession_emp_sn')
        shift_content=request.values.get('shift_content')
        focus=request.values.get('focus')
        add_emp_sn=session.get('emp_sn')
        shift_id=session.get('shift_id')
        mysql_insertPatient_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
        mysql_insertPatient_cur=mysql_insertPatient_db.cursor(dictionary=True)
        insertPatient_sql='insert into patient_list (patient_id,inpatient_no,admiss_times,bed_no,name,patient_status,sex,age,admiss_diag_str,\
                          succession_emp_sn,shift_content,focus,shift_id,add_emp_sn) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        mysql_insertPatient_cur.execute(insertPatient_sql,(patient_id,inpatient_no,admiss_times,bed_no,name,patient_status,sex,age,admiss_diag_str,\
                                                           succession_emp_sn,shift_content,focus,shift_id,add_emp_sn))
        mysql_insertPatient_db.commit()
        mysql_insertPatient_cur.close()
        mysql_insertPatient_db.close()
        return '1'

@app.route('/get_patient_status',methods=['POST'])
def get_patient_status():
    if request.method=='POST':
        mysql_selectPatientStatus_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
        mysql_selectPatientStatus_cur=mysql_selectPatientStatus_db.cursor(dictionary=True)
        selectPatientStatus_sql='select id,patient_status from dic_patient_status'
        mysql_selectPatientStatus_cur.execute(selectPatientStatus_sql)
        selectPatientStatusResult=mysql_selectPatientStatus_cur.fetchall()
        #patientStatus_json=json.dumps(selectPatientStatusResult,indent=4)
        patientStatus_json=json.dumps ([{'id':i['id'],'patient_status':i['patient_status']}for i in selectPatientStatusResult],indent=4)
        return patientStatus_json
    
@app.route('/edit_patient',methods=['POST'])
def edit_patient():
    if request.method=='POST':
        pl_id=request.values.get('id')
        patient_status=request.values.get('patientstatus')
        succession_emp_sn=request.values.get('succession_emp_sn')
        shift_content=request.values.get('shift_content')
        focus=request.values.get('focus')
        mysql_updatePatient_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
        mysql_updatePatient_cur=mysql_updatePatient_db.cursor(dictionary=True)
        updatePatient_sql='update patient_list set shift_content=%s,focus=%s,succession_emp_sn=%s,patient_status=%s \
                          where id=%s'
        mysql_updatePatient_cur.execute(updatePatient_sql,(shift_content,focus,succession_emp_sn,patient_status,pl_id))
        mysql_updatePatient_db.commit()
        mysql_updatePatient_cur.close()
        mysql_updatePatient_db.close()
        return '1'

@app.route('/delete_patient',methods=['POST'])
def delete_patient():
    if request.method=='POST':
        pl_id=request.values.get('id')
        mysql_deletePatient_db=mysql.connector.Connect(database='dh_inf_manage',user='root',password='password')
        mysql_deletePatient_cur=mysql_deletePatient_db.cursor(dictionary=True)
        delete_patient_sql='update patient_list set is_deleted= \'1\' where id=%s'
        mysql_deletePatient_cur.execute(delete_patient_sql%pl_id)
        mysql_deletePatient_db.commit()
        mysql_deletePatient_cur.close()
        mysql_deletePatient_db.close()
        return '1'

if __name__ == '__main__':
    app.run(host = '172.17.141.203',debug = True)
    
    