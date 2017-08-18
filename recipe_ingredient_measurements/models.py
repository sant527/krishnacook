from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.core.urlresolvers import reverse


# Create your models here.

class RecipeIngredientMeasurements (models.Model):
	KILOGRAM = 'Kg'
	LITER = 'ltr'
	PIECES = 'pcs'
	GRAM = 'g'
	MILLILETER = 'ml'
	MUNITS_CHOICES = (
		(KILOGRAM, 'Kilogram'),
		(LITER, 'Liter'),
		(PIECES, 'Pieces'),
		(GRAM, 'Grams'),
		(MILLILETER, 'Millileters'),
		)


	MASS = 'kg'
	VOLUME = 'ltr'
	PIECES = 'pcs'
	FORM_CHOICES = (
		(MASS, 'Mass'),
		(VOLUME, 'Volume'),
		(PIECES, 'Pieces'),
		)


	name = models.CharField(max_length=200,unique=True,null=False)
	slug = models.SlugField(unique=True)
	formtype = models.CharField(max_length=10,choices=FORM_CHOICES,default=MASS)
	volume_Liters = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True)
	mass_KiloGrams = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True)
	pieces_Numbers = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return '{%s} %s' % (self.name,self.form_type2())
		return self.name

	def get_absolute_url_update(self):
		return reverse("mixedmeasurements:update", kwargs={"slug": self.slug})

	def get_absolute_url_confirm(self):
		return reverse("mixedmeasurements:confirm", kwargs={"slug": self.slug})

	def get_absolute_url_delete(self):
		return reverse("mixedmeasurements:delete", kwargs={"slug": self.slug})

	def form_type(self):
		if self.formtype == "kg":
			return "Mass"
		elif self.formtype == "ltr":
			return "Volume"
		elif self.formtype == "pcs":
			return "Pieces"

	def form_type2(self):
		if self.formtype == "kg":
			return "M"
		elif self.formtype == "ltr":
			return "V"
		elif self.formtype == "pcs":
			return "P"

	def form_type3(self):
		if self.formtype == "kg":
			return "Kilogram"
		elif self.formtype == "ltr":
			return "Liter"
		elif self.formtype == "pcs":
			return "Pieces"

	def form_type2(self):
		if self.formtype == "kg":
			text="(M) - "+("{:.3f}".format(self.mass_KiloGrams))+" kg"
			if self.volume_Liters:
				text = text+" ["+("{:.3f}".format(self.volume_Liters))+" lt]"
			if self.pieces_Numbers:
				text = text+" ["+str("{:.3f}".format(self.pieces_Numbers))+" pcs]"
			return text
		elif self.formtype == "ltr":
			text="(V) - "+("{:.3f}".format(self.volume_Liters))+" lt"
			if self.mass_KiloGrams:
				text = text+" ["+str("{:.3f}".format(self.mass_KiloGrams))+" kg]"
			if self.pieces_Numbers:
				text = text+" ["+str("{:.3f}".format(self.pieces_Numbers))+" pcs]"
			return text
		else:
			text="(PC) - "+("{:.3f}".format(self.pieces_Numbers))+" pcs"
			if self.mass_KiloGrams:
				text = text+" ["+str("{:.3f}".format(self.mass_KiloGrams))+" kg]"
			if self.volume_Liters:
				text = text+" ["+str("{:.3f}".format(self.volume_Liters))+" lt]"
			return text







	class Meta:
		ordering = ["-updated","-timestamp"]


def pre_save_typeofingredient_receiver(sender, instance, *args, **kwargs):
		instance.slug = instance.slug

pre_save.connect(pre_save_typeofingredient_receiver, sender=RecipeIngredientMeasurements)

