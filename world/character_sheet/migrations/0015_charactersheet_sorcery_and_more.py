# Generated by Django 4.2.14 on 2024-08-19 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character_sheet", "0014_alter_sorcery_options_alter_swordsmanschool_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="charactersheet",
            name="sorcery",
            field=models.ManyToManyField(blank=True, to="character_sheet.sorcery"),
        ),
        migrations.AddField(
            model_name="charactersheet",
            name="swordsman_school",
            field=models.ManyToManyField(
                blank=True, to="character_sheet.swordsmanschool"
            ),
        ),
    ]
