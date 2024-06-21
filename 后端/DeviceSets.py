'''
该文件用于设备组的管理和函数实现
'''

import re
import numpy as np
import networkx as nx
from collections import defaultdict, deque
import json, time
import pytz
from shapely.geometry import LineString, Point, Polygon
from datetime import datetime, timedelta
from flask_socketio import emit

from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.region.region import Region
from huaweicloudsdkiotda.v5 import *
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.auth.credentials import DerivedCredentials


from UserSet import *
from tools import *
from graph import *
from AIchat import get_response

OBSTACLES_LAYER = "0"
AVERAGE_WAITTIME = 4
STARTTARGET = '领取处'
STARTPOS = dict(pos=(24.24, 3.84), floor=1)
INFUSION_START = 200
MIN_DIS = 3
NURSE_LOC = Polygon([(9.9, 20.1), (20.1, 20.1), (20.1, 4.2), (9.9, 4.2)])
PRE_IDNUM = {
    'device1':'10001',
    'device2':'10002',
    'di1':'10010',
    'di2':'10012',
    'di3':'10013',
    'di4':'10014',
    'di5':'10015',
    'di6':'10016',
}
WAIT_DES = dict(
    pos=Polygon([(0, 20), (2.1, 20), (2.1, 14.85), (0, 14.85)]),
    floor=2    
)

