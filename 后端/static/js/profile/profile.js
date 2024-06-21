
var dataPass=false;
var pname;
var id;
var phone;
var client;
  
$(document).ready(function () {
    document.getElementById('input-target').value = '等候区'
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
        socket.emit('room', 'register');
        console.log('Successfully connected!');
    });

    socket.on('regdata', function(data){
        console.log(data)
        pname = data.name;
        id = data.id;
        phone = data.phone;
        client = data.client;
        document.getElementById('Main-name').textContent = pname;
        document.getElementById('input-name').value = pname;
        document.getElementById('input-id').value = id;
        document.getElementById('input-phone').value = phone;
        document.getElementById('input-client').value = client;
        dataPass=true;
    });
})
function submit_data()
{
    if(dataPass){
        data = {
            "real_id":id,
            "client":client,
            "target":$("#input-target").val(),
            "regpos":$("#input-regpos").val(),
            "twice":($("#input-twice").val())
        };
        $.ajax({
            url:"/pages-profile",
            type:"POST",
            contentType: 'application/json', // 发送数据的格式
            data: JSON.stringify(data), // 将数据转换为JSON字符串
            dataType: "json",
            success: function (response) {
                console.log(response);
                window.location.reload();
            },
            error: function(xhr, status, error) {
                // 请求失败时执行的操作
                console.log("请求失败");
                console.log("状态码：" + xhr.status); // 输出状态码
                console.log("错误信息：" + error); // 输出错误信息
            }
        });
    }
}