from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.core.urlresolvers import reverse


# Create your models here.

class TypeOfIngredient(models.Model):
	name = models.CharField(max_length=200,unique=True,null=False)
	slug = models.SlugField(unique=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.slug

	def get_absolute_url_update(self):
		return reverse("typeofingredient:update", kwargs={"slug": self.slug})

	def get_absolute_url_confirm(self):
		return reverse("typeofingredient:confirm", kwargs={"slug": self.slug})

	def get_absolute_url_delete(self):
		return reverse("typeofingredient:delete", kwargs={"slug": self.slug})

	class Meta:
		ordering = ["-updated","-timestamp"]



def create_slug_typeofingredient(instance, new_slug=None):
	slug = slugify(instance.name)
	if new_slug is not None:
		slug = new_slug
	qs = TypeOfIngredient.objects.filter(slug=slug).order_by("-id")
	exists = qs.exists()
	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug_typeofingredient(instance, new_slug=new_slug)
	return slug



def pre_save_typeofingredient_receiver(sender, instance, *args, **kwargs):
		instance.slug = create_slug_typeofingredient(instance)

pre_save.connect(pre_save_typeofingredient_receiver, sender=TypeOfIngredient)