class DeviceSets:
    def __init__(self, G, socket, app):
        self.devices = dict()
        self.G = G
        self.app = app
        self.socket = socket
        self.layer_navi = False
        self.id2client = defaultdict(None)
        self.queues = defaultdict(deque)
        self.nurseLoc = NURSE_LOC
        self.dd2client = defaultdict(None)
        self.ak = "BKWMOWKPSS0VN5EFAGJR"
        self.sk = "FUGCw2zgAtXKdMF5paMX3JJ6p2pD4dNgqYPAEslD"
        self.project_id = "d6452ce762744431b80422b35a7dc220"
        # region_id：如果是上海一，请填写"cn-east-3"；如果是北京四，请填写"cn-north-4"；如果是华南广州，请填写"cn-south-1"
        self.region_id = "cn-east-3"
        # endpoint：请在控制台的"总览"界面的"平台接入地址"中查看"应用侧"的https接入地址
        self.endpoint = "50d55e0ae4.st1.iotda-app.cn-east-3.myhuaweicloud.com"

        # 标准版/企业版：需自行创建Region对象
        self.REGION = Region(self.region_id, self.endpoint)

        # 创建认证
        # 创建BasicCredentials实例并初始化
        self.credentials = BasicCredentials(self.ak, self.sk, self.project_id)

        # 标准版/企业版需要使用衍生算法，基础版请删除配置"with_derived_predicate"
        self.credentials.with_derived_predicate(DerivedCredentials.get_default_derived_predicate())

        # 基础版：请选择IoTDAClient中的Region对象 如： .with_region(IoTDARegion.CN_NORTH_4)
        # 标准版/企业版：需要使用自行创建的Region对象
        self.ioTDAClient = IoTDAClient.new_builder() \
            .with_credentials(self.credentials) \
            .with_region(self.REGION) \
            .build()
    
    def publish(self, client, *args):
        data = ' '.join([str(arg) for arg in args])
        try:
            request_obj =  CreateMessageRequest(device_id='661a2131387fa41cc8a21155_' + client)
            request_obj.body = DeviceMessageRequest(message=data, payload_format='raw')
            response = self.ioTDAClient.create_message(request_obj)
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    #获取设备的目的地
    def GetClientTarget(self, client):
        return self.devices[client].target
    
    #获取设备的位置
    def GetClientPos(self, client):
        return self.devices[client].pos
    
    #获取设备所在楼层
    def GetClientFloor(self, client):
        return self.devices[client].floor
    
    #设置设备所在楼层
    def SetClientFloor(self, client, floor):
        self.devices[client].floor = floor

    #设置设备的位置
    def SetClientPos(self, client, pos):
        self.devices[client].pos = pos
    #获取设备目的地楼层
    def GetTargetFloor(self, client):
        if self.devices[client].target == None:
            return None
        if(type(self.devices[client].target) == str):
            return self.GetNodeFloor(self.devices[client].target)
        return self.devices[client].target['floor']
    #获取设备目的地xy位置
    def GetTargetPos(self, client):
        if(type(self.devices[client].target) == str):
            return self.G.GetNodePos(self.devices[client].target)
        return self.devices[client].target['pos']
    #停止导航
    def sign_direct(self, client):
        if(self.devices[client].target == None):
            return
        self.publish(client, 'sign_direct')
        target = self.devices[client].target
        self.devices[client].target = None
        if(target == '等候区' and self.devices[client].regpos != None and self.devices[client].called == False):
            adminuser = None
            with app.app_context():
                adminuser = session.query(AdminUser).filter_by(sub_des=self.devices[client].regpos).first()
            idx = self.queues[adminuser.username].index(client)
            self.wait_time(client, 3*idx)
            if idx > 0:
                time.sleep(2)
                self.publish(client, 'question')
        
        
    
    #导航计算函数
    def navigation(self, client):
        current_floor = self.GetClientFloor(client)
        target_floor = self.GetTargetFloor(client)
        if(self.layer_navi and current_floor != target_floor):
            self.gotofloor(client, target_floor)
            return
        
        copy_G = self.G.copy()
        copy_G.add_node('now_pos', pos=self.GetClientPos(client), floor=self.GetClientFloor(client))
        target = 'now_target'
        if(type(self.GetClientTarget(client)) == str):
            target = self.GetClientTarget(client)
        else:
            copy_G.add_node(target, pos=self.GetClientTarget(client)['pos'], floor = self.GetClientTarget(client)['floor'])
            copy_G.createSingleVisibilityEdge(target)
        copy_G.createSingleVisibilityEdge('now_pos')
        
        #self.devices[client]['debug_edges'] = [(copy_G.GetNodePos(u), (copy_G.GetNodePos(v))) for u, v in copy_G.edges()]
        path = nx.astar_path(copy_G, source='now_pos', target=target, weight='weight', heuristic=copy_G.heuristic_func)
        if(copy_G.GetNodeFloor(path[1]) != self.GetClientFloor(client)):
            self.gotofloor(client, copy_G.GetNodeFloor(path[1]))
            self.devices[client].path = path[1:]
        elif(len(path) >= 3 and copy_G.GetDistance('now_pos', path[1]) < MIN_DIS and copy_G.GetNodeFloor(path[2]) != self.GetClientFloor(client)):
            self.gotofloor(client, copy_G.GetNodeFloor(path[2]))
            self.devices[client].path = path[2:]
        else:
            self.devices[client].path = path[1:]
            if copy_G.nodes['now_pos']['floor'] == 2:
                self.publish(client, 'direction', calculate_direction(copy_G.nodes['now_pos']['pos'], self.G.nodes[path[1]]['pos'], True))
            else:
                self.publish(client, 'direction', calculate_direction(copy_G.nodes['now_pos']['pos'], self.G.nodes[path[1]]['pos']))
        if self.devices[client].path[-1] == 'now_target':
            self.devices[client].path[-1] = self.GetClientTarget(client)

    def question1(self, client, status):
        if status == '1':
            status = True
        else:
            status = False
        self.devices[client].question[1] = status
    def question2(self, client, status):
        if status == '1':
            status = True
        else:
            status = False
        self.devices[client].question[2] = status
        if 1 in self.devices[client].question.keys():
            self.ai_response(client)

    def ai_response(self, client):
        self.devices[client].question['answer'] = get_response(self.devices[client].question[1], self.devices[client].question[2], self.devices[client].twice)
        with app.app_context():
            adminuser = session.query(AdminUser).filter_by(sub_des=self.devices[client].regpos).first()
            socket.emit('ai_response', self.devices[client].question['answer'], room=adminuser.username)
        
    #设置设备的目的地
    def setClientTarget(self, client, target):
        pos1 = np.array(self.GetClientPos(client))
        self.devices[client].target = target
        if(type(target) == str):
            pos2 = np.array(self.G.nodes[target]['pos'])
        else:
            pos2 = np.array(target['pos'])
        
        if(self.GetTargetFloor(client) == self.GetClientFloor(client) and np.linalg.norm(pos1 - pos2) < MIN_DIS):
            self.sign_direct(client)
            return
        self.navigation(client)
    
    #设置设备的体温值
    def temperature(self, client, temperature):
        self.devices[client].temperature = temperature

    def Gettem(self, client):
        return self.devices[client].temperature
    
    #接受设备的位置信息
    def pos(self, client, current_pos):
        pos = current_pos['pos']
        floor = current_pos['floor']
        self.devices[client].pos = pos
        self.devices[client].floor = floor
        if(self.GetClientTarget(client) != None):
            target_floor = self.GetTargetFloor(client)
            dist = np.linalg.norm(np.array(pos) - np.array(self.GetTargetPos(client)))
            if(floor == target_floor and dist <= MIN_DIS):
                self.sign_direct(client)
                
            else:
                self.navigation(client)

    #发送改变楼层信息
    def gotofloor(self, client, floor):
        if(self.GetClientFloor(client) > floor):
            self.publish(client, 'direction', 361)        #下楼
        else:
            self.publish(client, 'direction', 360)        #上楼

    #添加设备，用于设备和人员绑定
    def addDevice(self, client, medical_id, pos=STARTPOS['pos'], floor=STARTPOS['floor'], target=None):
        if(client not in self.devices or self.devices[client].medical_id != medical_id):
        #client
            with app.app_context():
                self.devices[client] = Device(client, medical_id, pos, floor, target)
            self.id2client[medical_id] = client
            if target == None:
                self.devices[client].target = STARTTARGET
        else:
            print('已存在设备', client)
        if target != None:
            self.devices[client].target = target
        self.navigation(client)
    #删除设备
    def delDevice(self, client):
        if client in self.devices:
            self.id2client[self.devices[client].medical_id] = None
            self.devices.pop(client)
        else:
            print('不存在设备', client)


    '''
    medicineList={
            medicine_id:quantity,
            ...
        }
    '''
    def medicinePrescribe(self, adminuser, client, medicineList):
        with app.app_context():
            id2medicines = {medicine.id:medicine for medicine in session.query(Medicine).filter(Medicine.id.in_(list(medicineList.keys()))).all()}
        
        try:
            med_record = ''
            original_usage = None
            if self.devices[client].medicine != None:
                with app.app_context():
                    original_usage = session.query(Medication_Usage).filter_by(id=self.devices[client].medicine.id)
                med_record = self.devices[client].medicine
            else:
                med_record = Medication_Record(
                    doctor_id = adminuser.id, 
                    patient_id = self.devices[client].user.id,
                    remarks = self.devices[client].question['answer'] if 'answer' in self.devices[client].question.keys() else None
                )
                with app.app_context():
                    session.add(med_record)
                    session.flush()
            with app.app_context():
                for id, quantity in medicineList.items():
                    id = int(id)
                    session.add(Medication_Usage(
                        medicine_record_id = med_record.id,
                        medicine_id = id,
                        quantity = quantity
                    ))
                    id2medicines[id].stock_quantity -= quantity
                    if id2medicines[id].stock_quantity < 0:
                        session.rollback()
                        return id
                if original_usage != None:
                    original_usage.delete()
                session.commit()
                
            socket.emit('medicine_change', {k:{
                'name':v.name,
                'form':v.form,
                'specification':v.specification,
                'stock_quantity':v.stock_quantity,
                'usage':v.usage,
                'price':v.price,
                'notes':v.notes
            } for k, v in id2medicines.items()}, room='medicine')
            self.devices[client].medicine = med_record
            goto_infusion = False
            for id, quantity in medicineList.items():
                id = int(id)
                if id2medicines[id].usage != None and '静点' in id2medicines[id].usage:
                    goto_infusion = True
                    self.devices[client].infusion.medicine.append(id)
            if(goto_infusion):
                with app.app_context():
                    socket.emit('infusionlist', json.dumps(self.GetInfusionList()), room='infusionlist')
                    if self.devices[client].target == None:
                        self.setClientTarget(client, '点滴处')
        except Exception as e:
            session.rollback()
            print('medicinePrescribe:', e)
            return False


    #设置输液的位置和剩余量
    def CountSensor_Count(self, ddclient, Count):
        client = self.dd2client[ddclient]
        if type(Count) == str:
            Count = int(Count)
        if self.devices[client].infusion.remain == None:
            if Count == 0:
                return
            self.devices[client].infusion.now_med += 1
            self.devices[client].infusion.remain = INFUSION_START
            self.devices[client].infusion.starttime = datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(seconds=30)
        self.devices[client].infusion.remain -= Count / 15
        self.devices[client].infusion.speed = Count / 15 / 60
        self.devices[client].infusion.nowtime = datetime.now(pytz.timezone('Asia/Shanghai'))
        if self.devices[client].infusion.warning == True:
            self.publish(client, "warning", 1)
        if(self.devices[client].infusion.remain < 0):
            self.devices[client].infusion.remain = 0
        with app.app_context():
            socket.emit('infusionlist', json.dumps(self.GetInfusionList()), room='infusionlist')

    #停止输液
    def stopInfusion(self, client):
        self.devices[client].infusion.StopInfusion()
        self.publish(client, 'warning', 0)
    def warning(self, ddclient, status):
        client = self.dd2client[ddclient]
        if status == '1':
            self.devices[client].infusion.warning = True
        elif status == '0':
            self.stopInfusion(client)
        with app.app_context():
            socket.emit('infusionlist', json.dumps(self.GetInfusionList()), room='infusionlist')

    def GetInfusionList(self):
        infusionList = dict()
        for client, device in self.devices.items():
            if len(device.infusion.medicine) > 0 and device.infusion.now_med < len(device.infusion.medicine):
                infusionList[client] = {
                    'name':device.user.name,
                    'age':datetime.now().year - int(device.user.real_id[6:10]),
                    'speed':device.infusion.speed * 60 if self.devices[client].infusion.speed != None else None,
                    'remain':device.infusion.remain if not device.infusion.warning else 'warning',
                    'querytime':device.infusion.nowtime.isoformat() if device.infusion.nowtime != None else None,
                    'real_id':device.user.real_id,
                    'phone':device.user.phone,
                    'medicine':device.infusion.medicine,
                    'pos':device.pos,
                    'now_med':device.infusion.now_med,
                    'floor':device.floor
                }
        return infusionList

    def infusionList_todisplay(self, infusionList):
        client2user = {client:self.devices[client].user for client in list(infusionList.keys())}
        return [[
            client2user[client].name, 
            client, 
            datetime.now().year - int(client2user[client].real_id[6:10]), 
            self.devices[client].infusion.speed * 60 if self.devices[client].infusion.speed != None else None,
            infusion['remain'] if not self.devices[client].infusion.warning else 'warning',
            self.devices[client].infusion.get_endtime().isoformat(),
            client
        ] for client, infusion in infusionList.items()]
    #获取节点的楼层

    def GetNodeFloor(self, node):
        return self.G.nodes[node]['floor']
    
    def sign_call(self, client):
        
        if not self.devices[client].called:
            self.devices[client].called = True
            self.setClientTarget(client, self.devices[client].regpos)
            self.publish(client, 'sign_call')

    def reg_data_in(self, client, medical_id=None):
        with app.app_context():    
            medical_id = PRE_IDNUM[client]
            try:
                user = session.query(PatientUser).filter_by(medical_id=medical_id).first()
            except:
                session.rollback()
        data = dict(
            name = user.name,
            id = user.real_id,
            phone=user.phone,
            client=client
        )
        socket.emit('regdata', data, room='register')
    
    def publish_waitlist(self, username, waitlist):
        waitlist = json.dumps(waitlist)
        socket.emit('waitlist', waitlist, room='waitlist_' + username)
        if username != 'admin':
            socket.emit('waitlist', waitlist, room='waitlist_admin')
    
    def register(self, client, twice, regpos, target):
        with app.app_context():
            adminuser = session.query(AdminUser).filter_by(sub_des=regpos).first()
        username = adminuser.username

        self.addDevice(
            client=client,
            medical_id=PRE_IDNUM[client],
            target=target
        )

        if self.devices[client].regpos != None and self.devices[client].regpos != regpos:
            with app.app_context():
                originaladmin = session.query(AdminUser).filter_by(sub_des=self.devices[client].regpos).first()
            if client in self.queues[originaladmin.username]:
                self.queues[originaladmin.username].remove(client)
                self.publish_waitlist(originaladmin.username, self.GetWaitList(originaladmin.username))
                if len(self.queues[originaladmin.username]) > 0:
                    self.sign_call(self.queues[originaladmin.username][0])
        self.devices[client].regpos = regpos
        self.devices[client].twice = twice
        if client not in self.queues[username]:
            self.queues[username].append(client)
            waitdata = self.GetWaitList(username)
            self.publish_waitlist(username, waitdata)
            self.publish(client, 'register', username)
            self.devices[client].called = False
        if target:
            self.setClientTarget(client, target)
        self.sign_call(self.queues[username][0])
        

    def GetWaitList(self, username):
        users = dict()
        if username == 'admin':
            for k, v in self.queues.items():
                users[k] = [self.devices[client].user for client in v]
        else:
            users = {username:[self.devices[client].user for client in list(self.queues[username])]}
        with app.app_context():    
            admins_des = {user.username:user.sub_des for user in sorted(
                session.query(AdminUser).filter(AdminUser.username.in_(list(users.keys()))), 
                key=lambda user: list(users.keys()).index(user.username))}
        
        sock_data = {k:[[
            user.name,
            self.id2client[user.medical_id],
            self.devices[self.id2client[user.medical_id]].twice,
            datetime.now().year - int(user.real_id[6:10]),
            admins_des[k]
        ] for user in v] for k, v in users.items()}
        '''
        {
            username:[
                {datas}, ...
            ]
        }
        '''
        return sock_data
    
    def wait_time(self, client, minute):
        self.publish(client, 'wait_time', minute)

    def finishWait(self, client):
        with app.app_context():
            adminuser = session.query(AdminUser).filter_by(sub_des=self.devices[client].regpos).first()
        username = adminuser.username
        self.queues[username].remove(client)
        if self.devices[client].target == None or self.devices[client].target == self.devices[client].regpos:
            if len(self.devices[client].infusion.medicine) > 0:
                self.setClientTarget(client, '点滴处')
            else:
                self.setClientTarget(client, '入口')
        if len(self.queues[username]) > 0:
            self.sign_call(self.queues[username][0])

    def RFID_Num(self, client, RFID):
        RFID = re.sub(r"[^a-zA-Z0-9]", "", RFID)
        if RFID[:2] == 'dd':
            self.devices[client].infusion.ddid = RFID
            self.dd2client[RFID] = client
            return
        floor = int(RFID[:2])
        x = int(RFID[2:7]) / 100
        y = int(RFID[7:]) / 100
        current_pos = dict(pos=(x, y), floor=floor)

        self.pos(client, current_pos)
    


