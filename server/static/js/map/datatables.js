var room;
var fullwaitlist = {};
var datatable;

var { pinyin } = pinyinPro;
var medicine_submit, medicine_list;
var medicines = {};
var now_patient = null;
var patient_med = {};
var ai_messages = {};
var username;
/*
    medicines = {
        id:{
            'name':
            'form':
            'specification':
            'quantity':
            'usage':
            'price':
            'notes':
        }
    }
*/

$(document).ready(function () {

    datatable = $('#datatables').DataTable({
        "columnDefs": [{
                "targets": 2,
                "render": function(data, type, row) {
                    
                    return `<button onclick="moveToPos('${data}')" class="btn btn-outline-secondary">查看位置</button>`;
                }
            },
            {
                "targets": 6,
                "render": function(data, type, row) {
                    
                    return `<button onclick="open_medicineList('${data}')" class="btn btn-outline-secondary">药方详情</button>`;
                }
            },
            {
                "targets": 7,
                "render": function(data, type, row) {
                    
                    return `<button onclick="send_Medicine_Record('${data}')" class="btn btn-outline-danger">完成就诊</button>`;
                }
            },
            {
                "targets": 0,
                "render": function(data, type, row) {
                    if(data == "0"){
                        return "就诊中";
                    }
                    return "等待中";

                }
            }
        ],
        "autoWidth": true
    });
    
    medicine_submit = $('#medicine-submit').DataTable({
        "info": false,
        "lengthChange":false,
        paging: false,
        searching:false,
        
        'language': {
            'paginate': {
                'previous': '上一页',
                'next': '下一页'
            },
            emptyTable: "暂无药品"
        },
        "columnDefs": [{
                "targets": 5, // 目标列 - 假设"Position"是第二列
                "render": function(data, type, row) {
                    
                    return `<button onclick="medicine_delete('${data}')" class="btn btn-outline-danger">删除</button>`;
                }
            },
            {
                "targets": 4, // 目标列 - 假设"Position"是第二列
                "render": function(data, type, row) {
                    
                    return `<input id="${row[5]}-quantity" value="${data}" type="number" class="form-control" style="width:60px;margin-left:auto;margin-right:auto;" min=1 max=${medicines[row[5]].quantity}>
                    <script>
                    $("#${row[5]}-quantity").change(function(){
                        patient_med[now_patient][${row[5]}] = Number($("#${row[5]}-quantity").val())
                    });
                    </script>
                    `;
                }
            }
        ],
        "autoWidth": true
    });
    medicine_list = $('#medicine-list').DataTable({
        "info": false,
        "lengthChange":false,
        searching:false,
        'language': {
            'paginate': {
                'previous': '上一页',
                'next': '下一页'
            }
        },
        "columnDefs": [{
                "targets": 5, // 目标列 - 假设"Position"是第二列
                "render": function(data, type, row) {
                    
                    return `<button onclick="medicine_add('${data}')" class="btn btn-outline-primary">添加</button>`
                }
            }
        ],
        "autoWidth": true
    });
    
    $.ajax({
        url: '/map/ai-chat', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: '', // 将数据转换为JSON字符串
        success: function(response) {
            data = JSON.parse(response);
            Object.assign(ai_messages, data);
            ai_messages['device1'] = "- **病人症状**：患者出现发烧症状，但未出现咳嗽，目前为复诊情况。\n  \n- **疑似病症**：鉴于发烧是多种疾病的共有症状，且未伴有咳嗽，可能涉及的病症有感冒、轻度呼吸道感染、或其他炎症性疾病。\n\n- **治疗建议**：建议医生详细询问病史，进行全面的体格检查，并根据以下情况进行处理：\n    - 若发烧原因尚不明确，可进行必要的实验室检查（如血常规、尿常规等）以辅助诊断。\n    - 若有感染迹象，可考虑给予抗炎或抗感染治疗。\n    - 针对发烧症状，可适当采用物理降温或退烧药物治疗。\n\n- **注意事项**：\n    - 在多病流行期，注意患者在医院内的交叉感染风险，建议在基层医院首诊或采用互联网复诊。\n    - 对于发烧患者，注意保持充分的休息和水分摄入，密切监测体温变化。\n    - 避免自行随意用药，尤其是抗生素等需要医嘱的药物，以免影响病情观察和后续治疗。 \n\n（共约100字）"
        }
    });

    $.ajax({
        url: '/map/datatable', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: '', // 将数据转换为JSON字符串
        success: function(response) {
            response = JSON.parse(response);
            username = response.username;
            room = 'waitlist_' + username;
            waitlist = response.waitlist;
            Object.assign(fullwaitlist, waitlist);
            datatable.clear();
            displaylist = to_display(fullwaitlist);
            datatable.rows.add(displaylist).draw();
            med = localStorage.getItem('patient_med')
            if(med != null){
            patient_med = JSON.parse(localStorage.getItem('patient_med'));
            Object.keys(patient_med)
                .filter(key => !datatable.column(2).data().toArray().includes(key))
                .forEach(key => delete patient_med[key]);
            }
            else
            {
                patient_med = {}
            }
            loc = window.location;
            socketUrl = loc.host;
            
            socket = io.connect(socketUrl, {
                // 自动重连
                reconnection: true, // 默认为 true
                // 重连尝试的次数，Infinity 表示无限次
                reconnectionAttempts: Infinity, 
                // 初始重连延迟毫秒数
                reconnectionDelay: 1000, 
                // 最大重连延迟毫秒数
                reconnectionDelayMax: 5000, 
                // 用于增加重连延迟的随机化因子，以避免重连风暴
                randomizationFactor: 0.5 
            });
            socket.on('connect', function() {
                socket.emit('room', room);
                socket.emit('room', username);
                console.log('Successfully connected!');
            });
            socket.on('waitlist', function(data){
                data = JSON.parse(data);
                Object.assign(fullwaitlist, data);
                datatable.clear();
                displaylist = to_display(fullwaitlist);
                datatable.rows.add(displaylist).draw();
            });
        },
        error: function(xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
        }
    });

    
    $('#medicine-list_wrapper').prepend('<div id="medicine-list_filter" class="dataTables_filter"><label>搜索:<input type="search" class="" placeholder="" aria-controls="medicine-list"></label></div>')
    $('#medicine-list_filter input').on('keyup', function() {
        // 每次键盘按键抬起时清除搜索查询并重新绘制表格
        var input = $('#medicine-list_filter input').val().trim().toLowerCase();
        medicine_list.rows().every(function(){
            data = this.data();
            var name = data[0].toString().trim().toLowerCase(); // 假设名称在第一列
            var nameFirstLetter = pinyin(name, {
                pattern: 'first',
                toneType: 'none',
                type: 'array'
            }).join('');
            var namepinyin = pinyin(name, {
                toneType: 'none',
                type: 'array',
                v: true
            }).join('');
            if (nameFirstLetter.indexOf(input) !== -1 || name.indexOf(input) !== -1 || namepinyin.indexOf(input) !== -1)
            {
                $(this.node()).show();
            }
            else
            $(this.node()).hide();
        })
    });

    get_Medicine_Record();

    loc = window.location;
            socketUrl = loc.host;
            
            socket = io.connect(socketUrl, {
                // 自动重连
                reconnection: true, // 默认为 true
                // 重连尝试的次数，Infinity 表示无限次
                reconnectionAttempts: Infinity, 
                // 初始重连延迟毫秒数
                reconnectionDelay: 1000, 
                // 最大重连延迟毫秒数
                reconnectionDelayMax: 5000, 
                // 用于增加重连延迟的随机化因子，以避免重连风暴
                randomizationFactor: 0.5 
            });
            socket.on('connect', function() {
                socket.emit('room', 'medicine');
                console.log('Successfully connected!');
            });
            socket.on('medicine_change', function(data){
                data = JSON.parse(data);
                Object.assign(medicines, data);
                medicine_list.clear();
                displayed_medicine = medicine_to_display();
                medicine_list.rows.add(displayed_medicine).draw();
            });
    
});

