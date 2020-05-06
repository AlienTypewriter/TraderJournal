# Generated by Django 3.0.5 on 2020-05-05 11:37

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trader_journal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('init_deposit', models.DecimalField(decimal_places=4, max_digits=12)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='operation',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 5, 5, 11, 37, 11, 529970, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='operation',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='period',
            name='date_start',
            field=models.DateField(default=datetime.datetime(2020, 5, 5, 11, 37, 11, 531970, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='period',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Trader',
        ),
    ]