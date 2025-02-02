# Generated by Django 4.2.11 on 2024-03-11 07:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='room_model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.IntegerField(unique=True)),
                ('user1_score', models.IntegerField(default=0)),
                ('user2_score', models.IntegerField(default=0)),
                ('tie_score', models.IntegerField(default=0, null=True)),
                ('moves', models.IntegerField(default=10)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1_model', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2_model', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
