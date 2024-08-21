from django.db import migrations

def handle_duplicate_knacks_and_associate_skills(apps, schema_editor):
    Knack = apps.get_model('character_sheet', 'Knack')
    Skill = apps.get_model('character_sheet', 'Skill')
    
    # Create a default skill if none exists
    default_skill, _ = Skill.objects.get_or_create(name='General', category='Misc')
    
    # Handle duplicate knacks
    for knack in Knack.objects.all():
        duplicates = Knack.objects.filter(name=knack.name).exclude(id=knack.id)
        if duplicates.exists():
            # Assign the first duplicate to the default skill if it doesn't have one
            if not knack.skill:
                knack.skill = default_skill
                knack.save()
            # Delete other duplicates
            duplicates.delete()
        
        # Associate knacks with skills if they don't have one
        if not knack.skill:
            # Try to find a matching skill
            matching_skill = Skill.objects.filter(knacks__name=knack.name).first()
            if matching_skill:
                knack.skill = matching_skill
            else:
                knack.skill = default_skill
            knack.save()

class Migration(migrations.Migration):

    dependencies = [
        ('character_sheet', '0016_remove_charactersheet_sorcery_knacks_and_more'),  # replace with actual previous migration
    ]

    operations = [
        migrations.RunPython(handle_duplicate_knacks_and_associate_skills),
    ]