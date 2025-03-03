# Generated by Django 4.2.14 on 2024-08-23 19:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("objects", "0015_clothing_heavysword"),
    ]

    operations = [
        migrations.CreateModel(
            name="WeaponModel",
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
                ("name", models.CharField(blank=True, max_length=50)),
                ("description", models.TextField(blank=True)),
                ("damage", models.PositiveIntegerField(default=1)),
                ("roll_keep", models.PositiveIntegerField(default=1)),
                (
                    "weapon_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("fencing", "Fencing"),
                            ("heavy weapon", "Heavy Weapon"),
                            ("pugilism", "Pugilism"),
                            ("firearms", "Firearm"),
                            ("polearms", "Polearm"),
                            ("knives", "Knife"),
                            ("swordcane", "Swordcane"),
                            ("fencingandknife", "Fencing/Knife"),
                        ],
                        max_length=30,
                        null=True,
                    ),
                ),
                ("flameblade_active", models.BooleanField(default=False)),
                (
                    "attack_skill",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("attack (fencing)", "Attack (Fencing)"),
                            ("attack (knife)", "Attack (Knife)"),
                            ("attack (heavy weapon)", "Attack (Heavy Weapon)"),
                            (
                                "attack (improvised weapon)",
                                "Attack (Improvised Weapon)",
                            ),
                            ("attack (polearms)", "Attack (Polearms)"),
                            ("attack (whip)", "Attack (Whip)"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "parry_skill",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("parry (fencing)", "Parry (Fencing)"),
                            ("parry (knife)", "Parry (Knife)"),
                            ("parry (heavy weapon)", "Parry (Heavy Weapon)"),
                            ("parry (improvised weapon)", "`Parry (Improvised Weapon)"),
                            ("parry (polearms)", "Parry (Polearms)"),
                            ("footwork", "Footwork"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("damage_bonus", models.PositiveIntegerField(default=0)),
                ("cost", models.IntegerField(default=0)),
                ("requirements", models.JSONField(blank=True, default=dict)),
                ("weight", models.FloatField(default=0)),
                (
                    "evennia_object",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="weapon_model",
                        to="objects.objectdb",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
