# Generated by Django 3.2.8 on 2021-12-12 02:30

import Bakery.models
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BanType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ban_name', models.CharField(max_length=40)),
                ('ban_desc', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'Ban Type',
                'db_table': 'BanType',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=40)),
                ('last_name', models.CharField(max_length=40)),
                ('email_address', models.EmailField(max_length=254)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(default='+19043335252', help_text='xxx-xxx-xxxx', max_length=15, region=None)),
                ('birthdate', models.DateField(validators=[Bakery.models.past_validator])),
                ('begin_date', models.DateField(auto_now_add=True, help_text='YYYY-MM-DD')),
                ('comments', models.TextField(blank=True, null=True)),
                ('points_earned', models.IntegerField(default=0)),
                ('points_spent', models.IntegerField(default=0)),
                ('point_total', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Loyalty Customer',
                'db_table': 'Customer',
            },
        ),
        migrations.CreateModel(
            name='CustomerStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status_name', models.CharField(max_length=40)),
                ('status_desc', models.CharField(blank=True, max_length=200, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Customer Status',
                'db_table': 'CustomerStatus',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order_date', models.DateField(auto_now_add=True)),
                ('original_total', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('final_total', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('discount_amount', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('eligible_for_points', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('points_consumed', models.IntegerField(default=0)),
                ('points_produced', models.IntegerField(default=0)),
                ('points_total', models.IntegerField(default=0)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.customer')),
            ],
            options={
                'verbose_name_plural': 'Order/Transaction',
                'db_table': 'Order',
            },
        ),
        migrations.CreateModel(
            name='PointReason',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('reason_name', models.CharField(max_length=40)),
                ('reason_desc', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'Point Log Type',
                'db_table': 'PointReason',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=80)),
                ('product_desc', models.CharField(blank=True, max_length=200, null=True)),
                ('product_price', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('ban_reason', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Bakery.bantype')),
            ],
            options={
                'verbose_name_plural': 'Product',
                'db_table': 'Product',
            },
        ),
        migrations.CreateModel(
            name='ProductStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status_name', models.CharField(max_length=40)),
                ('status_desc', models.CharField(blank=True, max_length=200, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Product Status',
                'db_table': 'ProductStatus',
            },
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_type_name', models.CharField(max_length=40)),
                ('product_type_desc', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'Product Type',
                'db_table': 'ProductType',
            },
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('reward_name', models.CharField(max_length=80)),
                ('reward_desc', models.CharField(blank=True, max_length=200, null=True)),
                ('point_cost', models.IntegerField(default=0)),
                ('reset_period', models.IntegerField(blank=True, default=0, null=True)),
                ('discount_amount', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('date_disabled', models.DateField(blank=True, null=True)),
                ('free_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Bakery.product')),
            ],
            options={
                'verbose_name_plural': 'Reward',
                'db_table': 'Reward',
            },
        ),
        migrations.CreateModel(
            name='RewardStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status_name', models.CharField(max_length=40)),
                ('status_desc', models.CharField(blank=True, max_length=200, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Reward Status',
                'db_table': 'RewardStatus',
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('store_name', models.CharField(max_length=40)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Store',
                'db_table': 'Store',
            },
        ),
        migrations.CreateModel(
            name='StoreStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status_name', models.CharField(max_length=40)),
                ('status_desc', models.CharField(blank=True, max_length=200, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Store Status',
                'db_table': 'StoreStatus',
            },
        ),
        migrations.CreateModel(
            name='StoreReward',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('reward_assigned', models.DateField(auto_now_add=True)),
                ('reward', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.reward')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.store')),
            ],
            options={
                'verbose_name': 'Store Reward',
                'verbose_name_plural': 'Store Reward',
                'db_table': 'StoreReward',
            },
        ),
        migrations.CreateModel(
            name='StoreProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_assigned', models.DateField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.store')),
            ],
            options={
                'verbose_name': 'StoreProduct/Menu',
                'verbose_name_plural': 'StoreProduct/Menu',
                'db_table': 'StoreProduct',
            },
        ),
        migrations.AddField(
            model_name='store',
            name='store_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.storestatus'),
        ),
        migrations.AddField(
            model_name='reward',
            name='reward_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.rewardstatus'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.productstatus'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.producttype'),
        ),
        migrations.CreateModel(
            name='PointLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('points_amount', models.IntegerField(default=0)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.customer')),
                ('reason', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.pointreason')),
            ],
            options={
                'verbose_name': 'Point Log',
                'verbose_name_plural': 'Point Log',
                'db_table': 'PointLog',
            },
        ),
        migrations.CreateModel(
            name='OrderReward',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('point_cost', models.IntegerField(default=0)),
                ('discount_amount', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('free_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Bakery.product')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.order')),
                ('reward', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.reward')),
            ],
            options={
                'verbose_name': 'Customer Reward',
                'verbose_name_plural': 'Customer Reward',
                'db_table': 'OrderReward',
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=0)),
                ('ind_price', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('total_price', models.DecimalField(decimal_places=4, default=0, max_digits=19)),
                ('points_eligible', models.BooleanField(default=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.product')),
            ],
            options={
                'verbose_name': 'Order Line',
                'verbose_name_plural': 'Order Line',
                'db_table': 'OrderLine',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.store'),
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Bakery.customerstatus'),
        ),
        migrations.AddConstraint(
            model_name='storereward',
            constraint=models.UniqueConstraint(fields=('reward', 'store'), name='unique_store_reward'),
        ),
        migrations.AddConstraint(
            model_name='storeproduct',
            constraint=models.UniqueConstraint(fields=('product', 'store'), name='unique_store_product'),
        ),
        migrations.AddConstraint(
            model_name='orderline',
            constraint=models.UniqueConstraint(fields=('order', 'product'), name='unique_order_product'),
        ),
    ]
