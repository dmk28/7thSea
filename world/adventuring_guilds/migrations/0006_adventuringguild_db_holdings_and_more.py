# Generated by Django 4.2.14 on 2024-08-17 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("objects", "0015_clothing_heavysword"),
        ("adventuring_guilds", "0005_alter_adventuringguild_db_founder"),
    ]

    operations = [
        migrations.AddField(
            model_name="adventuringguild",
            name="db_holdings",
            field=models.ManyToManyField(
                blank=True, related_name="owned_by_guild", to="objects.objectdb"
            ),
        ),
        migrations.AddField(
            model_name="adventuringguild",
            name="db_treasury_doubloons",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="adventuringguild",
            name="db_treasury_guilders",
            field=models.IntegerField(default=0),
        ),
    ]
