# Generated by Django 4.0.6 on 2022-07-12 02:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.customfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('space', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Space',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('verbose_name', models.CharField(max_length=40, null=True)),
                ('icon', utils.customfields.ContentTypeRestrictedFileField(null=True, upload_to='space-icons/')),
                ('about', models.CharField(max_length=350, null=True)),
                ('tag_line', models.CharField(max_length=60, null=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'space',
                'verbose_name_plural': 'spaces',
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule', models.CharField(max_length=250)),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='space.space')),
            ],
            options={
                'verbose_name': 'space rule',
                'verbose_name_plural': 'space rules',
            },
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction', models.PositiveSmallIntegerField(choices=[(0, 'heart')])),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='space.message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Moderator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='space.space')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BanUserFromSpace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='space.space')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='space',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='space.space'),
            preserve_default=False,
        ),
    ]
