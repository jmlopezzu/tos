# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tos_web.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('firstname', models.CharField(max_length=64)),
                ('lastname', models.CharField(max_length=64)),
                ('email', models.EmailField(unique=True, max_length=255)),
                ('is_active', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('acceptance', models.BooleanField(default=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('modified', models.DateField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('email', models.EmailField(max_length=254)),
                ('count', models.PositiveIntegerField(default=1)),
                ('state', models.CharField(max_length=10, choices=[('AC', 'Active'), ('PD', 'Pending'), ('TOS', 'Inside')])),
                ('created', models.DateField(auto_now_add=True)),
                ('modified', models.DateField(auto_now_add=True)),
                ('inviter', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='invitations')),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('filename', models.TextField(max_length=64)),
                ('raw_data', models.FileField(upload_to=tos_web.models.Query.rename_file)),
                ('description', models.TextField()),
                ('tree', models.BinaryField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='queries')),
            ],
        ),
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('token', models.SlugField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together=set([('inviter', 'email')]),
        ),
    ]
