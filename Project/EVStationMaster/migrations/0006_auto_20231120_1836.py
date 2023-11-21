# Generated by Django 3.2.12 on 2023-11-20 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EVStationMaster', '0005_auto_20231120_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationdetails',
            name='Area',
            field=models.CharField(default='_', max_length=255),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='Paymodes',
            field=models.CharField(default='_', max_length=50),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='dayTime',
            field=models.CharField(default='_', max_length=50),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='loc1',
            field=models.CharField(default='_', max_length=255),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='loc2',
            field=models.CharField(default='_', max_length=255),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='loc3',
            field=models.CharField(default='_', max_length=255),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='loc4',
            field=models.CharField(default='_', max_length=255),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='loc5',
            field=models.CharField(default='_', max_length=255),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='loc6',
            field=models.CharField(default='_', max_length=255),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='state',
            field=models.CharField(default='_', max_length=255),
        ),
        migrations.AlterField(
            model_name='stationdetails',
            name='vehicleTypes',
            field=models.CharField(default='_', max_length=255),
        ),
    ]