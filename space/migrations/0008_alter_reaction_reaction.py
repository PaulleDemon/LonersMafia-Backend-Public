# Generated by Django 4.0.6 on 2022-07-22 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('space', '0007_moderator_datetime_alter_space_tag_line'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reaction',
            name='reaction',
            field=models.CharField(max_length=10),
        ),
    ]