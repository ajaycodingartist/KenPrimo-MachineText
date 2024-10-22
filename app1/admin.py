from django.contrib import admin

# Register your models here.
from . models import RoomCategory
from . models import Room
from . models import Reservation
from . models import SpecialRate

class RoomCategoryadmin(admin.ModelAdmin):
    list_display = ('name','base_price')

class Roomadmin(admin.ModelAdmin):
    list_display = ('room_number','category','is_available')

class Reservationadmin(admin.ModelAdmin):
    list_display = ('room','start_date','end_date','customer_name','total_price')

class SpecialRateadmin(admin.ModelAdmin):
    list_display = ('room_category','start_date','end_date','rate_multiplier')

admin.site.register(RoomCategory, RoomCategoryadmin)
admin.site.register(Room, Roomadmin)
admin.site.register(Reservation, Reservationadmin)
admin.site.register(SpecialRate, SpecialRateadmin)