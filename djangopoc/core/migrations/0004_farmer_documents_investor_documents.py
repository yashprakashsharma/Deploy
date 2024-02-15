# Generated by Django 5.0 on 2024-01-03 09:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_wallet_farmer_wallet_investor_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmer',
            name='documents',
            field=models.FileField(default=None, null=True, upload_to='farmer_documents/', validators=[django.core.validators.FileExtensionValidator(['pdf'])]),
        ),
        migrations.AddField(
            model_name='investor',
            name='documents',
            field=models.FileField(default=None, null=True, upload_to='investor_documents/', validators=[django.core.validators.FileExtensionValidator(['pdf'])]),
        ),
    ]