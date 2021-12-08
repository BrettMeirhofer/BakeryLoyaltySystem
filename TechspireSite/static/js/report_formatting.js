$(document).ready(function () {
    $(".phone").each(function () {
        var original_string = $(this).text().replace(/\s+/g, '');
        console.log(original_string)
        var last4 = original_string.slice(-4)
        original_string = original_string.substring(0,original_string.length -4)
        var last3 = original_string.slice(-3)
        original_string = original_string.substring(0,original_string.length -3)
        var area = original_string.slice(-3)
        original_string = original_string.substring(0, original_string.length -3)
        var output = original_string + "-" + area + "-" + last3 + "-" + last4
        $(this).text(output)
    })
})