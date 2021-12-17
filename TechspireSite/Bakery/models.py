from django.db import models
from django import forms
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db.models import Sum
import os
from django.db import connection
from. import bulk_insert


def past_validator(value):
    if value > timezone.now().date():
        raise forms.ValidationError("The date must be in the past!")
    return value


class MoneyField(models.DecimalField):
    def __init__(self):
        super().__init__(max_digits=19, decimal_places=4, default=0)

    def __str__(self):
        return "$" + super.__str__(self)
    widget = forms.Textarea


class DescriptiveModel(models.Model):
    id = models.AutoField(primary_key=True)
    description = "Blank Description"
    pk_desc = "Standard Auto-Increment PK"

    class Meta:
        abstract = True
        

# Used as an abstract parent for status codes
class StatusCode(DescriptiveModel):
    description = "Used to soft delete rows with a reason name and desc"
    status_name = models.CharField(max_length=40)
    status_desc = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    category = "Other"

    def __str__(self):
        return self.status_name

    class Meta:
        abstract = True
        

# Used as an abstract parent for labels
class LabelCode(DescriptiveModel):
    description = "Allows for multiple named categories"
    type_name = models.CharField(max_length=40)
    type_desc = models.CharField(max_length=200, blank=True, null=True)
    category = "Other"

    def __str__(self):
        return self.type_name

    class Meta:
        abstract = True


class CustomerStatus(StatusCode):
    description = 'Describes the current relationship between the ' \
                  'customer and the business (are they an ' \
                  'Active customer? are they an inactive customer?)'

    class Meta:
        db_table = "CustomerStatus"
        verbose_name_plural = "Customer Status"
        

class ProductStatus(StatusCode):
    description = 'Refers to whether a product is available or not. ' \
                  'Not that it is unavailable but also if it is not offered anymore'

    class Meta:
        db_table = "ProductStatus"
        verbose_name_plural = "Product Status"


class StoreStatus(StatusCode):
    description = 'Soft delete of store.'

    class Meta:
        db_table = "StoreStatus"
        verbose_name_plural = "Store Status"
        

class RewardStatus(StatusCode):
    description = 'Defines whether a particular reward is active/inactive. Core attributes: active, inactive'

    class Meta:
        db_table = "RewardStatus"
        verbose_name_plural = "Reward Status"
        

class BanType(DescriptiveModel):
    description = "Describes why a specific product that is banned"
    ban_name = models.CharField(max_length=40)
    ban_desc = models.CharField(max_length=200, blank=True, null=True)
    category = "Other"

    class Meta:
        db_table = "BanType"
        verbose_name_plural = "Ban Type"

    def __str__(self):
        return self.ban_name


class PointReason(DescriptiveModel):
    description = "Describes why points were added or removed"
    reason_name = models.CharField(max_length=40)
    reason_desc = models.CharField(max_length=200, blank=True, null=True)
    category = "Other"

    class Meta:
        db_table = "PointReason"
        verbose_name_plural = "Point Log Type"

    def __str__(self):
        return self.reason_name


# Used as an abstract parent for people
class Person(DescriptiveModel):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email_address = models.EmailField(max_length=254)
    phone_number = PhoneNumberField(max_length=15, help_text="xxx-xxx-xxxx", default="+19043335252")
    birthdate = models.DateField(validators=[past_validator])
    begin_date = models.DateField(auto_now_add=True, help_text="YYYY-MM-DD")
    comments = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.first_name + " " + self.last_name


class Customer(Person):
    description = 'Someone who potentially purchases an item/service ' \
                  'from our client and whose general information has been collected by our loyalty system database.'
    customer_status = models.ForeignKey(CustomerStatus, on_delete=models.RESTRICT)
    points_earned = models.IntegerField(default=0)
    points_spent = models.IntegerField(default=0)
    point_total = models.IntegerField(default=0)
    category = "Cashier"

    class Meta:
        db_table = "Customer"
        verbose_name_plural = "Loyalty Customer"
        

