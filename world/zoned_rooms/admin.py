from django.contrib import admin
from evennia.objects.models import ObjectDB
from .models import ZonedRoomModel

@admin.register(ZonedRoomModel)
class ZonedRoomAdmin(admin.ModelAdmin):
    list_display = ('room', 'zone', 'get_room_key', 'get_exit_count', 'get_contents_count')
    list_filter = ('zone',)
    search_fields = ('room__db_key', 'zone')
    raw_id_fields = ('room',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('room', 'zone')
        }),
        # ('Room Details', {
        #     'fields': ('get_room_desc', 'get_room_type')
        # }),
            # ('Statistics', {
            #     'fields': ('get_exit_count', 'get_contents_count')
            # }),
    )

    def get_room_key(self, obj):
        return obj.room.key
    get_room_key.short_description = 'Room Name'

    def get_room_desc(self, obj):
        return obj.room.db.desc
    get_room_desc.short_description = 'Description'

    def get_room_type(self, obj):
        return obj.room.db_typeclass_path
    get_room_type.short_description = 'Room Type'

    def get_exit_count(self, obj):
        return ObjectDB.objects.filter(db_location=obj.room, db_typeclass_path__endswith='exits.Exit').count()
    get_exit_count.short_description = 'Exit Count'

    def get_contents_count(self, obj):
        return ObjectDB.objects.filter(db_location=obj.room, db_typeclass_path__endswith='exits.Exit').count()

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room')