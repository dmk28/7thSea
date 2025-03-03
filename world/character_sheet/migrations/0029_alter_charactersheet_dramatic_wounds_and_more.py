# Generated by Django 4.2.14 on 2024-08-21 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character_sheet", "0028_charactersheet_special_effects"),
    ]

    operations = [
        migrations.AlterField(
            model_name="charactersheet",
            name="dramatic_wounds",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="charactersheet",
            name="flesh_wounds",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