function to_display(waitlist){
    copylist = {...waitlist};
    displaylist = [];
    for(key in copylist){
        if (waitlist.hasOwnProperty(key))
        {
            copylist[key] = copylist[key].map((sublist, index) =>{
                sublist.push(sublist[1]);
                return [index, ...sublist, sublist[sublist.length - 1]];
            });
            displaylist.push(...copylist[key]);
        }
    }
    return displaylist;

}

function moveToPos(client){
    document.getElementById('client').value = client;
    window.location.href = "#graph-container";
    $.ajax({
        url: '/graph/devicepos', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: JSON.stringify({"client":client}), // 将数据转换为JSON字符串
        success:  function(response) {
            response = JSON.parse(response);
            document.getElementById('floor').value = response.floor;
            nowfloor = $("#floor").val();
            nowclient = $("#client").val();
            updateGraph(nowfloor, nowclient);
        },
        error: function(xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
        }
    });
}

function finish_check(client){
    $.ajax({
        url: '/map/finish', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: JSON.stringify({"client":client}), // 将数据转换为JSON字符串
        success:  function(response) {
            response = JSON.parse(response);
            waitlist = response.waitlist;
            Object.assign(fullwaitlist, waitlist);
            datatable.clear();
            displaylist = to_display(fullwaitlist);
            datatable.rows.add(displaylist).draw();
        },
        error: function(xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
        }
    });
}

