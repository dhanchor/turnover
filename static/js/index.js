$(function(){
     
    obj={
        add_shift_id:function(){
            $.ajax({
                    type:'post',
                    url:'/creat_shift_id',
                    data:{
                        
                    },
                    success:function(data){
                        if(data){
                                    $('#nav').tree('reload');
                                    $('#tabs').tabs('add',{
                                        title:date,
                                        closable:true,
                                        href:'/turnover/'+node.text,
                                    });
                                }
                    },
                
                });
        },
        
    };
    
       
    $('#nav').tree({
        url:'/zy_shift_turnover',
        line:true,
        onLoadSuccess:function(node,data){
            if(data){
                $(data).each(function(index,value){
                    if(this.state=='closed'){
                        $('#nav').tree('expanAll');
                    }
                });
            }
        },
        onClick:function(node){
            if(node.text){
                if($('#tabs').tabs('exists',node.text)){
                   $('#tabs').tabs('select',node.text);
                   var tab = $('#tabs').tabs('getSelected');
                   tab.panel('refresh','/turnover/'+node.text)
                }else{
                    $('#tabs').tabs('add',{
                        title:node.text,
                        closable:true,
                        href:'/turnover/'+node.text,
                    });
                }
            }
        }
        
    });
    
    $('#tabs').tabs({
        fit:true,
        border:false,
    });
});