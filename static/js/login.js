$(function(){
    $('#login').dialog({
       title:'登陆',
       width: 300,
       height:180,
       modal:true,
       iconCls:'icon-login',
       buttons:'#btn',
    });
    $('#user').validatebox({
        required:true,
        missingMessage:'请输入用户名',
    });
    $('#password').validatebox({
        required:true,
        missingMessage:'请输入密码',
    });
    
    if(!$('#user').validatebox('isValid')){
            $('#user').focus();
        } else if(!$('#password').validatebox('isValid')){
            $('#password').focus();
        }
    
    $('#btn a').click(function(){
        if(!$('#user').validatebox('isValid')){
            $('#user').focus();
        } else if(!$('#password').validatebox('isValid')){
            $('#password').focus();
        } else{
            $.ajax({
                url:'/login',
                type:'post',
                data:{
                    user:$('#user').val(),
                    password:$('#password').val(),
                },
                beforeSend:function(){
                    $.messager.progress({
                        text:'正在登陆准备中......',
                    });
                },
                success:function(data,response,status){
                    $.messager.progress('close');
                    if (data>0){
                        location.href='/'
                    }else{
                        $.messager.alert('登陆失败！','用户名或密码错误！','warning',function(){
                            $('#password').select();
                        });
                    }
                }
            });
        }
    });
});