# Generated by Django 4.0.6 on 2022-07-23 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_blacklistedip_ip_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='tag_line',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
    ]
