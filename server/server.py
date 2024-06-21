from flask import Flask, json, request, render_template, jsonify, url_for, redirect, send_from_directory
from flask_mqtt import Mqtt
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Date
from sqlalchemy import event

from networkx import json_graph
import pandas as pd
from shapely.geometry import mapping

import json, os, threading

from tools import *
from graph import *
from DeviceSets import *
from UserSet import *


main_topic = '$oc/devices/661a2131387fa41cc8a21155_server/sys/messages/down'



devices = DeviceSets(expand_Gragh(), socket, app)


@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('Patient_'):
        Patient_id = user_id[8:]  # 移除前缀
        return PatientUser.query.get(int(Patient_id))
    elif user_id.startswith('Admin_'):
        admin_id = user_id[6:]  # 移除前缀
        return AdminUser.query.get(int(admin_id))
    return None

@app.route('/table-basic')
@login_required
def tabel_basic():
    return render_template('table-basic.html')

@app.route('/icon-material')
@login_required
def icon_material():
    return render_template('icon-material.html')

@app.route('/pages-blank')
@login_required
def pages_blank():
    return render_template('pages-blank.html')

#主界面
@app.route('/')
@login_required
def index():
    return render_template('index.html')

#网页api，用于更改设备目的地
@app.route('/settarget', methods=['POST'])
@login_required
def settarget():
    data = json.loads(request.data.decode())
    devices.setClientTarget(**data)
    return jsonify(dict(status='SUCCESS'))

@app.route('/graph/devicepos', methods=['POST'])
@login_required
def get_devicepos():
    data = json.loads(request.data.decode())
    return json.dumps({
        "pos":devices.GetClientPos(**data),
        "floor":devices.GetClientFloor(**data)    
    })


#网页api，用于获取地图信息
@app.route('/graph', methods=['POST'])
@login_required
def getGraph():
    args = json.loads(request.data.decode())
    isnurse = False
    if 'nurse' in args.keys():
        if args['nurse'] == True:
            isnurse = True
    
    
    if isnurse:
        warnings = []
        infusings = []
        obstacle_data = json.dumps(mapping(devices.G.GetNurseObs()))
        for client, device in devices.devices.items():
            if device.infusion.remain != None:
                if device.infusion.warning:
                    warnings.append(dict(client=client, pos=device.pos))
                else:
                    infusings.append(dict(client=client, pos=device.pos))
        return jsonify(dict(obstacle=obstacle_data, warnings=warnings, infusings=infusings))
    floor = args['floor']
    if type(floor) == str:
        floor = int(floor)
    if 'medical_id' in args.keys():
        client = devices.id2client[args['medical_id']]
    else:
        client = args['client']
    edges = []
    try:
        copy_G = devices.G.nodeGraph[floor].copy()
    except:
        print("未初始化完成")
        return None
    devicepos = None
    if client != None:
        devicepos = devices.GetClientPos(client)
        if(devices.GetClientTarget(client) != None and devices.devices[client].path != None):
            path = devices.devices[client].path
            edges = [(devices.G.GetNodePos(path[i]), devices.G.GetNodePos(path[i + 1])) for i in range(len(path) - 1) if devices.G.GetNodeFloor(path[i]) == floor and devices.G.GetNodeFloor(path[i + 1]) == floor]
            if devices.GetClientFloor(client) == floor and devices.G.GetNodeFloor(path[0]) == floor:
                edges.append((devicepos, devices.G.GetNodePos(path[0])))
        if devices.GetClientFloor(client) != floor:
            devicepos = None
    json_Data = eval(str(json_graph.node_link_data(copy_G)))
    graphdata = json.dumps(json_Data)
    obstacle_data = json.dumps(mapping(devices.G.display_obstacles[floor]))
    #print(devices.G.edges())
        
    
    return jsonify(dict(graphData=graphdata, devicepos=devicepos, obstacle=obstacle_data, path=edges))

