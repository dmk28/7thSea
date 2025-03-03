# Generated by Django 4.2.14 on 2024-08-17 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AdventuringGuild",
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
                ("name", models.CharField(default="", max_length=150)),
                ("founder", models.CharField(default="", max_length=100)),
                ("founding_date", models.PositiveIntegerField(default=1665)),
                (
                    "history",
                    models.TextField(blank=True, verbose_name="Founding History"),
                ),
                (
                    "recent_history",
                    models.TextField(blank=True, verbose_name="Recent History"),
                ),
                ("Members", models.JSONField()),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
