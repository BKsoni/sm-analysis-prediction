# Generated by Django 4.2.3 on 2023-10-07 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apis", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tickers", name="ticker", field=models.CharField(max_length=100),
        ),
    ]
