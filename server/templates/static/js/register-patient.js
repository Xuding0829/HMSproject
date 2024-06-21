$(function(){
    /*错误class  form-control is-invalid
    正确class  form-control is-valid*/
    var flagPhone=false;
    var flagPas=false;
    var flagPass=false;
    var flagBirth=false;
    var flagname=false;
    /*验证用户名*/
    var phone,passWord,passWords, birthday, name;
    $("#register-phone").change(function(){
        phone=$("#register-phone").val();
        if(phone.length != 11 || phone.match(/\d*/i) != phone){
            $("#register-phone").removeClass("form-control is-valid")
            $("#register-phone").addClass("form-control is-invalid");
            flagPhone=false;
        }else{
            $("#register-phone").removeClass("form-control is-invalid")
            $("#register-phone").addClass("form-control is-valid");
            flagPhone=true;
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
    $("#register-name").change(function(){
        name=$("#register-name").val();
        if(name.length<1){
            $("#register-name").removeClass("form-control is-valid")
            $("#register-name").addClass("form-control is-invalid");
            flagname=false;
        }else{
            $("#register-name").removeClass("form-control is-invalid")
            $("#register-name").addClass("form-control is-valid");
            flagname=true;
        }
    })
    $("#register-birthday").change(function(){
        birthday=$("#register-birthday").val();
        flagBirth=true;
    })
    
    
    $("#regbtn").click(function(){
        if(flagPhone&&flagPas&&flagPass){
            localStorage.setItem("phone",phone);
            localStorage.setItem("passWord",passWord);
            userdata = {'phone':phone, 'password':passWord, 'name':name, 'birthday':birthday};
            $.ajax({
                url: '/register-patient', // 服务器端的URL
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
            if(!flagPhone){
                $("#register-phone").addClass("form-control is-invalid");
            }
            if(!flagPas){
                $("#register-password").addClass("form-control is-invalid");
            }
            if(!flagPass){
                $("#register-passwords").addClass("form-control is-invalid");
            }
            if(!flagname)
            {
                $("#register-name").addClass("form-control is-invalid");
            }
        }
    })
})