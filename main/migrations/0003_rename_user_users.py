# Generated by Django 4.2.3 on 2023-08-17 18:08

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0002_rename_fullname_user_name_user_user"),
    ]

    operations = [
        migrations.RenameModel(old_name="User", new_name="Users",),
    ]