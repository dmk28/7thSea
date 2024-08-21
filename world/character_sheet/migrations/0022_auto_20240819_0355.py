from django.db import migrations

def assign_default_skill_to_knacks(apps, schema_editor):
    Knack = apps.get_model('character_sheet', 'Knack')
    Skill = apps.get_model('character_sheet', 'Skill')
    
    default_skill, _ = Skill.objects.get_or_create(name='General', category='Misc')
    
    for knack in Knack.objects.filter(skill__isnull=True):
        knack.skill = default_skill
        knack.save()

class Migration(migrations.Migration):

    dependencies = [
        ('character_sheet', '0021_remove_charactersheet_sorcery_and_more'),  # replace with actual previous migration
    ]

    operations = [
        migrations.RunPython(assign_default_skill_to_knacks),
    ]