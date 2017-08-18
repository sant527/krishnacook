from django.contrib import admin

from .models import Memory,Computer,ComputerMemory,Room
# Register your models here.

class MemoryModelAdmin(admin.ModelAdmin):
	list_display = ["partNum", "capacity"]
	class Meta:
		model=Memory

class ComputerModelAdmin(admin.ModelAdmin):
	list_display = ["name"]
	class Meta:
		model=Computer

class ComputerMemoryModelAdmin(admin.ModelAdmin):
	list_display = ["memory", "computer","count"]
	class Meta:
		model=ComputerMemory

class RoomModelAdmin(admin.ModelAdmin):
	list_display = ["name"]
	class Meta:
		model=Room

admin.site.register(Room, RoomModelAdmin)
admin.site.register(Memory, MemoryModelAdmin)
admin.site.register(Computer, ComputerModelAdmin)
admin.site.register(ComputerMemory, ComputerMemoryModelAdmin)

