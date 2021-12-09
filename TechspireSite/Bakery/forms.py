from decimal import Decimal
import math
from django.db.models import Sum
from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.core import validators
from phonenumber_field.formfields import PhoneNumberField
from .models import OrderLine, Product, Reward, OrderReward, Customer


class LocationForm(forms.ModelForm):
    test_field = forms.CharField(label='Your name', max_length=100)


class GenericForm(forms.ModelForm):
    your_name = forms.CharField(label='Your name', max_length=100, disabled=True)


class ProductForm(forms.ModelForm):
    model = Product
    pass


class OrderFormSet(BaseInlineFormSet):
    def clean(self):
        super(OrderFormSet, self).clean()
        total = Decimal(0)
        eligible = Decimal(0)
        for form in self.forms:
            if form.is_valid():
                try:
                    current_product = Product.objects.get(pk=form.cleaned_data["product"].id)
                    ind_price = current_product.product_price
                    line_total = ind_price * Decimal(form.cleaned_data["quantity"])
                    total += line_total
                    if not current_product.ban_reason:
                        eligible += line_total
                except KeyError:
                    pass

        self.instance.original_total = total
        self.instance.final_total = total
        self.instance.eligible_for_points = eligible
        self.instance.points_produced = math.floor(eligible/5)


class RewardFormSet(BaseInlineFormSet):
    def clean(self):
        super(RewardFormSet, self).clean()
        try:
            discount = Decimal(0)
            consumed_points = 0
            for form in self.forms:
                if form.is_valid():
                    try:
                        current_reward = Reward.objects.get(pk=form.cleaned_data["reward"].id)
                        discount += current_reward.discount_amount
                        consumed_points += current_reward.point_cost
                    except KeyError:
                        pass

            self.instance.points_consumed = consumed_points
            self.instance.discount_amount = discount
            self.instance.points_total = self.instance.points_produced - consumed_points
            self.instance.final_total -= discount
            self.instance.eligible_for_points -= discount
            modified_points = self.instance.customer.pointlog_set.all().aggregate(Sum('points_amount'))[
                "points_amount__sum"]
            modified_points += self.instance.points_total
            if modified_points < 0:
                raise validators.ValidationError("Customer needs {} more points to complete this transaction"
                                                 .format(str(-modified_points)))
        except Customer.DoesNotExist:
            #if customer doesn't exist don't bother
            pass


class OrderLineInline(admin.TabularInline):
    formset = OrderFormSet
    model = OrderLine
    min_num = 0
    extra = 1

    fields = ["product", "ind_price", "quantity", "total_price", "points_eligible"]
    readonly_fields = ["ind_price", "total_price", "points_eligible"]


class RewardLineForm(admin.TabularInline):
    formset = RewardFormSet
    model = OrderReward
    min_num = 0
    max_num = 1
    extra = 0
    can_delete = True
    fields = ["reward", "point_cost", "discount_amount", "free_product"]
    readonly_fields = ["point_cost", "discount_amount", "free_product"]


class RewardLineFormRead(RewardLineForm):
    def get_readonly_fields(self, request, obj=None):
        return self.fields + self.readonly_fields

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return False

    min_num = 0


class OrderLineFormRead(OrderLineInline):
    def get_readonly_fields(self, request, obj=None):
        return self.fields + self.readonly_fields

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return False

    extra = 0


class PhoneForm(forms.Form):
    phone = PhoneNumberField()

