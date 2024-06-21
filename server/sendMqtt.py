from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.region.region import Region
from huaweicloudsdkiotda.v5 import *
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.auth.credentials import DerivedCredentials

ak = "BKWMOWKPSS0VN5EFAGJR"
sk = "FUGCw2zgAtXKdMF5paMX3JJ6p2pD4dNgqYPAEslD"
project_id = "d6452ce762744431b80422b35a7dc220"
# region_id：如果是上海一，请填写"cn-east-3"；如果是北京四，请填写"cn-north-4"；如果是华南广州，请填写"cn-south-1"
region_id = "cn-east-3"
# endpoint：请在控制台的"总览"界面的"平台接入地址"中查看"应用侧"的https接入地址
endpoint = "50d55e0ae4.st1.iotda-app.cn-east-3.myhuaweicloud.com"

# 标准版/企业版：需自行创建Region对象
REGION = Region(region_id, endpoint)

# 创建认证
# 创建BasicCredentials实例并初始化
credentials = BasicCredentials(ak, sk, project_id)

# 标准版/企业版需要使用衍生算法，基础版请删除配置"with_derived_predicate"
credentials.with_derived_predicate(DerivedCredentials.get_default_derived_predicate())

# 基础版：请选择IoTDAClient中的Region对象 如： .with_region(IoTDARegion.CN_NORTH_4)
# 标准版/企业版：需要使用自行创建的Region对象
ioTDAClient = IoTDAClient.new_builder() \
    .with_credentials(credentials) \
    .with_region(REGION) \
    .build()


def publish(client, *args):
    data = ' '.join([str(arg) for arg in args])
    try:
        request_obj =  CreateMessageRequest(device_id='661a2131387fa41cc8a21155_' + client)
        request_obj.body = DeviceMessageRequest(message=data, payload_format='raw')
        response = ioTDAClient.create_message(request_obj)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)