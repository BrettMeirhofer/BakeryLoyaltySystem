from django.db.models.signals import post_save, post_delete
from .models import PointLog, Order, Customer
from django.dispatch import receiver
from django.db.models import Sum


@receiver(post_save, sender=PointLog)
def point_log_saved(sender, instance, created, **kwargs):
    update_customer_points(instance.customer.id)


@receiver(post_save, sender=Order)
def order_saved(sender, instance, created, **kwargs):
    update_customer_points(instance.customer.id)


@receiver(post_delete, sender=PointLog)
def point_log_deleted(sender, instance, **kwargs):
    update_customer_points(instance.customer.id)


@receiver(post_delete, sender=Order)
def order_deleted(sender, instance, **kwargs):
    update_customer_points(instance.customer.id)


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
    target_customer.point_total = (pos_log + pos_order) - (neg_order - neg_log)
    target_customer.save()