DJQ = django.jQuery;


$(document).ready(function () {

    //Update totals when an OrderLine or reward is removed
    DJQ(document).on('formset:removed', function (event, row, formsetName) {
        update_order_total()
    });

    convert_money_inline(".field-ind_price")
    convert_money_inline(".field-total_price")
    convert_money_inline(".field-discount_amount", parent_element = "orderreward")
    convert_money("field-original_total")
    convert_money("field-discount_amount")
    convert_money("field-final_total")
    convert_money("field-eligible_for_points")
    update_on_store()

    //Update Employee/Product/Reward dropdown when Store is changed
    var store_binding = $("#id_store").change(update_on_store);
    var customer_binding = $("#id_customer").change(update_rewards);

    //When quantity changes update line_total and order_total
    $("tbody").on("change", '[id^="id_orderline_set-"][id$="-quantity"]', function () {
        line_num = this.id.substring(17, 18)
        update_line_total(line_num)
    })

    //When product changes update ind_price, line_total, order_total
    $("tbody").on("change", '[id^="id_orderline_set-"][id$="-product"]', function () {
        update_product_row(this)
    })

    $("tbody [id^=id_orderreward_set-][id$=-reward]").each(function () {
        update_reward_row(this)
    })

    $("tbody [id^=id_orderline_set-][id$=-product]").each(function () {
        console.log("Update Order-Line")
        update_product_row(this)
    })

    //When reward changes update point cost, discount, extra product
    $("tbody").on("change", '[id^="id_orderreward_set-"][id$="-reward"]', function () {
        console.log("Updated Reward")
        update_reward_row(this)
        update_rewards()
    })
})


//Updates all the calculated fields related to money/points
function update_order_total() {
    var order_total = 0
    var eligible = 0
    var order_total = 0
    $(".field-total_price p").each(function (index) {
        console.log("Each")
        let line_total = $(this).text()
        line_total = line_total.substring(1)
        line_total = Number(parseFloat(line_total).toFixed(2))
        order_total += line_total


        var id_name = "orderline_set-" + index
        var eligible_element = $("#" + id_name + " .field-points_eligible p img")
        if (typeof eligible_element.attr("src") !== 'undefined') {
            console.log(typeof eligible_element.attr("src"))
            if (eligible_element.attr("src").includes("yes")) {
                console.log("Valid for reward system")
                eligible += line_total
            }
        }
    })

    var discount = 0
    $(".field-discount_amount p").each(function () {
        num = parseInt($(this).text().substring(1))
        if (!isNaN(num)) {
            console.log(num)
            discount += num
        }
    })

    var points_consumed = 0
    $(".field-point_cost p").each(function () {
        num = parseInt($(this).text())
        points_consumed += num
    })



    points_produced = (Math.floor(parseFloat(eligible) / 5)).toFixed(0)
    points_total = points_produced - points_consumed
    console.log(discount)
    final_total = order_total - discount

    //Format as money
    final_total = format_money(final_total)
    order_total = format_money(order_total)
    discount = format_money(discount)
    eligible = format_money(eligible)

    //Update elements
    $(".field-final_total div div").text(final_total)
    $(".field-original_total div div").text(order_total)
    $(".field-eligible_for_points div div").text(eligible)
    $(".field-points_produced div div").text(points_produced)
    $(".field-discount_amount div div").text(discount)
    $(".field-points_total div div").text(points_total)
    $(".field-points_consumed div div").text(points_consumed)
}

//Updates every products dropdown
function update_products() {
    var url = $("#Product_URL").attr("data-url");  // get the url of the `load_cities` view
    var storeID = $("#id_store").val();  // get the selected country ID from the HTML input
    var selected = []

    $('[id^="id_orderline_set-"]').filter('[id$="-product"]').each(function () {
        selected.push($(this).val());
    });
    $.ajax({                       // initialize an AJAX request
        url: url,                    // set the url of the request (= localhost:8000/hr/ajax/load-cities/)
        data: {
            'store': storeID       // add the country id to the GET parameters
        },
        success: function (data) {
            $('[id^="id_orderline_set-"]').filter('[id$="-product"]').each(function (index) {
                $(this).html(data)
                $(this).val(selected[index])
                if ($(this).val() == null) {
                    $(this).val("")
                    var text = parseFloat("0").toFixed(2)
                    line_num = $(this).attr('id').substring(17, 18)
                    var id_name = "orderline_set-" + line_num
                    var query = "#" + id_name + " " + ".field-ind_price" + " p"
                    $(query).text("$" + text)
                    update_line_total(line_num, true)

                }
            });
        }
    })
}

