# Generated by Django 4.2.14 on 2024-08-19 01:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "character_sheet",
            "0013_remove_skill_knacks_knack_skill_alter_knack_name_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sorcery",
            options={"verbose_name": "Sorcery", "verbose_name_plural": "Sorceries"},
        ),
        migrations.AlterModelOptions(
            name="swordsmanschool",
            options={
                "verbose_name": "Swordsman School",
                "verbose_name_plural": "Swordsman Schools",
            },
        ),
    ]
