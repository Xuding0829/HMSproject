import numpy as np
import hashlib, json
#计算前进的方向
def calculate_direction(current_pos, next_pos, is2=False):
    

    direction = np.arctan2(next_pos[1] - current_pos[1], next_pos[0] - current_pos[0])
    if is2:
        return (int(360 - np.degrees(direction) + 90 - 90)) % 360
    return (int(360 - np.degrees(direction) + 90)) % 360

def point_to_segment_distance(point, segment_start, segment_end):
    # 将点和线段端点转换为NumPy数组以进行向量化计算
    point = np.array(point)
    segment_start = np.array(segment_start)
    segment_end = np.array(segment_end)
    # 计算线段的方向向量
    segment_vector = segment_end - segment_start
    # 计算从起点到目标点的向量
    point_vector = point - segment_start
    # 计算点到线段起点的投影长度
    projection_length = np.dot(point_vector, segment_vector) / np.dot(segment_vector, segment_vector)
    # 如果投影在线段范围内，则投影点即为离目标点最近的点
    if 0 <= projection_length <= 1:
        nearest_point = segment_start + projection_length * segment_vector
    else:
        # 否则，选择离目标点更近的线段端点
        if projection_length < 0:
            nearest_point = segment_start
        else:
            nearest_point = segment_end
    # 计算目标点到最近点的距离
    distance = np.linalg.norm(point - nearest_point)
    return distance

def calculate_file_sha256(file_path, sha256_hash = None):
    # 创建SHA256哈希对象
    if sha256_hash == None:
        sha256_hash = hashlib.sha256()
    
    # 以二进制模式打开文件
    with open(file_path, "rb") as f:
        # 按块读取文件内容
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    # 返回文件的SHA256哈希值（十六进制形式）
    return sha256_hash

def default_converter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
    
def type_debug(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            type_debug(v, path=f"{path}.{k}")
            type_debug(k, path=f"{path}.{k}_key")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            type_debug(item, f"{path}[{i}]")
    else:
        try:
            json.dumps(obj)
        except Exception as e:
            print(f"Cannot serialize: {path}, value: {obj}, type: {type(obj)}")