# Generated by Django 4.2.14 on 2024-08-20 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character_sheet", "0025_remove_advantage_eisen_cost_alter_advantage_cost"),
    ]

    operations = [
        migrations.AddField(
            model_name="charactersheet",
            name="eye_color",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="charactersheet",
            name="hair_color",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="charactersheet",
            name="skin_hue",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