class Infusion:
    def __init__(self, name, now_med=-1, ddid=None, medicine=None):
        self.remain = None
        self.ddid = None
        self.starttime = None
        self.nowtime = None
        self.warning = False
        self.speed = None
        self.name = name
        self.now_med = now_med
        self.medicine = []

    def get_endtime(self):
        if self.nowtime == None:
            return None
        return self.nowtime + timedelta(seconds=(self.remain / self.speed))

    def StopInfusion(self):
        self.__init__(self.name, self.now_med, self.ddid, medicine=self.medicine)
    
class Device:
    def __init__(self, name, medical_id, pos=STARTPOS['pos'], floor=STARTPOS['floor'], target=None) -> None:
        self.target=target
        self.name = name
        self.path=None
        self.pos=pos
        self.twice = None
        self.called = False
        self.regpos = None
        self.floor=floor
        self.infusion=Infusion(name)
        self.temperature=None
        self.medicine = None
        self.question = {'answer':"- **病人症状**：患者出现发烧症状，但未出现咳嗽，目前为复诊情况。\n  \n- **疑似病症**：鉴于发烧是多种疾病的共有症状，且未伴有咳嗽，可能涉及的病症有感冒、轻度呼吸道感染、或其他炎症性疾病。\n\n- **治疗建议**：建议医生详细询问病史，进行全面的体格检查，并根据以下情况进行处理：\n    - 若发烧原因尚不明确，可进行必要的实验室检查（如血常规、尿常规等）以辅助诊断。\n    - 若有感染迹象，可考虑给予抗炎或抗感染治疗。\n    - 针对发烧症状，可适当采用物理降温或退烧药物治疗。\n\n- **注意事项**：\n    - 在多病流行期，注意患者在医院内的交叉感染风险，建议在基层医院首诊或采用互联网复诊。\n    - 对于发烧患者，注意保持充分的休息和水分摄入，密切监测体温变化。\n    - 避免自行随意用药，尤其是抗生素等需要医嘱的药物，以免影响病情观察和后续治疗。 \n\n（共约100字）"}
        self.medical_id=medical_id
        self.user = session.query(PatientUser).filter_by(medical_id=medical_id).first()