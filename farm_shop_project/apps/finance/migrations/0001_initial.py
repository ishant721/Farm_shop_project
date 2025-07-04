# Generated by Django 5.2.3 on 2025-06-13 11:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FarmerBill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, help_text="Optional description for the bill (e.g., 'Produce purchase for May')")),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('due_date', models.DateField()),
                ('is_approved', models.BooleanField(default=False, help_text='True if the bill has been approved by an admin.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bills_created', to=settings.AUTH_USER_MODEL)),
                ('farmer', models.ForeignKey(limit_choices_to={'user_type': 'farmer'}, on_delete=django.db.models.deletion.CASCADE, related_name='bills', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Farmer Bill',
                'verbose_name_plural': 'Farmer Bills',
                'ordering': ['-created_at'],
                'permissions': [('can_create_farmer_bill', 'Can create a farmer bill (requires admin approval)'), ('can_approve_farmer_bill', 'Can approve a farmer bill'), ('can_send_payment_reminders', 'Can send payment reminders to farmers'), ('can_view_all_bills', 'Can view all farmer bills (not just own/pending)')],
            },
        ),
    ]
