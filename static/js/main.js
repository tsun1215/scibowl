function flyDown(msg, type){
    if(type==0){
        $("body").append("<div class='flyDown success'><img src='/static/images/check.png' id='checkmark' height='20px' alt='Check Mark' title='Success'/>"+msg+"</div>");
    }else if(type==1){
        $("body").append("<div class='flyDown fail'><img src='/static/images/cross.png' id='checkmark' height='20px' alt='Cross' title='Unsuccessful'/>"+msg+"</div>");
    }
    var flydown = $(".flyDown").last();
    $(flydown).slideDown(500).delay(1500).fadeOut(1000, function(){
        flydown.remove();
    });
}

function questionPopup(){
    var specs = "width=450,height=430,menubar=0,scrollbars=0,toolbar=0,status=0,toolbar=0,resizable=0,location=0";
    newWindow = window.open("/question/add/","Add Question",specs);
}