from django.db import models

# Create your models here.
class Memory(models.Model):
	partNum = models.CharField(max_length=200,unique=True,null=False)
	capacity = models.CharField(max_length=200,null=False)

	def __str__(self):
		return self.partNum

class Computer(models.Model):
	name = models.CharField(max_length=200,unique=True,null=False)
	memory = models.ManyToManyField(Memory, through='ComputerMemory')

	def __str__(self):
		return self.name

class ComputerMemory(models.Model):
	memory = models.ForeignKey(Memory)
	computer = models.ForeignKey(Computer)
	count = models.IntegerField()

	def __str__(self):
		return self.memory

class Room(models.Model):
	name = models.CharField(max_length=200,null=False)
	memory = models.ManyToManyField(Memory,related_name='room_memory')

	def __str__(self):
		return self.name
