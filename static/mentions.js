//This Javascript class is for mentions and for querying the available users
//and opening a select field that filters your input and writes in the input on enter



function registerAtSign(event){
    var target_id = event.target.id
    if (event.key == "@"){
        console.log("registerAtSign was called");
        $('#'+target_id).autocomplete({
        delimiter: " ",
        showNoSuggestionNotice: true,
        serviceUrl: "/mentions/registered/users/score/",
        onSelect: function (suggestion) {
        $(this.id).autocomplete('dispose')
        
    }
});
    }
    if (event.key == " " || event.keyCode == 13){
        $('#'+target_id).autocomplete('dispose')

    }

}

function getRegisteredUsers(){
    $.ajax(
        {
            type: "POST",
            dataType: 'jsonp', //mispelled
            url: "/mentions/registered/users/score.json/",
            async: true,
            contentType: "application/json; charset=utf-8",
            success: function(msg){
                console.log(msg)
                return msg;}
        }
    )
}

function messageRead(message_id){
//     req = new XMLHttpRequest()
//     req.open("POST", '/notification/clicked/', true)
//     req.send("msg_id"=message_id)

$.ajax({
    type: 'POST',
    url: '/notifications/clicked/',
    data: { 
        'msg_id': String(message_id)
        }
    
});

}