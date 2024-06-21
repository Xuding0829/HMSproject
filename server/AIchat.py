from zhipuai import ZhipuAI
client = ZhipuAI(api_key="a19d743e970f97000da29ad71ca3b004.NDszZOg6rQ3TBnOr") # 请填写您自己的APIKey

def get_response(cough, heat, twice):
    if cough:
        cough = '咳嗽'
    else:
        cough = '不咳嗽'
    if heat:
        heat = '发烧'
    else:
        heat = '不发烧'
    if twice:
        twice = '复诊'
    else:
        twice = "初诊"
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": '''
            你是一个辅助医生进行诊断的助手，你的任务是根据用户提供的病症情况，向医生复述病人症状并根据症状进行初步诊断，并向医生提供诊断建议。
            格式分点为：病人症状，疑似病症，治疗建议，注意事项。
            使用无级列表进行分点陈述，以第三方身份向医生讲解，内容根据病人的实际情况和最近的流行病等出发，在陈述病人症状阶段，禁止添加不存在的症状，不能随意夸大病症，共100字左右。
            '''},
            {"role": "user", "content": f"有以下症状：{cough}，{heat}，{twice}"},
        ]
    )
    return response.choices[0].message.content