//Update every rewards dropdown
function update_rewards() {

    var url = $("#Reward_URL").attr("data-url");
    var storeID = $("#id_store").val();
    console.log("Sent Rewards Request")

    var selected = []
    $('[id^="id_orderreward_set-"]').filter('[id$="-reward"]').each(function () {
        selected.push($(this).val());
    });


    $.ajax({
        url: url,
        data: {
            'store': storeID
        },
        success: function (data) {
            console.log("Rewards Request Sucess")
            $('[id^="id_orderreward_set-"]').filter('[id$="-reward"]').each(function (index) {
                $(this).html(data)
                $(this).val(selected[index])
                if ($(this).val() == null) {
                    $(this).val("")
                    update_reward_line(0, convert_money(0), "None", index)
                }
            });
        }
    })



}

//Updates the employee dropdown
function update_emps() {
    var url = $("#Emp_URL").attr("data-url");
    var storeID = $("#id_store").val();
    var target_element = $("#id_employee")
    var empID = target_element.val();
    $.ajax({
        url: url,
        data: {
            'store': storeID
        },
        success: function (data) {
            target_element.html(data);
            target_element.val(empID)
            //If selected option doesn't exsist reset it to blank
            if (target_element.val() == null) {
                target_element.val("")
            }
        }
    })
}

//Updates the total for a orderline row
function update_line_total(line_num) {
    var total_id = "orderline_set-" + line_num
    var total_query = "#" + total_id + " " + ".field-total_price" + " p"
    var ind_id = "orderline_set-" + line_num
    var ind_query = "#" + ind_id + " " + ".field-ind_price" + " p"
    var price = $(ind_query).text()
    price = price.substr(1)
    price = parseFloat(price).toFixed(2)
    var qty_query = "#" + "id_orderline_set-" + line_num + "-quantity"
    var qty = $(qty_query).val()
    total = price * qty
    total_text = "$" + parseFloat(total).toFixed(2)
    $(total_query).text(total_text)
    update_order_total()

    return total

}

//converts money for each row in an inline
function convert_money_inline(element_id, parent_element = "orderline") {
    parent_element_query = '[id^=' + parent_element + '_set-]'
    $(parent_element_query).children("td").filter(element_id).children("p").each(function () {
        $(this).text("$" + parseFloat($(this).text()).toFixed(2))
    })

}

//Converts money for fields in the overall form
function convert_money(element) {
    var target_element = $("." + element + " div div")
    target_element.text("$" + parseFloat(target_element.text()).toFixed(2))
}

//Several dropdowns need to be updated whenever the store updates
function update_on_store() {
    update_products()
    update_rewards()
    update_emps()
}

//Adds a dollar sign and sets decimals to 2
function format_money(input) {
    return "$" + parseFloat(input).toFixed(2)
}


function update_reward_line(cost, discount, product, line) {
    console.log(discount)
    var id_name = "orderreward_set-" + line

    var cost_select = "#" + id_name + " " + ".field-point_cost" + " p"
    var discount_select = "#" + id_name + " " + ".field-discount_amount" + " p"
    var product_select = "#" + id_name + " " + ".field-free_product" + " p"
    console.log(cost_select)
    $(cost_select).text(cost)
    $(discount_select).text(format_money(discount))
    $(product_select).text(product)

}


function update_reward_row(target_element) {
    var url = $("#Reward_Details_URL").attr("data-url");
    var rewardID = $(target_element).val()
    $.ajax({
        url: url,
        data: {
            'reward': rewardID
        },
        success: function (data) {
            var line_num = target_element.id.replace(/\D/g, '');
            console.log(line_num)
            console.log(data)
            update_reward_line(data.cost, data.discount, data.product, line_num)
            update_order_total()
        }
    })
}


function update_product_row(target_element, update_total) {
    var url = $("#Product_Price_URL").attr("data-url");
    var productID = $(target_element).val()
    $.ajax({
        url: url,
        data: {
            'product': productID
        },
        success: function (data) {
            //Update ind_price    
            var text = parseFloat(data.price).toFixed(2)
            var line_num = target_element.id.substring(17, 18)
            var id_name = "orderline_set-" + line_num
            if (line_num != "_") {
                var query = "#" + id_name + " " + ".field-ind_price" + " p"
                var eligible_element = $("#" + id_name + " .field-points_eligible p img")

                first = "yes"
                last = "no"
                if (data.eligible == "None") {
                    first = "no"
                    last = "yes"
                }
                var current = eligible_element.attr("src")
                current = current.replace(first, last)
                eligible_element.attr("src", current)
                $(query).text("$" + text)
                update_line_total(line_num)
            }

        }
    })

}