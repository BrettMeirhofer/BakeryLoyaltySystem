from django.contrib import admin
from django.db.models import CharField
from . import forms
from . import models


def format_phone(target_string):
    last4 = target_string[-4:]
    target_string = target_string[:-4]
    last3 = target_string[-3:]
    target_string = target_string[:-3]
    area = target_string[-3:]
    target_string = target_string[:-3]
    country = target_string
    return country + "-" + area + "-" + last3 + "-" + last4


def update_char_field_len(db_field, field):
    if isinstance(db_field, CharField):
        varchar_em_ratio = 1.8
        max_field_size = 60
        updated_width = min(db_field.max_length / varchar_em_ratio, max_field_size)
        field.widget.attrs['style'] = "width:{}em;".format(updated_width)


class TwentyPageAdmin(admin.ModelAdmin):
    list_per_page = 20
    save_on_top = True
    change_form_template = "admin/hide_inline.html"

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(TwentyPageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        update_char_field_len(db_field, field)
        return field


@admin.register(models.StoreProduct)
class MenuAdmin(TwentyPageAdmin):
    list_display = ["product", "store"]


@admin.register(models.Reward)
class RewardAdmin(TwentyPageAdmin):
    model = models.Reward
    list_display = ["reward_name", "point_cost", "display_discount", "reward_status", "date_added"]
    list_filter = ["reward_status"]
    change_form_template = 'admin/reward_form.html'

    @admin.display(description='Discount', ordering="discount_amount")
    def display_discount(self, obj):
        return "$" + str(round(obj.discount_amount, 2))

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            'Bakery/js/UpdateDiscountPrice.js',
        )


@admin.register(models.Customer)
class CustomerAdmin(TwentyPageAdmin):
    fields = (
        ('first_name', 'last_name'), "email_address", "birthdate", "phone_number",
        "customer_status", ("points_earned", "points_spent", "point_total"), "comments"
    )

    widgets = {
        'phone_number': forms.PhoneForm
    }
    list_filter = ["customer_status"]
    search_fields = ["email_address", "phone_number"]
    list_display = ["first_name", "last_name", "email_address", "display_phone", "customer_status",
                    "points_earned"]
    readonly_fields = ["points_earned", "points_spent", "point_total"]

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            'Bakery/js/Location.js',
            'Bakery/js/FormatPhone.js',
        )

    @admin.display(description='Phone Number', ordering="phone_number")
    def display_phone(self, obj):
        return format_phone(str(obj.phone_number))


@admin.register(models.Order)
class OrderAdmin(TwentyPageAdmin):
    fields = ("customer", "store",
              "points_produced", "points_consumed", "points_total",
              "original_total", "discount_amount", "eligible_for_points", "final_total")
    list_display = ["customer", "store", "order_date", "display_original_total"]
    readonly_fields = ["original_total", "discount_amount", "eligible_for_points",
                       "points_consumed", "points_produced", "points_total", "final_total"]
    inlines = [forms.OrderLineInline, forms.RewardLineForm]
    change_form_template = 'admin/order_change_form.html'
    raw_id_fields = ("customer",)
    list_filter = ["store"]

    @admin.display(description='Total', ordering="original_total")
    def display_original_total(self, obj):
        return "$" + str(round(obj.original_total, 2))

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            'Bakery/js/OrderChange.js',
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ["order_date", "customer", "store", "payment_type"] + self.readonly_fields
        return self.readonly_fields

    def get_inlines(self, request, obj):
        if obj:
            return [forms.OrderLineFormRead, forms.RewardLineFormRead]
        return self.inlines

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True

    def save_model(self, request, obj, form, change):
        points_added = models.PointLog(customer=obj.customer,
                                       reason_id=4, order=obj, points_amount=obj.points_produced)
        points_removed = models.PointLog(customer=obj.customer,
                                         reason_id=5, order=obj, points_amount=-obj.points_consumed)
        obj.save()
        points_added.save()
        points_removed.save()


@admin.register(models.Product)
class ProductAdmin(TwentyPageAdmin):
    list_filter = ["product_type", "product_status"]
    list_display = ["product_name", "product_type", "product_status", "display_product_price"]
    search_fields = ["product_name"]
    change_form_template = 'admin/product_form.html'

    @admin.display(description='Price', ordering="product_price")
    def display_product_price(self, obj):
        return "$" + str(round(obj.product_price, 2))

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            'Bakery/js/UpdateProductPrice.js',
        )

    form = forms.ProductForm


@admin.register(models.StoreReward)
class StoreRewardAdmin(TwentyPageAdmin):
    list_filter = ["store"]
    list_display = ["reward", "store", "reward_assigned"]


@admin.register(models.Store)
class StoreAdmin(TwentyPageAdmin):
    list_display = ["store_name", "store_status"]

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            'Bakery/js/Location.js',
            'Bakery/js/FormatPhone.js',
        )


@admin.register(models.PointLog)
class PointLogAdmin(TwentyPageAdmin):
    list_display = ["customer", "reason", "points_amount", "created_date"]
    list_filter = ["reason"]
    raw_id_fields = ["customer"]


# Register all the models for bakery that don't have a custom admin model
def register_models():
    basic_admin_models = [models.ProductType, models.ProductStatus, models.CustomerStatus,
                          models.RewardStatus, models.StoreStatus, models.BanType,
                          models.PointReason]
    for target_model in basic_admin_models:
        admin.site.register(target_model, TwentyPageAdmin)


register_models()

