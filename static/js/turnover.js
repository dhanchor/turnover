$(function(){
    $('#turnover').datagrid({
        url:'/get_patient_list',
        columns:[[
            {
                field:'patient_id',
                title:'患者ID',
                width:100,
            },
        ]],
    });
});