class Store(DescriptiveModel):
    description = 'A physical location where customers go to complete transactions.'
    store_name = models.CharField(max_length=40)
    store_status = models.ForeignKey(StoreStatus, on_delete=models.RESTRICT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    category = "Core"

    class Meta:
        db_table = "Store"
        verbose_name_plural = "Store"

    def __str__(self):
        return self.store_name


class Order(DescriptiveModel):
    description = 'The customer’s finalized transaction of products purchased. ' \
                  'This order generates customer loyalty points based on the monetary total of the transaction.'
    order_date = models.DateField(auto_now_add=True)
    original_total = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    final_total = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    discount_amount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    eligible_for_points = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    points_consumed = models.IntegerField(default=0)
    points_produced = models.IntegerField(default=0)
    points_total = models.IntegerField(default=0)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    store = models.ForeignKey(Store, on_delete=models.RESTRICT)
    category = "Cashier"

    class Meta:
        db_table = "Order"
        verbose_name_plural = "Order/Transaction"

    def __str__(self):
        return str(self.store) + "-" + str(self.customer) + "-" + str(self.order_date)

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        update_customer_points(self.customer.id)
        #bulk_insert.run_sql("CalculateCustomerPointsSingle.sql", [self.customer.id])


class ProductType(DescriptiveModel):
    description = 'Identifying certain product types that are eligible ' \
                  'to be purchased with points, versus products ' \
                  'that are not eligible to earn points on; used to distinguish exclusions. '
    product_type_name = models.CharField(max_length=40)
    product_type_desc = models.CharField(max_length=200, blank=True, null=True)
    category = "Other"

    class Meta:
        db_table = "ProductType"
        verbose_name_plural = "Product Type"

    def __str__(self):
        return self.product_type_name


class Product(DescriptiveModel):
    description = 'An item purchased by the customer in a transaction.'
    product_name = models.CharField(max_length=80)
    product_desc = models.CharField(max_length=200, blank=True, null=True)
    product_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    product_status = models.ForeignKey(ProductStatus, on_delete=models.RESTRICT)
    ban_reason = models.ForeignKey(BanType, on_delete=models.SET_NULL, blank=True, null=True)
    category = "Core"

    class Meta:
        db_table = "Product"
        verbose_name_plural = "Product"

    def __str__(self):
        return self.product_name


class OrderLine(DescriptiveModel):
    description = 'Represents information located on a ' \
                  'singular line found on a receipt/invoice ' \
                  'produced after a completed transaction ' \
                  'that describes the customer’s transaction ' \
                  'and product details (quantity, product type, ' \
                  'total price for that order line).'
    quantity = models.IntegerField(default=1)
    ind_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    total_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    order = models.ForeignKey(Order, on_delete=models.RESTRICT)
    points_eligible = models.BooleanField(default=True)

    class Meta:
        db_table = "OrderLine"
        verbose_name = "Order Line"
        verbose_name_plural = verbose_name
        
        constraints = [models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product'),
                       models.CheckConstraint(check=models.Q(quantity__gt=0), name='quantity_gt_0')]

    def save(self, *args, **kwargs):
        target_product = Product.objects.get(pk=self.product.id)
        self.ind_price = target_product.product_price
        self.total_price = self.ind_price * self.quantity
        self.points_eligible = target_product.ban_reason is None
        super(OrderLine, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.order) + " " + str(self.product)


class Reward(DescriptiveModel):
    description = 'All benefits that are offered by the business ' \
                  'for being an active loyalty customer that can be ' \
                  'claimed by converting some of their earned points. ' \
                  '“Rewards” can be coupons ($5 off) or birthday reward ' \
                  '(does not need point conversion, it’s just a redemption code for a freebie)'
    reward_name = models.CharField(max_length=80)
    reward_desc = models.CharField(max_length=200, blank=True, null=True)
    reward_status = models.ForeignKey(RewardStatus, on_delete=models.RESTRICT)
    point_cost = models.IntegerField(default=0)
    reset_period = models.IntegerField(default=0, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    free_product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    date_disabled = models.DateField(blank=True, null=True)
    category = "Core"

    class Meta:
        db_table = "Reward"
        verbose_name_plural = "Reward"

    def __str__(self):
        return self.reward_name


class StoreProduct(DescriptiveModel):
    description = 'Products that are either associated with or are offered at a specific store location.'
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    store = models.ForeignKey(Store, on_delete=models.RESTRICT)
    product_assigned = models.DateField(auto_now_add=True)
    category = "Core"

    class Meta:
        db_table = "StoreProduct"
        verbose_name = "StoreProduct/Menu"
        verbose_name_plural = verbose_name
        
        constraints = [models.UniqueConstraint(fields=['product', 'store'], name='unique_store_product')]

    def __str__(self):
        return str(self.store) + " " + str(self.product)


class StoreReward(DescriptiveModel):
    description = 'Rewards available to loyalty customers based on which specific store points are redeemed at.'
    reward = models.ForeignKey(Reward, on_delete=models.RESTRICT)
    store = models.ForeignKey(Store, on_delete=models.RESTRICT)
    reward_assigned = models.DateField(auto_now_add=True)
    category = "Core"

    class Meta:
        db_table = "StoreReward"
        verbose_name = "Store Reward"
        verbose_name_plural = verbose_name
        
        constraints = [models.UniqueConstraint(fields=['reward', 'store'], name='unique_store_reward')]

    def __str__(self):
        return str(self.store) + " " + str(self.reward)


class OrderReward(DescriptiveModel):
    description = "Effectively the reward equivalent to OrderLine for transactions."
    order = models.ForeignKey(Order, on_delete=models.RESTRICT)
    reward = models.ForeignKey(Reward, on_delete=models.RESTRICT)
    point_cost = models.IntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    free_product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "OrderReward"
        verbose_name = "Customer Reward"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        target_reward = Reward.objects.get(pk=self.reward.id)
        self.free_product = target_reward.free_product
        self.discount_amount = target_reward.discount_amount
        self.point_cost = target_reward.point_cost
        super(OrderReward, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.order) + " " + str(self.reward)


class PointLog(DescriptiveModel):
    description = "Describes all point transactions for a customer in a single table."
    points_amount = models.IntegerField(default=0)
    created_date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    reason = models.ForeignKey(PointReason, on_delete=models.RESTRICT)
    category = "Core"

    class Meta:
        db_table = "PointLog"
        verbose_name = "Point Log"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.customer) + " " + str(self.reason) + " " + str(self.created_date)

    def save(self, *args, **kwargs):
        super(PointLog, self).save(*args, **kwargs)
        update_customer_points(self.customer.id)
        #bulk_insert.run_sql("CalculateCustomerPointsSingle.sql", [self.customer.id])


def update_customer_points(customer_id):
    target_customer = Customer.objects.get(id=customer_id)
    pos_log = \
    PointLog.objects.filter(customer__id=customer_id).filter(points_amount__gt=0).aggregate(Sum("points_amount"))[
        "points_amount__sum"]
    neg_log = \
    PointLog.objects.filter(customer__id=customer_id).filter(points_amount__lt=0).aggregate(Sum("points_amount"))[
        "points_amount__sum"]
    order_totals = Order.objects.filter(customer__id=customer_id).aggregate(Sum("points_produced"),
                                                                                 Sum("points_consumed"))
    pos_order = order_totals["points_produced__sum"]
    neg_order = order_totals["points_consumed__sum"]
    pos_log = 0 if pos_log is None else pos_log
    neg_log = 0 if neg_log is None else neg_log
    pos_order = 0 if pos_order is None else pos_order
    neg_order = 0 if neg_order is None else neg_order
    target_customer.points_earned = pos_log + pos_order
    target_customer.points_spent = neg_order - neg_log
    target_customer.point_total = (pos_log + pos_order) - neg_order - neg_log
    target_customer.save()