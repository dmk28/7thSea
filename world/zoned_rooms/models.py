from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel

class ZonedRoomModel(SharedMemoryModel):
    room = models.OneToOneField('objects.ObjectDB', on_delete=models.CASCADE, related_name='zoned_room')
    zone = models.CharField(max_length=50)
    
    class Meta:
        app_label = 'zoned_rooms'
        verbose_name = 'Zoned Room'
        verbose_name_plural = 'Zoned Rooms'

    def __str__(self):
        return f"{self.room} - {self.zone}"

    @classmethod
    def get_zones(cls):
        return cls.objects.values_list('zone', flat=True).distinct()

    @classmethod
    def get_rooms_in_zone(cls, zone):
        return cls.objects.filter(zone=zone)

    @property
    def exits(self):
        return self.room.exits

    @property
    def contents(self):
        return self.room.contents