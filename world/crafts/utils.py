from evennia.objects.models import ObjectDB
from django.db.models import Q

def get_weapon_objects(weapon_type=None, include_subclasses=True):
    """
    Retrieve weapon objects from the database.

    Args:
        weapon_type (str, optional): Specific weapon type to filter by (e.g., 'Sword', 'Dagger').
        include_subclasses (bool): If True, include objects of subclasses of Weapon.

    Returns:
        QuerySet: A QuerySet of weapon object IDs.
    """
    base_typeclass = 'typeclasses.objects.Weapon'
    
    query = Q(db_typeclass_path__endswith=base_typeclass)
    
    if include_subclasses:
        query |= Q(db_typeclass_path__contains=f"{base_typeclass}.")
    
    weapons = ObjectDB.objects.filter(query)
    
    if weapon_type:
        weapons = weapons.filter(db_typeclass_path__icontains=weapon_type)
    
    return weapons.values_list('id', flat=True)