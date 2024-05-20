# mqtt数据传递格式说明

### 手环→mqtt服务器

topic统一使用“main_control”进行通信，格式为

```json
action client *args
```

| 字段名称 | 类型   | 描述                   |
| -------- | ------ | ---------------------- |
| action   | String | 当前通讯的目标行为     |
| client   | String | 手环设备的唯一标识符   |
| args     | Object | 当前行为需要传入的参数 |

目前支持的action有

| action参数名      | 参数列表                                                     | 描述                         |
| ----------------- | ------------------------------------------------------------ | ---------------------------- |
| reg_data_in       | medical_id(电子医疗凭证，测试可选)                           | 挂号时传入信息               |
| RFID_Num          | RFID                                                         | 传递RFID值，用于定位         |
| setClientTarget   | target:String/Object，例如：<br />target为Object时：<br />{<br />“target”:{<br />“pos”:[3.92, 19.9],<br />“floor”:1<br />}<br />}<br /><br />target为String时：<br />{<br />“target”:”领取处”<br />} | 设置设备的目的地             |
| setBodyTemp       | temperature:Num                                              | 设置当前设备获取到的体温值   |
| CountSensor_Count | Count（每30秒的滴数）                                        | 定时汇报流速，可用于开始输液 |
| warning           | status(1为开始报警，0位报警结束，输液结束)                   | 用于控制点滴警报             |
| delDevice         | /                                                            | 设备解绑                     |

### mqtt服务器→手环

topic使用手环对应的唯一标识符进行通信，格式为：

```json
action *args
```

| 字段名称 | 类型   | 描述                   |
| -------- | ------ | ---------------------- |
| action   | String | 当前通讯的目标行为     |
| args     | Object | 当前行为需要传入的参数 |

目前支持的action有：

| action参数名 | args参数列表                                  | 描述                           |
| ------------ | --------------------------------------------- | ------------------------------ |
| direction    | direction:num，表示方向。360为上楼，361为下楼 | 向手环通信行走方向             |
| sign_direct  | /                                             | 停止导航                       |
| register     | username                                      | 用于表示已挂号，并传输挂号科室 |
| sign_call    | /                                             | 叫号                           |
| wait_time    | minute                                        | 汇报预计等待的分钟数           |

