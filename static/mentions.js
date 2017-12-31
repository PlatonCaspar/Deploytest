//This Javascript class is for mentions and for querying the available users
//and opening a select field that filters your input and writes in the input on enter



function registerAtSign(event){
    var target_id = event.target.id
    if (event.key == "@"){
        $('#'+target_id).autocomplete({
        delimiter: " ",
        type: "POST",
        serviceUrl: "/mentions/registered/users/score.json",
        onSelect: function (suggestion) {
        $(this.id).autocomplete('dispose')
        
    }
});
    }
    if (event.key == " "){
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