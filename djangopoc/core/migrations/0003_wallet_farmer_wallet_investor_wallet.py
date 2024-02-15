# Generated by Django 5.0 on 2023-12-24 11:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_farmer_investor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField(default=0.0)),
            ],
        ),
        migrations.AddField(
            model_name='farmer',
            name='wallet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wallet_farmer', to='core.wallet'),
        ),
        migrations.AddField(
            model_name='investor',
            name='wallet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wallet_investor', to='core.wallet'),
        ),
    ]