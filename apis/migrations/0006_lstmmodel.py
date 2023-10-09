# Generated by Django 4.2.3 on 2023-10-08 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("apis", "0005_linearregressionmodel_dates"),
    ]

    operations = [
        migrations.CreateModel(
            name="LSTMModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("dates", models.JSONField(blank=True, null=True)),
                ("prices", models.JSONField(blank=True, null=True)),
                (
                    "ticker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="apis.tickers"
                    ),
                ),
            ],
        ),
    ]