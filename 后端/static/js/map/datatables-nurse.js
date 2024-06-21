var room;
var datatable;

var now_patient = null;
var medicines = {};
var infusionlist = {};


$(document).ready(function () {

    datatable = $('#datatables').DataTable({
        "createdRow": function (row, data, dataIndex) {
            // 检查特定列的数据，比如第3列（索引为2），是否满足条件.
            console.log(1)
            if (data[4] == "warning") {
                $(row).addClass('red-row'); // 添加类来改变颜色
            }
            $(row).click(function(e){
                if(!$(e.target).is('button') && !$(e.target).is('select'))
                open_detail(data[1]);
            })
        },
        "columnDefs": [{
            "targets": 1,
            "render": function (data, type, row) {

                return `<button onclick="window.location.herf = '#graph-container'" class="btn btn-outline-secondary">查看位置</button>`;
            }
        },
        {
            "targets": 3,
            "render": function (data, type, row) {
                if (data == null)
                return "";
                return data.toFixed(2) + '毫升/分钟';
            }
        },
        {
            "targets": 4,
            "render": function (data, type, row) {
                
                if (data == 'warning') {
                    return '即将结束';
                }
                else if(data == null)
                return "";
                return data.toFixed(2) + '毫升';
            }
        },
        {
            "targets": 5,
            "render": function (data, type, row) {
                if (data == null)
                return "";
            
                return moment(data).format('HH:mm:ss');;
            }
        },
        {
            "targets": 6,
            "render": function (data, type, row) {
                result = [`<select name="${data}-medicines" id="${data}-medicines" class="form-control form-control-line">`];
                if(row[4] == null)
                {
                    return "尚未开始";
                }
                infusionlist[data].medicine.forEach(function(medicine){
                    option = document.createElement('option');
                    option.value = medicine;
                    option.textContent = medicines[medicine].name;
                    if(infusionlist[data].now_med == medicine)
                        option.selected = true;
                    result.push(option.outerHTML);
                });
                result.push('</select>');
                return result.join('\n');
            }
        }
        ],
        "autoWidth": true
    });
    
    $.ajax({
        url: '/map-nurse', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: JSON.stringify({ "display": true }), // 将数据转换为JSON字符串
        success: function (response) {
            $.ajax({
                url: '/medicine/get',
                type: 'POST',
                data: '',
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (response) {
                    Object.assign(medicines, response);
                }
            });
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
            socket.on('medicine_change', function (data) {
                data = JSON.parse(data);
                Object.assign(medicines, data);
            });
    
            $.ajax({
                url: '/map-nurse', // 服务器端的URL
                type: 'POST', // 请求类型，GET、POST、PUT等
                contentType: 'application/json', // 发送数据的格式
                data: "", // 将数据转换为JSON字符串
                success: function (response) {
                    infusionlist = JSON.parse(response);
                    displayed = to_display(infusionlist);
                    room = 'infusionlist';
        
                    datatable.clear();
                    datatable.rows.add(displayed).draw();
                    loc = window.location;
                    socketUrl = loc.host;
        
                    socket.on('connect', function () {
                        socket.emit('room', 'medicine');
                        socket.emit('room', room);
                        console.log('Successfully connected!');
                    });
                    socket.on('infusionlist', function (data) {
                        data = JSON.parse(data);
                        displayed = to_display(data);
                        datatable.clear();
                        datatable.rows.add(displayed).draw();
                    });
                },
                error: function (xhr, status, error) {
                    // 请求失败时的回调函数
                    console.error('Error:', error);
                }
            });
        }
    });
    

});

function to_display(infusionlist){
    return Object.entries(infusionlist).map(([key, value]) => [
        value.name,
        key,
        value.age,
        value.speed,
        value.remain,
        value.querytime != null ? ((new Date(value.querytime)).getTime() + (value.remain / value.speed * 60 * 1000)) : null,
        key
    ]);
}

function moveToPos(client) {
    document.getElementById('client').value = client;
    window.location.href = "#graph-container";
    $.ajax({
        url: '/graph/devicepos', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: JSON.stringify({ "client": client }), // 将数据转换为JSON字符串
        success: function (response) {
            response = JSON.parse(response);
            document.getElementById('floor').value = response.floor;
            nowfloor = $("#floor").val();
            nowclient = $("#client").val();
            updateGraph(nowfloor, nowclient);
        },
        error: function (xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
        }
    });
}

function finish_check(client) {
    $.ajax({
        url: '/map-nurse/finishInfusion', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: JSON.stringify({ "client": client }), // 将数据转换为JSON字符串
        success: function (response) {
            response = JSON.parse(response);
            waitlist = response.waitlist;
            Object.assign(fullwaitlist, waitlist);
            datatable.clear();
            displaylist = to_display(fullwaitlist);
            datatable.rows.add(displaylist).draw();
        },
        error: function (xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
        }
    });
}

function open_detail(client)
{
    $('#detailModal').modal('show');
}