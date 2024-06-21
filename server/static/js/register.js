$(function(){
    /*错误class  form-control is-invalid
    正确class  form-control is-valid*/
    var flagName=false;
    var flagPas=false;
    var flagPass=false;
    var flagsub=false;
    /*验证用户名*/
    var name,passWord,passWords,sub;
    $("#register-username").change(function(){
        name=$("#register-username").val();
        if(name.length<2||name.length>10){
            $("#register-username").removeClass("form-control is-valid")
            $("#register-username").addClass("form-control is-invalid");
            flagName=false;
        }else{
            $("#register-username").removeClass("form-control is-invalid")
            $("#register-username").addClass("form-control is-valid");
            flagName=true;
        }
    })
    /*验证密码*/
    $("#register-password").change(function(){
        passWord=$("#register-password").val();
        if(passWord.length<6||passWord.length>18){
            $("#register-password").removeClass("form-control is-valid")
            $("#register-password").addClass("form-control is-invalid");
            flagPas=false;
        }else{
            $("#register-password").removeClass("form-control is-invalid")
            $("#register-password").addClass("form-control is-valid");
            flagPas=true;
        }
    })
    /*验证确认密码*/
    $("#register-passwords").change(function(){
        passWords=$("#register-passwords").val();
        if((passWord!=passWords)||(passWords.length<6||passWords.length>18)){
            $("#register-passwords").removeClass("form-control is-valid")
            $("#register-passwords").addClass("form-control is-invalid");
            flagPass=false;
        }else{
            $("#register-passwords").removeClass("form-control is-invalid")
            $("#register-passwords").addClass("form-control is-valid");
            flagPass=true;
        }
    })

    $("#register-subdes").change(function(){
        sub=$("#register-subdes").val();
        if(sub.length < 1){
            $("#register-subdes").removeClass("form-control is-valid")
            $("#register-subdes").addClass("form-control is-invalid");
            flagsub=false;
        }else{
            $("#register-subdes").removeClass("form-control is-invalid")
            $("#register-subdes").addClass("form-control is-valid");
            flagsub=true;
        }
        
    })
    
    $("#regbtn").click(function(){
        if(flagName&&flagPas&&flagPass&&flagsub){
            localStorage.setItem("name",name);
            localStorage.setItem("passWord",passWord);
            userdata = {
                'name':name, 
                'password':passWord,
                'sub_des':sub
            };
            $.ajax({
                url: '/register', // 服务器端的URL
                type: 'POST', // 请求类型，GET、POST、PUT等
                contentType: 'application/json', // 发送数据的格式
                data: JSON.stringify(userdata), // 将数据转换为JSON字符串
                success: function(response) {
                    if(response == 'SUCCESS')
                    {
                        document.getElementById("regbtn").textContent = "注册成功"
                        //window.location.href = '/login'
                        setTimeout(window.location.href='/login', 1000);
                    }
                    else if(response == 'EXIST')
                    {
                        console.log('exist')
                        alert("用户名已存在")
                    }
                },
                error: function(xhr, status, error) {
                    // 请求失败时的回调函数
                    console.error('Error:', error);
                }
            });
        }else{
            if(!flagName){
                $("#register-username").addClass("form-control is-invalid");
            }
            if(!flagPas){
                $("#register-password").addClass("form-control is-invalid");
            }
            if(!flagPass){
                $("#register-passwords").addClass("form-control is-invalid");
            }
            if(!flagsub)
            {
                $("#register-subdes").addClass("form-control is-invalid");
            }
        }
    })
})