@app.route('/map/ai-chat', methods=["POST"])
def ai_chat():
    adminuser = current_user
    messages = {}
    for client, device in devices.devices.items():
        if('answer' in device.question.keys()) and (adminuser.username == 'admin' or adminuser.sub_des == device.regpos):
            messages[client] = device.question['answer']
    return json.dumps(messages)

#管理员登录界面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('userName')
        password = request.form.get('passWord')
        user = session.query(AdminUser).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user=user)
            return redirect('/')
        return render_template('login.html', msg='账号或密码错误')
    return render_template('login.html', msg='')

#登出页面
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#注册界面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = eval(request.data.decode())
        username = data['name']
        password = data['password']
        sub_des = data['sub_des']
        user = session.query(AdminUser).filter_by(username=username).first()
        if user:
            return 'EXIST'
        newUser = AdminUser(
            username=username, 
            password=generate_password_hash(password, "pbkdf2:sha256"),
            sub_des=sub_des
        )
        db.session.add(newUser)
        db.session.commit()
        return 'SUCCESS'
    return render_template('register.html')

#病人注册界面
@app.route('/register-patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        data = json.loads(request.data.decode())
        phone = data['phone']
        password = data['password']
        real_id = data['real_id']
        medical_id = data['medical_id']
        name = data['name']
        user = session.query(PatientUser).filter_by(phone=phone).first()
        if user:
            return 'EXIST', 409
        newUser = PatientUser(
            phone=phone, 
            password=generate_password_hash(password, "pbkdf2:sha256"),
            name=name,
            real_id=real_id,
            medical_id=medical_id    
        )
        session.add(newUser)
        session.commit()
        return 'SUCCESS', 200
    return render_template('register-patient.html')

#病人登录界面
@app.route('/login-patient', methods=['GET', 'POST'])
def login_patient():
    if request.method == 'POST':
        data = request.form.to_dict()
        phone = data['phone']
        password = request.form.get('password')
        user = session.query(PatientUser).filter_by(phone=phone).first()
        if user and check_password_hash(user.password, password):
            login_user(user=user)
            return 'SUCCESS', 200
        return 'FAIL', 401
    return render_template('login-patient.html')

@app.route('/report-files/<patients>/<filename>', methods=['GET', 'POST'])
def get_report_file(patients, filename):
    return send_from_directory(os.path.join('static', 'reports-files', patients), filename)

@app.route('/report-files/<patients>', methods=['GET', 'POST'], strict_slashes=False)
def get_patients_report(patients):
    return json.dumps(os.listdir(os.path.join('static/reports-files', patients)))


@app.route('/report', methods=['POST'])
def get_reports():
    data = json.loads(request.data.decode())
    phone = data['phone']
    patient = session.query(PatientUser).filter_by(phone=phone).first()
    medicines = session.query(Medicine).all()
    med_records = session.query(Medication_Record).filter_by(patient_id=patient.id).all()
    med_usages = session.query(Medication_Usage).filter(Medication_Usage.medicine_record_id.in_([rec.id for rec in med_records])).all()
    rec_usages_dict = defaultdict(lambda :dict(medicines=[]))
    id2med = {med.id:med for med in medicines}
    
    for usage in med_usages:
        rec_usages_dict[usage.medicine_record_id]['medicines'].append({'medicineName':id2med[usage.medicine_id].name, 'cautions':id2med[usage.medicine_id].usage + id2med[usage.medicine_id].notes if id2med[usage.medicine_id].notes != None else id2med[usage.medicine_id].usage})
    for rec in med_records:
        rec_usages_dict[rec.id]['suggestion'] = rec.remarks

    return json.dumps(rec_usages_dict)
    

#网页api，用于更换头像
@app.route('/upload-userpic', methods=['POST'])
@login_required
def upload_userpic():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    file = request.files['image']
    if file:
        file.save(os.path.join('static/assets/images/users', current_user.phone + '.jpg'))
        return "SUCCESS", 200
    return jsonify({'error': 'No image file'}), 400

#地图界面
@app.route('/map')
@login_required
def map_page():
    nodes = []
    for k,v in devices.G.nodeGraph.items():
        nodes.extend(v.nodes())

    return render_template(
        'map.html',
        clients=devices.devices.keys(),
        floors=list(devices.G.obstacles.keys()),
        targets=nodes
    )

@app.route('/medicine/Prescribe', methods=['POST'])
@login_required
def medicine_Prescribe():
    data = json.loads(request.data.decode())
    adminuser = current_user
    id = devices.medicinePrescribe(adminuser, **data)
    if id != None:
        if id == False:
            return 'FAIL', 500
        else:
            return json.dumps({'full':id}), 409
    return {'status':'SECCESS'}, 200
@app.route('/medicine/get', methods=['POST'])
@login_required
def get_medicines():
    with app.app_context():
        try:
            medicines = {medicine.id:{
                    'name':medicine.name,
                    'form':medicine.form,
                    'specification':medicine.specification,
                    'quantity':medicine.stock_quantity,
                    'usage':medicine.usage,
                    'price':medicine.price,
                    'notes':medicine.notes
                } for medicine in session.query(Medicine).all()}
        except:
            session.rollback()
    return json.dumps(medicines)

@app.route('/map/datatable', methods=['POST'])
@login_required
def datatable():
    username = current_user.username
    return json.dumps(dict(
        waitlist=devices.GetWaitList(username),
        username=username
    ))

@app.route('/map/finish', methods=['POST'])
@login_required
def finish_check():
    data = json.loads(request.data.decode())
    devices.finishWait(**data)
    return datatable(), 200

@app.route('/map/get_deviceid', methods=['POST'])
@login_required
def get_deviceid():
    data = json.loads(request.data.decode())
    return devices.id2client[data['medical_id']]

@app.route('/map-nurse', methods=['GET', 'POST'])
@login_required
def map_nurse_page():
    if request.method == 'POST':
        infusionlist = devices.GetInfusionList()
        
        return json.dumps(infusionlist)
    
    return render_template('map-nurse.html')

@app.route('/map-nurse/finishInfusion', methods=['POST'])
@login_required
def finishInfusion():
    data = json.loads(request.data.decode())
    client = data['client']
    devices.stopInfusion(client)
    return 'SUCCESS', 200

@app.route('/infusion-submit')
@login_required
def infusion_submit():
    return render_template('fluid-infusion.html')

#管理员个人信息界面
@app.route('/pages-profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    if request.method == 'POST':
        data = json.loads(request.data.decode())
        real_id = data['real_id']
        client = data['client']
        target = data['target']
        regpos = data['regpos']
        twice = data['twice']
        devices.register(client, twice, regpos, target)
        return json.dumps(dict(status='SUCCESS')), 200
    nodes = []
    for k,v in devices.G.nodeGraph.items():
        nodes.extend(v.nodes())
    return render_template('pages-profile.html', nodes=nodes)
@app.route('/pages-profile/import', methods=['GET'])
@login_required
def profile_import():
    data = request.args.to_dict()
    devices.reg_data_in(**data)
    return "SUCCESS", 200

@socket.on('room')
def room(data):
    join_room(data)   

with app.app_context():
    db.init_app(app)
    db.create_all()
#mqtt.subscribe(main_topic)
#print('已连接至',main_topic)

#mqtt接受到信息
@app.route('/mqtt/on-message', methods=["POST"])
def on_message():
    data = json.loads(request.data.decode())['notify_data']['body']['content'].strip('\r').split(' ')
    try:
        action = data[0]
        args = data[1:]
        print("收到命令", data)
        t = threading.Thread(target=eval('devices.' + action), args=args)
        t.start()
        #eval('devices.' + action)(*args)
    except (Exception) as e:
        print(data)
        print(e)
    return {'status':'SUCCESS'}, 200



socket.run(app, host='0.0.0.0', port=8880, debug=False)