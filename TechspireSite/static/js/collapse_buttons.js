$(document).ready(function () {
    $(".collapse_button").click(function (){
        target = $(this).parent().parent().children("tbody")
        if (target.css("visibility") == "collapse"){
            target.css("visibility", "visible")
        }
        else{
            target.css("visibility", "collapse")
        }
    })
})
