# Generated by Django 5.1 on 2024-10-28 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auction_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auction',
            old_name='reserve_price',
            new_name='bid_price',
        ),
    ]
