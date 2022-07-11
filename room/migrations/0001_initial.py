# Generated by Django 4.0.6 on 2022-07-11 16:05

from django.db import migrations, models
import utils.customfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(max_length=2500, null=True)),
                ('media', utils.customfields.ContentTypeRestrictedFileField(null=True, upload_to='chat-media/')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
            },
        ),
    ]
