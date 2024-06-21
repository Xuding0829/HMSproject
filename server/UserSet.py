from flask import Flask, json, request, render_template, jsonify, url_for, redirect
from flask_mqtt import Mqtt
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey, UUID
from datetime import datetime, timezone


app = Flask('api')
app.config['SECRET_KEY'] = 'hms_scrkey'
app.config['MQTT_BROKER_URL'] = '50d55e0ae4.st1.iotda-device.cn-east-3.myhuaweicloud.com'  
app.config['MQTT_BROKER_PORT'] = 1883          #mqtt服务器端口和ip设置
app.config['MQTT_USERNAME'] = '661a2131387fa41cc8a21155_server'  # 当你需要验证用户名和密码时，请设置该项
app.config['MQTT_PASSWORD'] = '8379b741ed9ed694db1899642cccbdba346c29703f640085eb9fce63673af948'  # 当你需要验证用户名和密码时，请设置该项
app.config['MQTT_CLIENT_ID'] = '661a2131387fa41cc8a21155_server_0_0_2024041412'
app.config['MQTT_KEEPALIVE'] = 120  # 设置心跳时间，单位为秒
#app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/hms_user'        #数据库地址
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


db = SQLAlchemy()
with app.app_context():
    session = db.session()
#管理员用户模型
class AdminUser(db.Model, UserMixin):
    __tablename__ = 'AdminUser'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    sub_des = db.Column(db.String(15), nullable=False, unique=True)

    def get_id(self):
        return f"Admin_{self.id}"

#病人用户模型
class PatientUser(db.Model, UserMixin):
    __tablename__ = 'PatientUser'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    real_id = db.Column(db.String(18), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(10), nullable=False)
    medical_id = db.Column(db.String(30), nullable=False, unique=True) 
    def get_id(self):
        return f"Patient_{self.id}"

class Medicine(db.Model):
    __tablename__ = 'Medicine'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    form = db.Column(db.String(255), nullable=False)  # 剂型
    specification = db.Column(db.String(255), nullable=False)  # 规格
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)  # 库存数量
    usage = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)  # 单价
    notes = db.Column(db.Text)  # 备注

class Medication_Record(db.Model):
    __tablename__ = 'Medication_Record'
    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    doctor_id = db.Column(db.Integer, ForeignKey('AdminUser.id'), nullable=False)  # 医生ID
    patient_id = db.Column(db.Integer, ForeignKey('PatientUser.id'), nullable=False)  # 病人ID
    prescribe_time = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))  # 开药时间
    remarks = db.Column(db.Text)    #诊疗建议
    
    
class Medication_Usage(db.Model):
    __tablename__ = 'Medication_Usage'
    id = db.Column(db.Integer, primary_key=True)
    medicine_record_id = db.Column(db.Integer, ForeignKey('Medication_Record.id'), nullable=False)  # 记录ID
    medicine_id = db.Column(db.Integer, ForeignKey('Medicine.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)  # 备注


#mqtt = Mqtt(app)
socket = SocketIO(app)