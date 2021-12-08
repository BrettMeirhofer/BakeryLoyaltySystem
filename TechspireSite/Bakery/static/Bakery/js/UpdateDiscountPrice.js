$(document).ready(function () {
    var target_element = $("#id_discount_amount")
    target_element.attr("step",.01)
    target_element.attr("type","text")
    update_currency_field(target_element)
    target_element.change(update_currency_field)
    target_element.before("<span>$")
    target_element.after("</span>")
})

function update_currency_field(){
    var target_element = $("#id_discount_amount")
    var updated_value = parseFloat(target_element.val())
    updated_value = updated_value.toFixed(2)
    updated_value = updated_value
    target_element.val(updated_value)
}