function get_Medicine_Record()
{
    $.ajax({
        url: '/medicine/get',
        type: 'POST',
        data:'',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            Object.assign(medicines, response);
            displayed_medicine = medicine_to_display();
            medicine_list.clear().rows.add(displayed_medicine).draw();
            
        }
    });
}

function send_Medicine_Record(client)
{
    if(patient_med.hasOwnProperty(client) && Object.keys(patient_med[client]) !== 0)
    {
            $.ajax({
            url: '/medicine/Prescribe',
            type: 'POST',
            data:JSON.stringify({
                client:client,
                medicineList:patient_med[client]
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response) {
                finish_check(client);
            },
            error: function(xhr, status, error) {
                // 请求失败时执行的操作
                console.log("请求失败");
                console.log("状态码：" + xhr.status); // 输出状态码
                console.log("错误信息：" + error); // 输出错误信息
                if(error != 'FAIL')
                {
                    alert(medicines[error.full].name + '库存不足');
                }
            }
        });
    }
    else
    {
        finish_check(client);
    }
}

function medicine_add(medicine_id)
{
    if(!patient_med[now_patient].hasOwnProperty(medicine_id))
    {
        patient_med[now_patient][medicine_id] = 1;
        localStorage.setItem('patient_med', JSON.stringify(patient_med));
        medicine_submit_display();
    }
}

function medicine_delete(medicine_id)
{
    delete patient_med[now_patient][medicine_id];
    localStorage.setItem('patient_med', JSON.stringify(patient_med));
    medicine_submit_display();
}

function medicine_to_display()
{
    displayed = Object.entries(medicines).map(([key, value]) => [value.name, value.form, value.specification, value.price, value.quantity, key])
    return displayed;
}

function medicine_submit_display()
{
    displayed_list = Object.entries(patient_med[now_patient]).map(([key, value]) => [medicines[key].name, medicines[key].form, medicines[key].specification, medicines[key].price, value, key]);

    medicine_submit.clear().rows.add(displayed_list).draw();
}

function open_medicineList(client)
{
    now_patient = client;
    patient_name = datatable.row(datatable.column(2).data().toArray().indexOf(client)).data()[1];
    $('#patient-name').text(patient_name);
    if(!patient_med.hasOwnProperty(client))
    {
        patient_med[client] = {};
    }

    medicine_submit_display()
    $('#ai-result').html(marked.parse(ai_messages[client]))
    $('#medicineModal').modal('show');
}

function close_medicineList()
{
    $('#medicineModal').modal('hide');
}

