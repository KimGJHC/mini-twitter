# Generated by Django 3.1.3 on 2022-10-13 00:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsfeeds', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='newsfeed',
            options={'ordering': ('-created_at',)},
        ),
    ]