# Generated by Django 2.2.4 on 2019-08-26 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('number', models.CharField(max_length=30)),
                ('chip_id', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('INI', 'Inicial'), ('ERR', 'Error'), ('CON', 'Conectado'), ('NO_CON', 'Desconectado')], default='INI', max_length=10)),
                ('chip_status', models.CharField(choices=[('FREE', 'Libre'), ('CALL', 'Llamando'), ('IN_CAL', 'En llamada'), ('ERR', 'Error')], default='FREE', max_length=10)),
                ('index_sms', models.IntegerField(default=1)),
                ('channel_i2c', models.CharField(max_length=10)),
                ('last_connection', models.DateTimeField(null=True)),
                ('enabled', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('INI', 'Inicial'), ('PRO', 'Procesando'), ('OK', 'Ok'), ('ERR', 'Error'), ('CAN', 'Cancelada')], default='INI', max_length=10)),
                ('log_type', models.CharField(choices=[('ERR', 'Error'), ('STATUS', 'Estado'), ('CALL', 'CALL'), ('CALL', 'IN_CALL'), ('NEWSMS', 'NEWSMS'), ('SMS', 'SMS')], max_length=10)),
                ('number', models.CharField(max_length=100, null=True)),
                ('description', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='devices.Device')),
            ],
        ),
        migrations.CreateModel(
            name='LogAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('INI', 'Inicial'), ('PRO', 'Procesando'), ('OK', 'Ok'), ('ERR', 'Error'), ('CAN', 'Cancelada')], default='INI', max_length=10)),
                ('origin', models.CharField(choices=[('API', 'Api'), ('RULE', 'Rule'), ('DEV', 'Device')], max_length=10)),
                ('log_type', models.CharField(choices=[('CALL', 'Llamar'), ('ANSW', 'Atender'), ('HOFF', 'Cortar'), ('SMS', 'Enviar SMS'), ('RSMS', 'Leer SMS'), ('DSMS', 'Eliminar SMSs'), ('INFO', 'Informacion'), ('STATUS', 'Estado')], max_length=10)),
                ('number', models.CharField(max_length=100, null=True)),
                ('description', models.TextField(null=True)),
                ('response', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='devices.Device')),
            ],
        ),
    ]
