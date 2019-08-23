# Generated by Django 2.2.4 on 2019-08-23 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='chip_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='chip_status',
            field=models.CharField(choices=[('FREE', 'Libre'), ('CALL', 'Llamando'), ('IN_CAL', 'En llamada'), ('ERR', 'Error')], default='FREE', max_length=10),
        ),
    ]
