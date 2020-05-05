# Generated by Django 3.0.5 on 2020-05-05 11:08

import datetime
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Trader',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('init_deposit', models.DecimalField(decimal_places=4, max_digits=12)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField(default=datetime.datetime(2020, 5, 5, 11, 8, 17, 341121, tzinfo=utc))),
                ('date_end', models.DateField()),
                ('max_acts', models.PositiveSmallIntegerField()),
                ('acts_window', models.CharField(choices=[('D', 'Day'), ('W', 'Week'), ('M', 'Month')], default='D', max_length=1)),
                ('max_freq', models.PositiveSmallIntegerField()),
                ('max_simultaneous', models.PositiveSmallIntegerField()),
                ('use_shoulder', models.BooleanField(default=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trader_journal.Trader')),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime(2020, 5, 5, 11, 8, 17, 339120, tzinfo=utc))),
                ('currency', models.CharField(max_length=5)),
                ('amount', models.DecimalField(decimal_places=8, max_digits=16)),
                ('current_price', models.DecimalField(decimal_places=4, max_digits=9)),
                ('eventual_price', models.DecimalField(decimal_places=4, default=None, max_digits=9, null=True)),
                ('is_buy', models.BooleanField()),
                ('is_maker', models.BooleanField()),
                ('is_open', models.BooleanField(default=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trader_journal.Trader')),
            ],
        ),
        migrations.CreateModel(
            name='Active',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=5)),
                ('amount', models.DecimalField(decimal_places=8, max_digits=16)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
