# Generated by Django 3.2.12 on 2023-11-25 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EVStationMaster', '0008_slotbooking'),
    ]

    operations = [
        migrations.RenameField(
            model_name='slotbooking',
            old_name='stationID',
            new_name='stationId',
        ),
    ]
