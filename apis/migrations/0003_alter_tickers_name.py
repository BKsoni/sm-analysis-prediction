# Generated by Django 4.2.3 on 2023-10-07 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apis", "0002_alter_tickers_ticker"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tickers",
            name="name",
            field=models.CharField(default="", max_length=100),
        ),
    ]
