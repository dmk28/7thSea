# Generated by Django 4.2.14 on 2024-08-20 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "character_sheet",
            "0026_charactersheet_eye_color_charactersheet_hair_color_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="swordsmanschool",
            name="country",
            field=models.JSONField(default=list),
        ),
    ]
