from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.core.urlresolvers import reverse


# Create your models here.

class SingleMeasurements (models.Model):
	MASS = 'kg'
	VOLUME = 'ltr'
	PIECES = 'pcs'
	MUNITS_CHOICES = (
		(VOLUME, 'Liter'),
		(MASS, 'Kilogram'),
		(PIECES, 'Pieces'),
		)


	name = models.CharField(max_length=200,unique=True,null=False)
	slug = models.SlugField(unique=True)
	formtype = models.CharField(max_length=10,choices=MUNITS_CHOICES,verbose_name="Units")
	quantity = models.DecimalField(max_digits=19, decimal_places=10)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return '%s:%s' %(self.id,self.name)

	def get_absolute_url_update(self):
		return reverse("singlemeasurements:update", kwargs={"slug": self.slug})

	def get_absolute_url_confirm(self):
		return reverse("singlemeasurements:confirm", kwargs={"slug": self.slug})

	def get_absolute_url_delete(self):
		return reverse("singlemeasurements:delete", kwargs={"slug": self.slug})

	class Meta:
		ordering = ["-updated","-timestamp"]


def pre_save_typeofingredient_receiver(sender, instance, *args, **kwargs):
		instance.slug = slugify(instance.slug)

pre_save.connect(pre_save_typeofingredient_receiver, sender=SingleMeasurements)

