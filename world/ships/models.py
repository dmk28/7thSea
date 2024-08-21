from django.db import models
from evennia.objects.models import ObjectDB



class Ship(models.Model):
    evennia_object = models.OneToOneField(ObjectDB, on_delete=models.CASCADE, related_name='ship', limit_choices_to={'db_typeclass_path': 'typeclasses.domain.ships.Ships'})
    name = models.CharField(max_length=100)
    brawn = models.IntegerField(default=0)
    finesse = models.IntegerField(default=0)
    resolve = models.IntegerField(default=0)
    wits = models.IntegerField(default=0)
    panache = models.IntegerField(default=0)
    cargo = models.IntegerField(default=0)
    draft = models.IntegerField(default=0)
    captain = models.ForeignKey(ObjectDB, on_delete=models.SET_NULL, null=True, related_name='captained_ships')

    def __str__(self):
        return self.name

class Modification(models.Model):
    name = models.CharField(max_length=100)
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='modifications')

    def __str__(self):
        return self.name

class Flaw(models.Model):
    name = models.CharField(max_length=100)
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='flaws')

    def __str__(self):
        return self.name    