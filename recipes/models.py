from django.db import models
from django.db.models.signals import pre_save,post_save,post_delete
from django.utils.text import slugify
from typeofingredient.models import TypeOfIngredient
#from ingredients.models import Ingredient
from django.core.urlresolvers import reverse
from django.db.models import F
from tags.models import Tag
from django.core.exceptions import ValidationError
from recipe_ingredient_measurements.models import RecipeIngredientMeasurements
from single_measurements.models import SingleMeasurements
from django.core.validators import MaxValueValidator, MinValueValidator
import arrow
# Create your models here.

class Recipe(models.Model):
	MASS = 'kg'
	VOLUME = 'ltr'
	PIECES = 'pcs'
	MUNITS_CHOICES = (
		(MASS, 'Mass'),
		(VOLUME, 'Volume'),
		(PIECES, 'Pieces'),
		)
	name = models.CharField(max_length=200)
	slug = models.SlugField(unique=True)
	tags = models.ManyToManyField(Tag,related_name='recipes_recipe_tag',help_text="CTRL + Click for selecting more than one tag",blank=True)
	primary_unit = models.CharField(max_length=10,choices=MUNITS_CHOICES,default=VOLUME,verbose_name="Preferred Display Units",help_text="Nothing significant for calculation. Only useful for Display. Eg: we enter Chapatis recipe Volume/Mass/Pieces Units, which are below this as 1 tub == 50 kg == 400 pieces. If we choose Volume, we will show the recipe name as: Chaptti for 1 tub, If we choose Mass then: Chappati for 50 kg, If we choose Pieces then: Chappati for 400 pices.",null=True,blank=True)
	mass_unit = models.ForeignKey(SingleMeasurements,on_delete=models.PROTECT,related_name='recipe_singlemeasurement_mass_unit',blank=True,null=True)
	mass_quantity = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True,validators=[MinValueValidator(0)])
	volume_unit = models.ForeignKey(SingleMeasurements,on_delete=models.PROTECT,related_name='recipe_singlemeasurement_volume_unit',blank=True,null=True)
	volume_quantity = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True,validators=[MinValueValidator(0)])
	pieces_unit = models.ForeignKey(SingleMeasurements,on_delete=models.PROTECT,related_name='recipe_singlemeasurement_pieces_unit',blank=True,null=True)
	pieces_quantity = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True,validators=[MinValueValidator(0)])
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return '%s --> %s' % (self.name,self.get_all_quantity_with_bulk_units_string())

	def get_absolute_url_update(self):
		return reverse("recipes:update", kwargs={"slug": self.slug})

	def get_absolute_url_detail(self):
		return reverse("recipes:detail", kwargs={"slug": self.slug})	

	def get_absolute_url_confirm(self):
		return reverse("recipes:confirm", kwargs={"slug": self.slug})

	def get_absolute_url_delete(self):
		return reverse("recipes:delete", kwargs={"slug": self.slug})

	def get_absolute_url_recipe_update_inline_bulk_ingredients(self):
		return reverse("recipes:updateingredientbulk", kwargs={"slug": self.slug})

	def get_absolute_url_ing_recipe_upd(self):
		return reverse("recipes:ing_recipe_upd", kwargs={"slug": self.slug})


	# def updated_time(self):
	# 	#a = self.recipe_positions.all().first().updated
	# 	if self.gauranga :
	# 		a = self.gauranga[0].updated #it will create no extra queries total 11 queries out of which 7 queries are
	# 	else:
	# 		a = self.updated

	# 	b = self.updated
	# 	if a >= b:
	# 		#return arrow.get(a).humanize()
	# 		return a
	# 	else:
	# 		#return arrow.get(b).humanize()
	# 		return b

	# def updated_time_nonhuman(self):
	# 	#a = self.recipe_positions.all().first().updated
	# 	if self.gauranga :
	# 		a = self.gauranga[0].updated
	# 	else:
	# 		a = self.updated
	# 	b = self.updated
	# 	if a >= b:
	# 		return a
	# 	else:
	# 		return b

	def updated_time_nonhuman_normal(self):
		count = self.recipe_positions.all().order_by('updated').count()
		if count == 0:
			a = self.updated
		else:
			a = self.recipe_positions.all().order_by('updated').first().updated
		b = self.updated
		if a >= b:
			return a
		else:
			return b

	def sort_by_date(self):
		return self.recipe_positions.order_by('-name')


	def get_all_quantity_with_bulk_units_string(self):
		z = ""
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			z = "%s - %.2f" % (self.mass_unit.slug,self.mass_quantity)
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			if z:
				z = z + ", %s - %.2f" % (self.volume_unit.slug,self.volume_quantity)
			else:
				z = z + "%s - %.2f" % (self.volume_unit.slug,self.volume_quantity)
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			if z:
				z = z + ", %s - %.2f" % (self.pieces_unit.slug,self.pieces_quantity)
			else:
				z = z + "%s - %.2f" % (self.pieces_unit.slug,self.pieces_quantity)
		return z

	def get_all_quantity_with_bulk_units_string_dict(self):
		data = dict()
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			data.update({self.volume_unit.slug:self.volume_quantity})
		else:
			data.update({"ltr":0})
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			data.update({self.mass_unit.slug:self.mass_quantity})
		else:
			data.update({"kg":0})
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			data.update({self.pieces_unit.slug:self.pieces_quantity})
		else:
			data.update({"pcs":0})
		return data

	#******************** Recipe Properties **********************************

	def list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe(self,factor=1):
		hare = []
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity >0:
			info = dict()
			info.update({'unit_type':'(mass)','unit_exists':1})
			info.update({'bulk': {'unit':self.mass_unit.slug,'quantity':self.mass_quantity}})
			basic_quantity = self.mass_quantity*self.mass_unit.quantity
			info.update({'basic':{'unit':'kg','quantity':basic_quantity}})
			info.update({'not_same':self.mass_quantity - basic_quantity})
			info.update({'bulk_fact': {'unit':self.mass_unit.slug,'quantity':self.mass_quantity*factor}})
			info.update({'basic_fact':{'unit':'kg','quantity':basic_quantity*factor}})


		else:
			info = dict()
			info.update({'unit_type':'(mass)','unit_exists':0})
			info.update({'bulk': {'unit':'kg','bulk_quantity':0}})
			info.update({'basic':{'unit':'kg','basic_quantity':0}})
			info.update({'bulk_fact': {'unit':'kg','bulk_quantity':0}})
			info.update({'basic_fact':{'unit':'kg','basic_quantity':0}})
			info.update({'not_same':0})

		hare.append(info)
		
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity >0:
			info = dict()
			info.update({'unit_type':'(vol)','unit_exists':1})
			info.update({'bulk':{'unit':self.volume_unit.slug,'quantity':self.volume_quantity}})
			basic_quantity = self.volume_quantity*self.volume_unit.quantity
			info.update({'basic':{'unit':'ltr','quantity':basic_quantity}})
			info.update({'not_same':self.volume_quantity - basic_quantity})
			info.update({'bulk_fact':{'unit':self.volume_unit.slug,'quantity':self.volume_quantity*factor}})
			info.update({'basic_fact':{'unit':'ltr','quantity':basic_quantity*factor}})

		else:
			info = dict()
			info.update({'unit_type':'(vol)','unit_exists':0})
			info.update({'bulk':{'unit':'ltr','quantity':0}})
			info.update({'basic':{'unit':'ltr','quantity':0}})
			info.update({'bulk_fact': {'unit':'kg','bulk_quantity':0}})
			info.update({'basic_fact':{'unit':'kg','basic_quantity':0}})
			info.update({'not_same':0})

		hare.append(info)
		
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity >0:
			info = dict()
			info.update({'unit_type':'(pcs)','unit_exists':1})
			info.update({'bulk':{'unit':self.pieces_unit.slug,'quantity':self.pieces_quantity}})
			basic_quantity = self.pieces_quantity*self.pieces_unit.quantity
			info.update({'basic':{'unit':'pcs','quantity':basic_quantity}})
			info.update({'not_same':self.pieces_quantity - basic_quantity})
			info.update({'bulk_fact':{'unit':self.pieces_unit.slug,'quantity':self.pieces_quantity * factor}})
			info.update({'basic_fact':{'unit':'pcs','quantity':basic_quantity * factor}})

		else:
			info = dict()
			info.update({'unit_type':'(pcs)','unit_exists':0})
			info.update({'bulk':{'unit':'pcs','quantity':0}})
			info.update({'basic':{'unit':'pcs','quantity':0}})
			info.update({'bulk_fact': {'unit':'kg','bulk_quantity':0}})
			info.update({'basic_fact':{'unit':'kg','basic_quantity':0}})
			info.update({'not_same':0})

		hare.append(info)

		return hare

	#*******************RECIPE PROPERTIES  total cost *******************************

	def dict_total_and_fact_cost_recipe(self,factor=1):
		data = dict()
		total_cost = 0
		recipepositions = self.recipe_positions.all()
		if recipepositions.exists():
			for recipepostion in recipepositions:
				cost_recipe_dict = recipepostion.dict_factor_density_cost_default_ing_recipeposition(factor)
				cost_recipe = cost_recipe_dict['cost']
				total_cost = total_cost + cost_recipe
		else:
			total_cost = total_cost
		data.update({"total_cost":total_cost,"fact_total_cost":total_cost * factor})
		return data

	#*******************RECIPE PROPERTIES default ingredients: cost per bulk and basic units *******************************

	def list_cost_per_bulk_units_and_kg_ltr_pcs_recipe(self):
		cost = self.dict_total_and_fact_cost_recipe(1)
		cost_recipe = cost['total_cost']
		hare = []
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			info = dict()
			info.update({'unit_type':'(mass)','unit_exists':1})
			bulk_cost = (cost_recipe/self.mass_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.mass_quantity * self.mass_unit.quantity))
			info.update({'bulk':{'unit':self.mass_unit.slug,'cost':bulk_cost}})
			info.update({'basic':{'unit':'kg','cost':kg_ltr_pcs_cost}})
			info.update({'not_same':bulk_cost - kg_ltr_pcs_cost})

		else:
			info = dict()
			info.update({'unit_type':'(mass)','unit_exists':0})
			info.update({'bulk':{'unit':'kg','cost':0}})
			info.update({'basic':{'unit':'kg','cost':0}})
			info.update({'not_same':0})

		hare.append(info)

		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			info = dict()
			info.update({'unit_type':'(vol)','unit_exists':1})
			bulk_cost = (cost_recipe/self.volume_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.volume_quantity * self.volume_unit.quantity))
			info.update({'bulk':{'unit':self.volume_unit.slug,'cost':bulk_cost}})
			info.update({'basic':{'unit':'ltr','cost':kg_ltr_pcs_cost}})
			info.update({'not_same':bulk_cost - kg_ltr_pcs_cost})
		else:
			info = dict()
			info.update({'unit_type':'(vol)','unit_exists':0})
			info.update({'bulk':{'unit':'ltr','cost':0}})
			info.update({'basic':{'unit':'ltr','cost':0}})
			info.update({'not_same':0})

		hare.append(info)

			
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			info = dict()
			info.update({'unit_type':'(pcs)','unit_exists':1})
			bulk_cost = (cost_recipe/self.pieces_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.pieces_quantity * self.pieces_unit.quantity))
			info.update({'bulk':{'unit':self.pieces_unit.slug,'cost':bulk_cost}})
			info.update({'basic':{'unit':'pcs','cost':kg_ltr_pcs_cost}})
			info.update({'not_same':bulk_cost - kg_ltr_pcs_cost})

		else:
			info = dict()
			info.update({'unit_type':'(pcs)','unit_exists':0})
			info.update({'bulk':{'unit':'pcs','cost':0}})
			info.update({'basic':{'unit':'pcs','cost':0}})
			info.update({'not_same':0})

		hare.append(info)

		return hare




	#*******************RECIPE PROPERTIES custom cost normal and factored *******************************

	def dict_total_and_fact_cost_custom_ing_recipe(self,menu,factor=1):
		data = dict()
		total_cost = 0
		recipepositions = self.recipe_positions.all()
		if recipepositions.exists():
			for recipepostion in recipepositions:
				cost_recipe_dict = recipepostion.dict_factor_density_cost_custom_ing_recipeposition(menu,factor)
				cost_recipe = cost_recipe_dict['cost']
				total_cost = total_cost + cost_recipe
		else:
			total_cost = total_cost
		data.update({"total_cost":total_cost,"fact_total_cost":total_cost * factor})
		return data

	#*******************RECIPE PROPERTIES custom cost per bulk and basic units *******************************

	def list_custom_cost_per_bulk_units_and_kg_ltr_pcs_recipe(self,menu):
		cost = self.dict_total_and_fact_cost_custom_ing_recipe(menu,1)
		cost_recipe = cost['total_cost']
		hare = []
		
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			info = dict()
			info.update({'unit_type':'(mass)','unit_exists':1})
			bulk_cost = (cost_recipe/self.mass_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.mass_quantity * self.mass_unit.quantity))
			info.update({'bulk':{'unit':self.mass_unit.slug,'cost':bulk_cost}})
			info.update({'basic':{'unit':'kg','cost':kg_ltr_pcs_cost}})
			info.update({'not_same':bulk_cost - kg_ltr_pcs_cost})

		else:
			info = dict()
			info.update({'unit_type':'(mass)','unit_exists':0})
			info.update({'bulk':{'unit':'kg','cost':0}})
			info.update({'basic':{'unit':'kg','cost':0}})
			info.update({'not_same':0})

		hare.append(info)

		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			info = dict()
			info.update({'unit_type':'(vol)','unit_exists':1})
			bulk_cost = (cost_recipe/self.volume_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.volume_quantity * self.volume_unit.quantity))
			info.update({'bulk':{'unit':self.volume_unit.slug,'cost':bulk_cost}})
			info.update({'basic':{'unit':'ltr','cost':kg_ltr_pcs_cost}})
			info.update({'not_same':bulk_cost - kg_ltr_pcs_cost})
		else:
			info = dict()
			info.update({'unit_type':'(vol)','unit_exists':0})
			info.update({'bulk':{'unit':'ltr','cost':0}})
			info.update({'basic':{'unit':'ltr','cost':0}})
			info.update({'not_same':0})

		hare.append(info)

			
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			info = dict()
			info.update({'unit_type':'(pcs)','unit_exists':1})
			bulk_cost = (cost_recipe/self.pieces_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.pieces_quantity * self.pieces_unit.quantity))
			info.update({'bulk':{'unit':self.pieces_unit.slug,'cost':bulk_cost}})
			info.update({'basic':{'unit':'pcs','cost':kg_ltr_pcs_cost}})
			info.update({'not_same':bulk_cost - kg_ltr_pcs_cost})

		else:
			info = dict()
			info.update({'unit_type':'(pcs)','unit_exists':0})
			info.update({'bulk':{'unit':'pcs','cost':0}})
			info.update({'basic':{'unit':'pcs','cost':0}})
			info.update({'not_same':0})

		hare.append(info)

		return hare


#****************************************************************************************

	def get_bulk_units_to_kg_lt_pcs_dict(self):
		data = dict()
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			data.update({self.volume_unit.slug:self.volume_unit.quantity})
		else:
			data.update({"ltr":0})
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			data.update({self.mass_unit.slug:self.mass_unit.quantity})
		else:
			data.update({"kg":0})
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			data.update({self.pieces_unit.slug:self.pieces_unit.quantity})
		else:
			data.update({"pcs":0})
		return data

	def get_all_quantity_with_kg_lt_pcs_units_string_dict(self):
		data = dict()
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			data.update({"ltr":self.volume_quantity * self.volume_unit.quantity})
		else:
			data.update({"ltr":0})
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			data.update({"kg":self.mass_quantity * self.mass_unit.quantity})
		else:
			data.update({"kg":0})
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			data.update({"pcs":self.pieces_quantity * self.pieces_unit.quantity})
		else:
			data.update({"pcs":0})
		return data

	def get_all_quantity_with_kg_lt_pcs_units_string(self):
		z = ""
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			z = "%s - %.2f" % ("kg",self.mass_quantity * self.mass_unit.quantity)
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			if z:
				z = z + ", %s - %.2f" % ("ltr",self.volume_quantity * self.volume_unit.quantity)
			else:
				z = z + "%s - %.2f" % ("ltr",self.volume_quantity * self.volume_unit.quantity)
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			if z:
				z = z + ", %s - %.2f" % ("pcs",self.pieces_quantity * self.pieces_unit.quantity)
			else:
				z = z + "%s - %.2f" % ("pcs",self.pieces_quantity * self.pieces_unit.quantity)
		return z


	def get_cost_of_the_recipe(self):
		# only 138 times
		total_cost = 0
		recipepositions2 = self.recipe_positions.all()
		if recipepositions2.exists():
			for recipepostion in recipepositions2:
				total_cost = total_cost + recipepostion.get_total_cost()
		else:
			total_cost = total_cost
		return total_cost

	def get_cost_of_the_recipe_custom_price_ingredient_factor(self,factor,menu):
		# only 138 times
		total_cost = 0
		recipepositions2 = self.recipe_positions.all()
		if recipepositions2.exists():
			for recipepostion in recipepositions2:
				total_cost = total_cost + recipepostion.custom_cost_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(factor,menu)
		else:
			total_cost = total_cost
		return total_cost

	def get_cost_of_the_recipe_custom_price_ingredient_factor_per_person(self,factor,menu,menuposition):
		# only 138 times
		total_cost = 0
		recipepositions2 = self.recipe_positions.all()
		if recipepositions2.exists():
			for recipepostion in recipepositions2:
				total_cost = total_cost + recipepostion.custom_cost_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(factor,menu)
		else:
			total_cost = total_cost
		return total_cost/menuposition.persons

	def get_cost_of_the_recipe_custom_price_ingredient(self,menu):
		# only 138 times
		total_cost = 0
		recipepositions2 = self.recipe_positions.all()
		if recipepositions2.exists():
			for recipepostion in recipepositions2:
				total_cost = total_cost + recipepostion.custom_cost_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with(menu)
		else:
			total_cost = total_cost
		return total_cost


	def get_cost_per_bulk_units_and_kg_ltr_pcs_custom_ingredient_prices(self,menu):
		cost_recipe = self.get_cost_of_the_recipe_custom_price_ingredient(menu)
		hare = []
		if self.volume_quantity is not None and self.volume_quantity > 0:
			data = dict()
			bulk_cost = (cost_recipe/self.volume_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.volume_quantity * self.volume_unit.quantity))
			data.update({'exists':1,'needed':bulk_cost - kg_ltr_pcs_cost ,'bulk_unit':self.volume_unit.slug,'bulk_cost':bulk_cost,'unit':'ltr','unit_cost':kg_ltr_pcs_cost})
			hare.append(data)
		else:
			data = dict()
			data.update({'exists':0,'needed':0,"bulk_unit":'ltr','bullk_cost':0,'unit':'ltr','unit_cost':0})
			hare.append(data)

		if self.mass_quantity is not None and self.mass_quantity > 0:
			data=dict()
			bulk_cost = (cost_recipe/self.mass_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.mass_quantity * self.mass_unit.quantity))
			data.update({'exists':1,'needed':bulk_cost - kg_ltr_pcs_cost ,'bulk_unit':self.mass_unit.slug,'bulk_cost':bulk_cost,'unit':'kg','unit_cost':kg_ltr_pcs_cost})
			hare.append(data)
		else:
			data=dict()
			data.update({'exists':0,'needed':0,"bulk_unit":'kg','bulk_cost':0,'unit':'kg','unit_cost':0})
			hare.append(data)

		if self.pieces_quantity is not None and self.pieces_quantity > 0:
			data=dict()
			bulk_cost = (cost_recipe/self.pieces_quantity)
			kg_ltr_pcs_cost = (cost_recipe/(self.pieces_quantity * self.pieces_unit.quantity))
			data.update({'exists':1,'needed':bulk_cost - kg_ltr_pcs_cost ,'bulk_unit':self.pieces_unit.slug,'bulk_cost':bulk_cost,'unit':'pcs','unit_cost':kg_ltr_pcs_cost})
			hare.append(data)
		else:
			data=dict()
			data.update({'exists':0,'needed':0,"bulk_unit":'pcs','bulk_cost':0,'unit':'pcs','unit_cost':0})
			hare.append(data)
		return hare


	def get_total_quantity_in_primary_bulk_units(self):
		if self.primary_unit == "kg":
			if self.mass_unit is not None and self.mass_quantity is not None:
				total_quantity = self.mass_quantity
				return total_quantity
		elif self.primary_unit == "ltr":
			if self.volume_unit is not None and self.volume_quantity is not None:
				total_quantity = self.volume_quantity
				return total_quantity
		else:
			if self.pieces_unit is not None and self.volume_quantity is not None:
				total_quantity = self.pieces_quantity
				return total_quantity

	def get_primary_bulk_unit(self):
		if self.primary_unit == "kg":
			if self.mass_unit is not None and self.mass_quantity is not None:
				return self.mass_unit
		elif self.primary_unit == "ltr":
			if self.volume_unit is not None and self.volume_quantity is not None:
				return self.volume_unit
		else:
			if self.pieces_unit is not None and self.volume_quantity is not None:
				return self.pieces_unit
		

	def get_cost_of_the_recipe_per_bulk_unit_mass(self):
		if self.mass_quantity and self.mass_quantity > 0:
			cost = (self.const_total_cost_recipe()/self.mass_quantity)
			return cost
		else:
			return 0

	def get_cost_of_the_recipe_per_bulk_unit_volume(self):
		#print("get_cost_of_the_recipe_per_bulk_unit_volume")
		if self.volume_quantity and self.volume_quantity > 0:
			#print(self.get_cost_of_the_recipe())
			cost = (self.const_total_cost_recipe()/self.volume_quantity)
			return cost
		else:
			return 0

	def get_cost_of_the_recipe_per_bulk_unit_pieces(self):
		if self.pieces_quantity and self.pieces_quantity > 0:
			cost = (self.const_total_cost_recipe()/self.pieces_quantity)
			return cost
		else:
			return 0


	def get_cost_of_the_recipe_per_bulk_unit_dict(self):
		data = dict()
		if self.volume_quantity and self.volume_quantity > 0:
			cost = (self.const_total_cost_recipe()/self.volume_quantity)
			data.update({self.volume_unit.slug:cost})
		else:
			data.update({"ltr":0})
		if self.mass_quantity and self.mass_quantity > 0:
			cost = (self.const_total_cost_recipe()/self.mass_quantity)
			data.update({self.mass_unit.slug:cost})
		else:
			data.update({"kg":0})
		if self.pieces_quantity and self.pieces_quantity > 0:
			cost = (self.const_total_cost_recipe()/self.pieces_quantity)
			data.update({self.pieces_unit.slug:cost})
		else:
			data.update({"pcs":0})
		return data

	def get_cost_of_the_recipe_per_kg_lt_pcs_unit_dict(self):
		data = dict()
		if self.volume_quantity  and self.volume_quantity > 0:
			cost = (self.const_total_cost_recipe()/(self.volume_quantity*self.volume_unit.quantity))
			data.update({"ltr":cost})
		else:
			data.update({"ltr":0})
		if self.mass_quantity and self.mass_quantity > 0:
			cost = (self.const_total_cost_recipe()/(self.mass_quantity*self.mass_unit.quantity))
			data.update({"kg":cost})
		else:
			data.update({"kg":0})
		if self.pieces_quantity and self.pieces_quantity > 0:
			cost = (self.const_total_cost_recipe()/(self.pieces_quantity*self.pieces_unit.quantity))
			data.update({"pcs":cost})
		else:
			data.update({"pcs":0})
		return data


	def get_cost_of_the_recipe_per_unit_mass(self):
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			cost = (self.const_total_cost_recipe()/(self.mass_quantity*self.mass_unit.quantity))
			return cost
		else:
			return 0

	def get_cost_of_the_recipe_per_unit_volume(self):
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			cost = (self.const_total_cost_recipe()/(self.volume_quantity*self.volume_unit.quantity))
			return cost
		else:
			return 0

	def get_cost_of_the_recipe_per_unit_pieces(self):
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			cost = (self.const_total_cost_recipe()/(self.pieces_quantity*self.pieces_unit.quantity))
			return cost
		else:
			return 0
		

	# def get_cost_of_the_recipe_per_kg_lt_pcs(self):
	# 	if self.get_total_quantity_in_primary_kg_lt_pcs():
	# 		if self.get_total_quantity_in_primary_kg_lt_pcs() > 0:
	# 			a = (self.get_cost_of_the_recipe()/self.get_total_quantity_in_primary_kg_lt_pcs())
	# 			return a

	def get_allowable_Units(self):
		text = self.primary_unit.form_type()+"- ["
		if self.primary_unit.mass_quantity:
			text = text+"Kg"
		if self.primary_unit.volume_quantity:
			text = text+"-lt"
		if self.primary_unit.pieces_quantity:
			text = text+"-pcs"
		text = text+"]"
		return text

	def get_Mass_quantity(self):
		if self.mass_unit is not None and self.mass_quantity is not None:
			if self.mass_quantity > 0:
				return self.mass_unit.quantity * self.mass_quantity
		else:
			return 0

	def get_Volume_quantity(self):
		if self.volume_unit is not None and self.volume_quantity is not None:
			if self.volume_quantity > 0:
				return self.volume_unit.quantity * self.volume_quantity
		else:
			return 0
	
	def get_Pieces_quantity(self):
		if self.pieces_unit is not None and self.volume_quantity is not None:
			if self.pieces_quantity > 0:
				return self.pieces_unit.quantity * self.pieces_quantity
		else:
			return 0



	class Meta:
		ordering = ["name"]


def create_slug_recipe(instance, new_slug=None):
	slug = slugify(instance.name)
	if new_slug is not None:
		slug = new_slug
	qs = Recipe.objects.filter(slug=slug).order_by("-id")
	exists = qs.exists()
	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug_recipe(instance, new_slug=new_slug)
	return slug


def pre_save_recipe_receiver(sender, instance, *args, **kwargs):
		num = Recipe.objects.filter(pk=instance.pk).count()
		if num == 0 :
			print('INSERT !!')
			instance.slug = create_slug_recipe(instance)
		else:
			print('UPDAT !!')
			if has_changed(instance,"name"):
				instance.slug = create_slug_recipe(instance)
				
		#a = instance.updated_time_nonhuman_normal()
		#instance.overall_updated = a

def has_changed(instance, field):
	if not instance.pk:
		return False
	old_value = instance.__class__._default_manager.filter(pk=instance.pk).values(field).get()[field]
	return not getattr(instance, field) == old_value



# def post_save_recipe_receiver(sender, instance, *args, **kwargs):
# 	a = instance.updated_time_nonhuman_normal()
# 	instance.overall_updated = a




pre_save.connect(pre_save_recipe_receiver, sender=Recipe)

# post_save.connect(post_save_recipe_receiver, sender=Recipe)

# class RecipePositionManger(models.Manager):
# 	def sort_sequence_asc(self, *args, **kwargs):
# 		return super(RecipePositionManger, self).order_by('sequence_number')

# class PostManager(models.Manager):
#     def active(self, *args, **kwargs):
#         # Post.objects.all() = super(PostManager, self).all()
#         return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())

class RecipePosition(models.Model):
	MASS = 'kg'
	VOLUME = 'ltr'
	PIECES = 'pcs'
	MUNITS_CHOICES = (
		(MASS, 'Mass'),
		(VOLUME, 'Volume'),
		(PIECES, 'Pieces'),
		)

	# objects = RecipePositionManger()

	name = models.CharField(max_length=200,blank=True,help_text="If left blank will be same as Ingredient name Eg: Tomato pulp")
	recipe = models.ForeignKey(Recipe,related_name='recipe_positions', on_delete=models.CASCADE)
	ingredient = models.ForeignKey('ingredients.Ingredient',verbose_name="ingredient (MUnit) - Rate/MUnit",related_name='ingredient_recipeposition', null=True,blank=False,on_delete=models.PROTECT)
	recipeposition_slug = models.SlugField(unique=True)
	primary_unit =models.CharField(max_length=10,choices=MUNITS_CHOICES,default=MASS,verbose_name="Preferred Display Units",help_text="Nothing significant for calculation. Only useful for Display. Eg: we enter Nimbu ingredients Volume/Mass/Pieces Units, which are below this as 1 mug == 0.7 kg == 100 pieces. If we choose Volume, we will show the ingredient name as: Nimbu - 1 mug, If we choose Mass then: Nimbu - 0.7 kg, If we choose Pieces then: Nimbu - 100 pieces.",null=True,blank=True)
	mass_unit = models.ForeignKey(SingleMeasurements,on_delete=models.PROTECT,related_name='recipepoisition_singlemeasurement_mass_unit',blank=True,null=True)
	mass_quantity = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True,default=0,validators=[MinValueValidator(0)])
	volume_unit = models.ForeignKey(SingleMeasurements,on_delete=models.PROTECT,related_name='recipepoisition_singlemeasurement_volume_unit',blank=True,null=True)
	volume_quantity = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True,default=0,validators=[MinValueValidator(0)])
	pieces_unit = models.ForeignKey(SingleMeasurements,on_delete=models.PROTECT,related_name='recipepoisition_singlemeasurement_pieces_unit',blank=True,null=True)
	pieces_quantity = models.DecimalField(max_digits=19, decimal_places=10,null=True,blank=True,default=0,validators=[MinValueValidator(0)])
	cooking_notes = models.CharField(max_length=200,blank=True)
	sequence_number = models.PositiveSmallIntegerField(default = 0,null=True,blank=True)
	title = models.CharField(max_length=200,blank=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return '%s:: %s' % (self.ingredient.name, self.recipe.name )


	def get_absolute_url_update(self):
		return reverse("recipes:updatepos", kwargs={"slug": self.recipeposition_slug})

	def get_absolute_url_detail(self):
		return reverse("recipes:detail", kwargs={"slug": self.recipe.slug})	

	def get_absolute_url_confirm(self):
		return reverse("recipes:confirmpos", kwargs={"slug": self.recipeposition_slug})

	def get_absolute_url_delete(self):
		return reverse("recipes:deletepos", kwargs={"slug": self.recipeposition_slug})

	class Meta:
		ordering = ["sequence_number"]

#******************* RecipePosition Properties of original and factored values

	def list_factor_qty_unit_bulk_and_kg_ltr_pcs_list_recipeposition(self,factor=1):
		hare = []
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity >0:
			info = dict()
			info.update({'unit_type':'kg','unit_exists':1})
			info.update({'bulk': {'unit':self.mass_unit.slug,'quantity':self.mass_quantity}})
			basic_quantity = self.mass_quantity*self.mass_unit.quantity
			info.update({'basic':{'unit':'kg','quantity':basic_quantity}})
			info.update({'not_same':self.mass_quantity - basic_quantity})
			info.update({'bulk_fact': {'unit':self.mass_unit.slug,'quantity':self.mass_quantity*factor}})
			info.update({'basic_fact':{'unit':'kg','quantity':basic_quantity*factor}})

		else:
			info = dict()
			info.update({'unit_type':'kg','unit_exists':0})
			info.update({'bulk': {'unit':'kg','quantity':0}})
			info.update({'basic':{'unit':'kg','quantity':0}})
			info.update({'bulk_fact': {'unit':'kg','quantity':0}})
			info.update({'basic_fact':{'unit':'kg','quantity':0}})
			info.update({'not_same':0})

		hare.append(info)
		
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity >0:
			info = dict()
			info.update({'unit_type':'ltr','unit_exists':1})
			info.update({'bulk':{'unit':self.volume_unit.slug,'quantity':self.volume_quantity}})
			basic_quantity = self.volume_quantity*self.volume_unit.quantity
			info.update({'basic':{'unit':'ltr','quantity':basic_quantity}})
			info.update({'not_same':self.volume_quantity - basic_quantity})
			info.update({'bulk_fact':{'unit':self.volume_unit.slug,'quantity':self.volume_quantity*factor}})
			info.update({'basic_fact':{'unit':'ltr','quantity':basic_quantity*factor}})

		else:
			info = dict()
			info.update({'unit_type':'ltr','unit_exists':0})
			info.update({'bulk':{'unit':'ltr','quantity':0}})
			info.update({'basic':{'unit':'ltr','quantity':0}})
			info.update({'bulk_fact':{'unit':'ltr','quantity':0}})
			info.update({'basic_fact':{'unit':'ltr','quantity':0}})
			info.update({'not_same':0})

		hare.append(info)
		
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity >0:
			info = dict()
			info.update({'unit_type':'pcs','unit_exists':1})
			info.update({'bulk':{'unit':self.pieces_unit.slug,'quantity':self.pieces_quantity}})
			basic_quantity = self.pieces_quantity*self.pieces_unit.quantity
			info.update({'basic':{'unit':'pcs','quantity':basic_quantity}})
			info.update({'not_same':self.pieces_quantity - basic_quantity})
			info.update({'bulk_fact':{'unit':self.pieces_unit.slug,'quantity':self.pieces_quantity*factor}})
			info.update({'basic_fact':{'unit':'pcs','quantity':basic_quantity*factor}})

		else:
			info = dict()
			info.update({'unit_type':'pcs','unit_exists':0})
			info.update({'bulk':{'unit':'pcs','quantity':0}})
			info.update({'basic':{'unit':'pcs','quantity':0}})
			info.update({'not_same':0})
			info.update({'bulk_fact':{'unit':'pcs','quantity':0}})
			info.update({'basic_fact':{'unit':'pcs','quantity':0}})

		hare.append(info)

		return hare

	#************************* Recipe Position/Ingredient Cost Properties *******************************#
	# trying to get the cost quantity. Eg unit is in cups then multiply with density and get to kg
	def dict_factor_density_cost_default_ing_recipeposition(self,factor=1):
		default_rate = self.ingredient.rate
		data = dict()
		if self.ingredient.munit == "kg":
			cost_unit = 'kg'
			data.update({'cost_unit':cost_unit,'rate':default_rate})

			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				cost_quantity =  self.mass_quantity * self.mass_unit.quantity
				cost = cost_quantity * default_rate

				cost_quantity_factor =  self.mass_quantity * self.mass_unit.quantity * factor
				cost_factor = cost_quantity_factor * default_rate
			
				data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
				return data
				#return self.get_Mass_quantity()


			# here we want to check if two densities and two units are available, then which ever give the highest cost quantity is considered.
			if (self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0) and (self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0):
				cost1 = -9999999999999
				cost2 = -9999999999999
				if self.ingredient.density_kg_per_lt is not None:
					cost_quantity1 = self.volume_quantity * self.volume_unit.quantity * self.ingredient.density_kg_per_lt
					cost1 = cost_quantity1 * default_rate
					cost_quantity1_factor = self.volume_quantity * self.volume_unit.quantity * self.ingredient.density_kg_per_lt * factor
					cost1_factor = cost_quantity1_factor * default_rate			
				if self.ingredient.density_pcs_per_kg is not None and self.ingredient.density_pcs_per_kg != 0:
					cost_quantity2 = self.volume_quantity * self.volume_unit.quantity / self.ingredient.density_pcs_per_kg
					cost2 = cost_quantity2 * default_rate
					cost_quantity2_factor = self.volume_quantity * self.volume_unit.quantity / self.ingredient.density_pcs_per_kg * factor
					cost2_factor = cost_quantity2_factor * default_rate


				if cost_quantity1 > cost_quantity2:
					data.update({'density_factor': self.ingredient.density_kg_per_lt,'density_unit':'kg/ltr','inverse':'','cost_quantity':cost_quantity1,'cost':cost1,'cost_quantity_factor':cost_quantity1_factor,'cost_factor':cost1_factor})
					return data
				elif cost_quantity2 > cost_quantity1:
					data.update({'density_factor': self.ingredient.density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'1/','cost_quantity':cost_quantity2,'cost':cost2,'cost_quantity_factor':cost_quantity2_factor,'cost_factor':cost2_factor})
					return data
				else:
					pass


			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if self.ingredient.density_kg_per_lt is not None:
					cost_quantity = self.volume_quantity * self.volume_unit.quantity * self.ingredient.density_kg_per_lt
					cost = cost_quantity * default_rate
					cost_quantity_factor = self.volume_quantity * self.volume_unit.quantity * self.ingredient.density_kg_per_lt * factor
					cost_factor = cost_quantity_factor * default_rate
					data.update({'density_factor': self.ingredient.density_kg_per_lt,'density_unit':'kg/ltr','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
					return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
					return data

			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				#print("inside mass3")
				if self.ingredient.density_pcs_per_kg is not None:
					if self.ingredient.density_pcs_per_kg != 0:
						#print("inside mass4")
						cost_quantity = self.volume_quantity * self.volume_unit.quantity / self.ingredient.density_pcs_per_kg
						cost = cost_quantity * default_rate
						cost_quantity_factor = self.volume_quantity * self.volume_unit.quantity / self.ingredient.density_pcs_per_kg * factor
						cost_factor = cost_quantity_factor * default_rate
						data.update({'density_factor': self.ingredient.density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'1/','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
						return data
						#return self.get_Pieces_quantity() / self.ingredient.density_pcs_per_kg
					else:
						data.update({'density_factor':'0','density_unit':'pcs/kg','inverse':'1/','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
					return data

			data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
			return data

		if self.ingredient.munit == "lts":
			cost_unit = 'lts'
			data.update({'cost_unit':cost_unit,'rate':default_rate})
			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				cost_quantity = self.volume_quantity * self.volume_unit.quantity
				cost = cost_quantity * default_rate
				cost_quantity_factor = self.volume_quantity * self.volume_unit.quantity * factor
				cost_factor = cost_quantity_factor * default_rate
				data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
				return data
				#return self.get_Volume_quantity()


			if (self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0) and (self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0):
				cost1 = -9999999999999
				cost2 = -9999999999999
				if (self.ingredient.density_kg_per_lt is not None) and (self.ingredient.density_kg_per_lt != 0):
					cost_quantity1 = self.mass_quantity * self.mass_unit.quantity / self.ingredient.density_kg_per_lt
					cost1 = cost_quantity1 * default_rate
					cost_quantity1_factor = self.mass_quantity * self.mass_unit.quantity / self.ingredient.density_kg_per_lt * factor
					cost1_factor = cost_quantity1_factor * default_rate
				if (self.ingredient.density_pcs_per_lt is not None) and (self.ingredient.density_pcs_per_lt != 0):
					cost_quantity2 = self.pieces_quantity * self.pieces_unit.quantity / self.ingredient.density_pcs_per_lt
					cost2 = cost_quantity2 * default_rate
					cost_quantity2_factor = self.pieces_quantity * self.pieces_unit.quantity / self.ingredient.density_pcs_per_lt * factor
					cost2_factor = cost_quantity2_factor * default_rate
				if cost_quantity1 > cost_quantity2:
					data.update({'density_factor': self.ingredient.density_kg_per_lt,'density_unit':'kg/ltr','inverse':'1/','cost_quantity':cost_quantity1,'cost':cost1,'cost_quantity_factor':cost_quantity1_factor,'cost_factor':cost1_factor})
					return data
				elif cost_quantity2 > cost_quantity1:
					data.update({'density_factor': self.ingredient.density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'1/','quantity':cost_quantity2,'cost':cost2,'cost_quantity_factor':cost_quantity2_factor,'cost_factor':cost2_factor})
					return data
				else:
					pass					


			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if self.ingredient.density_kg_per_lt is not None:
					if self.ingredient.density_kg_per_lt != 0:
						cost_quantity = self.mass_quantity * self.mass_unit.quantity / self.ingredient.density_kg_per_lt
						cost = cost_quantity * default_rate
						cost_quantity_factor = self.mass_quantity * self.mass_unit.quantity / self.ingredient.density_kg_per_lt * factor
						cost_factor = cost_quantity_factor * default_rate
						data.update({'density_factor': self.ingredient.density_kg_per_lt,'density_unit':'kg/ltr','inverse':'1/','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
						return data
						#return self.get_Mass_quantity() / self.ingredient.density_kg_per_lt
					else:
						data.update({'density_factor':'0','density_unit':'kg/ltr','inverse':'1/','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'1/','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
					return data
			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				if self.ingredient.density_pcs_per_lt is not None:
					if self.ingredient.density_pcs_per_lt != 0:
						cost_quantity = self.pieces_quantity * self.pieces_unit.quantity / self.ingredient.density_pcs_per_lt
						cost = cost_quantity * default_rate
						cost_quantity_factor = self.pieces_quantity * self.pieces_unit.quantity / self.ingredient.density_pcs_per_lt * factor
						cost_factor = cost_quantity_factor * default_rate
						data.update({'density_factor': self.ingredient.density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'1/','quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
						return data
						#return self.get_Pieces_quantity() / self.ingredient.density_pcs_per_lt
					else:
						data.update({'density_factor':'0','density_unit':'pcs/ltr','inverse':'1/','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'1/','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
					return data

			data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
			return data

		if self.ingredient.munit == "pcs":
			cost_unit = 'pcs'
			data.update({'cost_unit':cost_unit,'rate':default_rate})
			
			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				cost_quantity = self.pieces_quantity * self.pieces_unit.quantity
				cost = cost_quantity * default_rate
				cost_quantity_factor = self.pieces_quantity * self.pieces_unit.quantity * factor
				cost_factor = cost_quantity_factor * default_rate
				data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
				return data
				#return self.get_Pieces_quantity()

			if (self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0) and (self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0):
				cost1 = -9999999999999
				cost2 = -9999999999999
				if self.ingredient.density_pcs_per_lt is not None:
					cost_quantity1 = self.volume_quantity * self.volume_unit.quantity * self.ingredient.density_pcs_per_lt
					cost1 = cost_quantity1 * default_rate
					cost_quantity1_factor = self.volume_quantity * self.volume_unit.quantity * self.ingredient.density_pcs_per_lt * factor
					cost1_factor = cost_quantity1_factor * default_rate

				if self.ingredient.density_pcs_per_kg is not None:
					cost_quantity2 = self.mass_quantity * self.mass_unit.quantity * self.ingredient.density_pcs_per_kg
					cost2 = cost_quantity2 * default_rate
					cost_quantity2_factor = self.mass_quantity * self.mass_unit.quantity * self.ingredient.density_pcs_per_kg * factor
					cost2_factor = cost_quantity2_factor * default_rate


				if cost_quantity1 > cost_quantity2:
					data.update({'density_factor': self.ingredient.density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'','cost_quantity':cost_quantity1,'cost':cost1,'cost_quantity_factor':cost_quantity1_factor,'cost_factor':cost1_factor})
					return data
				elif cost_quantity2 > cost_quantity1:
					data.update({'density_factor': self.ingredient.density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'','cost_quantity':cost_quantity2,'cost':cost2,'cost_quantity_factor':cost_quantity2_factor,'cost_factor':cost2_factor})
					return data
				else:
					pass



			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if self.ingredient.density_pcs_per_lt is not None:
					cost_quantity = self.volume_quantity * self.volume_unit.quantity * self.ingredient.density_pcs_per_lt
					cost = cost_quantity * default_rate
					cost_quantity_factor = self.volume_quantity * self.volume_unit.quantity * self.ingredient.density_pcs_per_lt * factor
					cost_factor = cost_quantity_factor * default_rate
					data.update({'density_factor': self.ingredient.density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
					return data
					#return self.get_Volume_quantity() * self.ingredient.density_pcs_per_lt
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
					return data

			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if self.ingredient.density_pcs_per_kg is not None:
					cost_quantity = self.mass_quantity * self.mass_unit.quantity * self.ingredient.density_pcs_per_kg
					cost = cost_quantity * default_rate
					cost_quantity_factor = self.mass_quantity * self.mass_unit.quantity * self.ingredient.density_pcs_per_kg * factor
					cost_factor = cost_quantity_factor * default_rate
					data.update({'density_factor': self.ingredient.density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
					return data
					#return self.get_Mass_quantity() * self.ingredient.density_pcs_per_kg
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/kg','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
					return data

			data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
			return data
			
		data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
		return data

	
	#************************* Recipe Position/Ingredient Cost Properties for custom ingredients *******************************#
	# trying to get the cost quantity. Eg unit is in cups then multiply with density and get to kg
	def dict_factor_density_cost_custom_ing_recipeposition(self,menu,factor=1):
		ingredient = menu.menu_positions_customingredients.all().filter(ingredient = self.ingredient).first()
		default_rate = ingredient.rate
		density_kg_per_lt = self.ingredient.density_kg_per_lt
		density_pcs_per_lt = self.ingredient.density_pcs_per_lt
		density_pcs_per_kg = self.ingredient.density_pcs_per_kg
		data = dict()
		if ingredient.ingredient.munit == "kg":
			cost_unit = 'kg'
			data.update({'cost_unit':cost_unit,'rate':default_rate})

			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				cost_quantity =  self.mass_quantity * self.mass_unit.quantity
				cost = cost_quantity * default_rate

				cost_quantity_factor =  self.mass_quantity * self.mass_unit.quantity * factor
				cost_factor = cost_quantity_factor * default_rate
			
				data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
				return data
				#return self.get_Mass_quantity()


			# here we want to check if two densities and two units are available, then which ever give the highest cost quantity is considered.
			if (self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0) and (self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0):
				cost1 = -9999999999999
				cost2 = -9999999999999
				if density_kg_per_lt is not None:
					cost_quantity1 = self.volume_quantity * self.volume_unit.quantity * density_kg_per_lt
					cost1 = cost_quantity1 * default_rate
					cost_quantity1_factor = self.volume_quantity * self.volume_unit.quantity * density_kg_per_lt * factor
					cost1_factor = cost_quantity1_factor * default_rate			
				if density_pcs_per_kg is not None and density_pcs_per_kg != 0:
					cost_quantity2 = self.volume_quantity * self.volume_unit.quantity / density_pcs_per_kg
					cost2 = cost_quantity2 * default_rate
					cost_quantity2_factor = self.volume_quantity * self.volume_unit.quantity / density_pcs_per_kg * factor
					cost2_factor = cost_quantity2_factor * default_rate


				if cost_quantity1 > cost_quantity2:
					data.update({'density_factor': density_kg_per_lt,'density_unit':'kg/ltr','inverse':'','cost_quantity':cost_quantity1,'cost':cost1,'cost_quantity_factor':cost_quantity1_factor,'cost_factor':cost1_factor})
					return data
				elif cost_quantity2 > cost_quantity1:
					data.update({'density_factor': density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'1/','cost_quantity':cost_quantity2,'cost':cost2,'cost_quantity_factor':cost_quantity2_factor,'cost_factor':cost2_factor})
					return data
				else:
					pass


			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if density_kg_per_lt is not None:
					cost_quantity = self.volume_quantity * self.volume_unit.quantity * density_kg_per_lt
					cost = cost_quantity * default_rate
					cost_quantity_factor = self.volume_quantity * self.volume_unit.quantity * density_kg_per_lt * factor
					cost_factor = cost_quantity_factor * default_rate
					data.update({'density_factor': density_kg_per_lt,'density_unit':'kg/ltr','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
					return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
					return data

			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				#print("inside mass3")
				if density_pcs_per_kg is not None:
					if density_pcs_per_kg != 0:
						#print("inside mass4")
						cost_quantity = self.volume_quantity * self.volume_unit.quantity / density_pcs_per_kg
						cost = cost_quantity * default_rate
						cost_quantity_factor = self.volume_quantity * self.volume_unit.quantity / density_pcs_per_kg * factor
						cost_factor = cost_quantity_factor * default_rate
						data.update({'density_factor': density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'1/','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
						return data
						#return self.get_Pieces_quantity() / density_pcs_per_kg
					else:
						data.update({'density_factor':'0','density_unit':'pcs/kg','inverse':'1/','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
					return data

			data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
			return data

		if ingredient.ingredient.munit == "lts":
			cost_unit = 'lts'
			data.update({'cost_unit':cost_unit,'rate':default_rate})
			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				cost_quantity = self.volume_quantity * self.volume_unit.quantity
				cost = cost_quantity * default_rate
				cost_quantity_factor = self.volume_quantity * self.volume_unit.quantity * factor
				cost_factor = cost_quantity_factor * default_rate
				data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
				return data
				#return self.get_Volume_quantity()


			if (self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0) and (self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0):
				cost1 = -9999999999999
				cost2 = -9999999999999
				if (density_kg_per_lt is not None) and (density_kg_per_lt != 0):
					cost_quantity1 = self.mass_quantity * self.mass_unit.quantity / density_kg_per_lt
					cost1 = cost_quantity1 * default_rate
					cost_quantity1_factor = self.mass_quantity * self.mass_unit.quantity / density_kg_per_lt * factor
					cost1_factor = cost_quantity1_factor * default_rate
				if (density_pcs_per_lt is not None) and (density_pcs_per_lt != 0):
					cost_quantity2 = self.pieces_quantity * self.pieces_unit.quantity / density_pcs_per_lt
					cost2 = cost_quantity2 * default_rate
					cost_quantity2_factor = self.pieces_quantity * self.pieces_unit.quantity / density_pcs_per_lt * factor
					cost2_factor = cost_quantity2_factor * default_rate
				if cost_quantity1 > cost_quantity2:
					data.update({'density_factor': density_kg_per_lt,'density_unit':'kg/ltr','inverse':'1/','cost_quantity':cost_quantity1,'cost':cost1,'cost_quantity_factor':cost_quantity1_factor,'cost_factor':cost1_factor})
					return data
				elif cost_quantity2 > cost_quantity1:
					data.update({'density_factor': density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'1/','quantity':cost_quantity2,'cost':cost2,'cost_quantity_factor':cost_quantity2_factor,'cost_factor':cost2_factor})
					return data
				else:
					pass					


			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if density_kg_per_lt is not None:
					if density_kg_per_lt != 0:
						cost_quantity = self.mass_quantity * self.mass_unit.quantity / density_kg_per_lt
						cost = cost_quantity * default_rate
						cost_quantity_factor = self.mass_quantity * self.mass_unit.quantity / density_kg_per_lt * factor
						cost_factor = cost_quantity_factor * default_rate
						data.update({'density_factor': density_kg_per_lt,'density_unit':'kg/ltr','inverse':'1/','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
						return data
						#return self.get_Mass_quantity() / density_kg_per_lt
					else:
						data.update({'density_factor':'0','density_unit':'kg/ltr','inverse':'1/','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'1/','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
					return data
			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				if density_pcs_per_lt is not None:
					if density_pcs_per_lt != 0:
						cost_quantity = self.pieces_quantity * self.pieces_unit.quantity / density_pcs_per_lt
						cost = cost_quantity * default_rate
						cost_quantity_factor = self.pieces_quantity * self.pieces_unit.quantity / density_pcs_per_lt * factor
						cost_factor = cost_quantity_factor * default_rate
						data.update({'density_factor': density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'1/','quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
						return data
						#return self.get_Pieces_quantity() / density_pcs_per_lt
					else:
						data.update({'density_factor':'0','density_unit':'pcs/ltr','inverse':'1/','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'1/','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
					return data

			data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
			return data

		if ingredient.ingredient.munit == "pcs":
			cost_unit = 'pcs'
			data.update({'cost_unit':cost_unit,'rate':default_rate})
			
			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				cost_quantity = self.pieces_quantity * self.pieces_unit.quantity
				cost = cost_quantity * default_rate
				cost_quantity_factor = self.pieces_quantity * self.pieces_unit.quantity * factor
				cost_factor = cost_quantity_factor * default_rate
				data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
				return data
				#return self.get_Pieces_quantity()

			if (self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0) and (self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0):
				cost1 = -9999999999999
				cost2 = -9999999999999
				if density_pcs_per_lt is not None:
					cost_quantity1 = self.volume_quantity * self.volume_unit.quantity * density_pcs_per_lt
					cost1 = cost_quantity1 * default_rate
					cost_quantity1_factor = self.volume_quantity * self.volume_unit.quantity * density_pcs_per_lt * factor
					cost1_factor = cost_quantity1_factor * default_rate

				if density_pcs_per_kg is not None:
					cost_quantity2 = self.mass_quantity * self.mass_unit.quantity * density_pcs_per_kg
					cost2 = cost_quantity2 * default_rate
					cost_quantity2_factor = self.mass_quantity * self.mass_unit.quantity * density_pcs_per_kg * factor
					cost2_factor = cost_quantity2_factor * default_rate


				if cost_quantity1 > cost_quantity2:
					data.update({'density_factor': density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'','cost_quantity':cost_quantity1,'cost':cost1,'cost_quantity_factor':cost_quantity1_factor,'cost_factor':cost1_factor})
					return data
				elif cost_quantity2 > cost_quantity1:
					data.update({'density_factor': density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'','cost_quantity':cost_quantity2,'cost':cost2,'cost_quantity_factor':cost_quantity2_factor,'cost_factor':cost2_factor})
					return data
				else:
					pass



			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if density_pcs_per_lt is not None:
					cost_quantity = self.volume_quantity * self.volume_unit.quantity * density_pcs_per_lt
					cost = cost_quantity * default_rate
					cost_quantity_factor = self.volume_quantity * self.volume_unit.quantity * density_pcs_per_lt * factor
					cost_factor = cost_quantity_factor * default_rate
					data.update({'density_factor': density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
					return data
					#return self.get_Volume_quantity() * density_pcs_per_lt
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'','cost_quantity':0,'cost':cost,'cost_quantity_factor':0,'cost_factor':0})
					return data

			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if density_pcs_per_kg is not None:
					cost_quantity = self.mass_quantity * self.mass_unit.quantity * density_pcs_per_kg
					cost = cost_quantity * default_rate
					cost_quantity_factor = self.mass_quantity * self.mass_unit.quantity * density_pcs_per_kg * factor
					cost_factor = cost_quantity_factor * default_rate
					data.update({'density_factor': density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'','cost_quantity':cost_quantity,'cost':cost,'cost_quantity_factor':cost_quantity_factor,'cost_factor':cost_factor})
					return data
					#return self.get_Mass_quantity() * density_pcs_per_kg
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/kg','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
					return data

			data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
			return data
			
		data.update({'density_factor':'--','density_unit':'--','inverse':'','cost_quantity':0,'cost':0,'cost_quantity_factor':0,'cost_factor':0})
		return data

#***********************************************************************************************************

	def get_all_quantity_with_bulk_units_dict(self):
		# MYSQL PROBLEM
		data = dict()
		if self.mass_unit is not None and self.mass_quantity is not None:
			if self.mass_quantity >0:
				data.update({self.mass_unit.slug:self.mass_quantity})
		if self.volume_unit is not None and self.volume_quantity:
			if self.volume_quantity >0:
				data.update({self.volume_unit.slug:self.volume_quantity})
		if self.pieces_unit is not None and self.pieces_quantity:
			if self.pieces_quantity >0:
				data.update({self.pieces_unit.slug:self.pieces_quantity})
		return data

	def get_all_quantity_with_bulk_units_dict_multiply_with_factor(self,factor):
		data = dict()
		if self.mass_unit is not None and self.mass_quantity:
			if self.mass_quantity >0:
				data.update({self.mass_unit.slug:self.mass_quantity * factor})
		if self.volume_unit is not None and self.volume_quantity:
			if self.volume_quantity >0:
				data.update({self.volume_unit.slug:self.volume_quantity * factor})
		if self.pieces_unit is not None and self.pieces_quantity:
			if self.pieces_quantity >0:
				data.update({self.pieces_unit.slug:self.pieces_quantity * factor})
		return data






	def get_all_quantity_with_bulk_units_string(self):
		z = ""
		if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
			z = "%s - %.2f" % (self.mass_unit.slug,self.mass_quantity)
		if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
			z = z + "%s - %.2f" % (self.volume_unit.slug,self.volume_quantity)
		if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
			z = z + "%s - %.2f" % (self.pieces_unit.slug,self.pieces_quantity)
		return z

	def get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(self,factor):
		data = dict()
		if self.mass_unit is not None and self.mass_quantity:
			if self.mass_quantity >0:
				data.update({"kg":self.mass_quantity * self.mass_unit.quantity * factor})
		if self.volume_unit is not None and self.volume_quantity:
			if self.volume_quantity >0:
				data.update({"ltr":self.volume_quantity * self.volume_unit.quantity * factor})
		if self.pieces_unit is not None and self.pieces_quantity:
			if self.pieces_quantity >0:
				data.update({"pcs":self.pieces_quantity * self.pieces_unit.quantity * factor})
		return data


	def custom_cost_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(self,factor,menu):
		data = self.get_cost_quantity_dict_custom_ingredient_mixed_density(menu)
		cost_quantity = data['quantity']
		custom_rate = menu.menu_get_custom_ingredient_rate(self.ingredient)
		if custom_rate == 0:
			return cost_quantity * self.ingredient.rate * factor
		else:
			return cost_quantity * custom_rate * factor

	def cost_quantity_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(self,factor):
		data = self.get_cost_quantity_dict()
		quantity_factor = data['quantity'] * factor
		data.update({'quantity_factor':quantity_factor})
		data.update({'factor':factor})
		return data

	def cost_quantity_kg_ltr_pcs_units_dict_multiply_with_factor_custom_ingredient_mixed_density(self,factor,menu):
		data = self.get_cost_quantity_dict_custom_ingredient_mixed_density(menu)
		quantity_factor = data['quantity'] * factor
		data.update({'quantity_factor':quantity_factor})
		data.update({'factor':factor})
		return data


	def custom_cost_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with(self,menu):
		custom_rate = menu.menu_get_custom_ingredient_rate(self.ingredient)
		data = self.get_cost_quantity_dict_custom_ingredient_mixed_density(menu)
		cost_quantity = data['quantity']
		custom_rate = menu.menu_get_custom_ingredient_rate(self.ingredient)
		if custom_rate != 0:
			return cost_quantity * custom_rate
		else:
			return cost_quantity * self.ingredient.rate



	def get_Mass_quantity(self):
		if self.mass_unit is not None and self.mass_quantity is not None:
			if self.mass_quantity >=0:
				return self.mass_unit.quantity * self.mass_quantity
		else:
			return 0

	def get_Volume_quantity(self):
		if self.volume_unit is not None and self.volume_quantity is not None:
			if self.volume_quantity >=0:
				return self.volume_unit.quantity * self.volume_quantity
		else:
			return 0
	
	def get_Pieces_quantity(self):
		if self.pieces_unit is not None and self.pieces_quantity is not None:
			if self.pieces_quantity >=0:
				return self.pieces_unit.quantity * self.pieces_quantity
		else:
			return 0

	def get_cost_quantity(self):
		if self.ingredient.munit == "kg":
			#print("inside mass")
			if self.mass_unit is not None and self.mass_quantity is not None :
				#print("inside mass1")
				return self.get_Mass_quantity()
			elif self.volume_unit is not None and self.volume_quantity is not None and self.ingredient.density_kg_per_lt is not None:
				#print("inside mass2")
				return self.get_Volume_quantity() * self.ingredient.density_kg_per_lt
			elif self.pieces_unit is not None and self.pieces_quantity is not None:
				#print("inside mass3")
				if self.ingredient.density_pcs_per_kg is not None and self.ingredient.density_pcs_per_kg != 0:
					#print("inside mass4")
					return self.get_Pieces_quantity() / self.ingredient.density_pcs_per_kg
			else:
				#print("inside mass 0 return")
				return 0
		if self.ingredient.munit == "lts":
			#print("inside liters")
			if self.volume_unit is not None and self.volume_quantity is not None:
				return self.get_Volume_quantity()
			if self.mass_unit is not None and self.mass_quantity is not None:
				if self.ingredient.density_kg_per_lt is not None and self.ingredient.density_kg_per_lt != 0:
					return self.get_Mass_quantity() / self.ingredient.density_kg_per_lt
			elif self.pieces_unit is not None and self.pieces_quantity is not None:
				if self.ingredient.density_pcs_per_lt is not None and self.ingredient.density_pcs_per_lt != 0:
					return self.get_Pieces_quantity() / self.ingredient.density_pcs_per_lt
			else:
				return 0
		if self.ingredient.munit == "pcs":
			#print("inside pieces")
			if self.pieces_unit is not None and self.pieces_quantity is not None:
				return self.get_Pieces_quantity()
			elif self.volume_unit is not None and self.volume_quantity is not None and self.ingredient.density_pcs_per_lt is not None:
				return self.get_Volume_quantity() * self.ingredient.density_pcs_per_lt
			elif self.mass_unit is not None and self.mass_quantity is not None and self.ingredient.density_pcs_per_kg is not None:
				return self.get_Mass_quantity() * self.ingredient.density_pcs_per_kg
			else:
				return 0
		return 0

	def get_cost_quantity_dict(self):
		data = dict()
		if self.ingredient.munit == "kg":
			#print("inside mass")
			data.update({'cost_unit':'kg'})
			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				#print("inside mass1")
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Mass_quantity()})
				return data
				#return self.get_Mass_quantity()
			elif self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if self.ingredient.density_kg_per_lt is not None:
					data.update({'density_factor': self.ingredient.density_kg_per_lt,'density_unit':'kg/ltr','inverse':'','quantity':self.get_Volume_quantity() * self.ingredient.density_kg_per_lt})
					return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'','quantity':0})
					return data
			elif self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				#print("inside mass3")
				if self.ingredient.density_pcs_per_kg is not None:
					if self.ingredient.density_pcs_per_kg != 0:
						#print("inside mass4")
						data.update({'density_factor': self.ingredient.density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'1/','quantity':self.get_Pieces_quantity() / self.ingredient.density_pcs_per_kg})
						return data
						#return self.get_Pieces_quantity() / self.ingredient.density_pcs_per_kg
					else:
						data.update({'density_factor':'0','density_unit':'pcs/kg','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/kg','inverse':'1/','quantity':0})
					return data
			else:
				#print("inside mass 0 return")
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		if self.ingredient.munit == "lts":
			#print("inside liters")
			data.update({'cost_unit':'lts'})
			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Volume_quantity()})
				return data
				#return self.get_Volume_quantity()
			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if self.ingredient.density_kg_per_lt is not None:
					if self.ingredient.density_kg_per_lt != 0:
						data.update({'density_factor': self.ingredient.density_kg_per_lt,'density_unit':'kg/ltr','inverse':'1/','quantity':self.get_Mass_quantity() / self.ingredient.density_kg_per_lt})
						return data
						#return self.get_Mass_quantity() / self.ingredient.density_kg_per_lt
					else:
						data.update({'density_factor':'0','density_unit':'kg/ltr','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'1/','quantity':0})
					return data
			elif self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				if self.ingredient.density_pcs_per_lt is not None:
					if self.ingredient.density_pcs_per_lt != 0:
						data.update({'density_factor': self.ingredient.density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'1/','quantity':self.get_Pieces_quantity() / self.ingredient.density_pcs_per_lt})
						return data
						#return self.get_Pieces_quantity() / self.ingredient.density_pcs_per_lt
					else:
						data.update({'density_factor':'0','density_unit':'pcs/ltr','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'1/','quantity':0})
					return data
			else:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		if self.ingredient.munit == "pcs":
			data.update({'cost_unit':'pcs'})
			#print("inside pieces")
			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Pieces_quantity()})
				return data
				#return self.get_Pieces_quantity()
			elif self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if self.ingredient.density_pcs_per_lt is not None:
					data.update({'density_factor': self.ingredient.density_pcs_per_lt,'density_unit':'pcs/ltr','inverse':'','quantity':self.get_Volume_quantity() * self.ingredient.density_pcs_per_lt})
					return data
					#return self.get_Volume_quantity() * self.ingredient.density_pcs_per_lt
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'','quantity':0})
					return data
			elif self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if self.ingredient.density_pcs_per_kg is not None:
					data.update({'density_factor': self.ingredient.density_pcs_per_kg,'density_unit':'pcs/kg','inverse':'','quantity':self.get_Mass_quantity() * self.ingredient.density_pcs_per_kg})
					return data
					#return self.get_Mass_quantity() * self.ingredient.density_pcs_per_kg
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/kg','inverse':'','quantity':0})
					return data
			else:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
		return data
		#return 0


	def get_custom_default_mixed_density_custom_ingredient(self,menu):
		data = menu.menu_get_custom_ingredient_density_dict(self.ingredient)
		if data['density_kg_per_lt'] == 0:
			if self.ingredient.density_kg_per_lt is None:
				data.update({'density_kg_per_lt':0})
			else:
				data.update({'density_kg_per_lt':self.ingredient.density_kg_per_lt})
		if data['density_pcs_per_kg'] == 0:
			if self.ingredient.density_pcs_per_kg is None:
				data.update({'density_pcs_per_kg':0})
			else:
				data.update({'density_pcs_per_kg':self.ingredient.density_pcs_per_kg})
		if data['density_pcs_per_lt'] == 0:
			if self.ingredient.density_pcs_per_lt is None:
				data.update({'density_pcs_per_lt':0})
			else:
				data.update({'density_pcs_per_lt':self.ingredient.density_pcs_per_lt})
		return data


	def get_cost_quantity_dict_custom_ingredient_mixed_density(self,menu):
		data = self.get_custom_default_mixed_density_custom_ingredient(menu)
		if self.ingredient.munit == "kg":
			#print("inside mass")
			data.update({'cost_unit':'kg'})
			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				#print("inside mass1")
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Mass_quantity()})
				return data
				#return self.get_Mass_quantity()
			elif self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if data['density_kg_per_lt'] is not None:
					data.update({'density_factor': data['density_kg_per_lt'],'density_unit':'kg/ltr','inverse':'','quantity':self.get_Volume_quantity() * data['density_kg_per_lt']})
					return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'','quantity':0})
					return data
			elif self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				#print("inside mass3")
				if data['density_pcs_per_kg'] is not None:
					if data['density_pcs_per_kg'] != 0:
						#print("inside mass4")
						data.update({'density_factor': data['density_pcs_per_kg'],'density_unit':'pcs/kg','inverse':'1/','quantity':self.get_Pieces_quantity() / data['density_pcs_per_kg']})
						return data
						#return self.get_Pieces_quantity() / data['density_pcs_per_kg']
					else:
						data.update({'density_factor':'0','density_unit':'pcs/kg','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/kg','inverse':'1/','quantity':0})
					return data
			else:
				#print("inside mass 0 return")
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		if self.ingredient.munit == "lts":
			#print("inside liters")
			data.update({'cost_unit':'lts'})
			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Volume_quantity()})
				return data
				#return self.get_Volume_quantity()
			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if data['density_kg_per_lt'] is not None:
					if data['density_kg_per_lt'] != 0:
						data.update({'density_factor': data['density_kg_per_lt'],'density_unit':'kg/ltr','inverse':'1/','quantity':self.get_Mass_quantity() / data['density_kg_per_lt']})
						return data
						#return self.get_Mass_quantity() / data['density_kg_per_lt']
					else:
						data.update({'density_factor':'0','density_unit':'kg/ltr','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'1/','quantity':0})
					return data
			elif self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				if data['density_pcs_per_lt'] is not None:
					if data['density_pcs_per_lt'] != 0:
						data.update({'density_factor': data['density_pcs_per_lt'],'density_unit':'pcs/ltr','inverse':'1/','quantity':self.get_Pieces_quantity() / data['density_pcs_per_lt']})
						return data
						#return self.get_Pieces_quantity() / data['density_pcs_per_lt']
					else:
						data.update({'density_factor':'0','density_unit':'pcs/ltr','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'1/','quantity':0})
					return data
			else:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		if self.ingredient.munit == "pcs":
			data.update({'cost_unit':'pcs'})
			#print("inside pieces")
			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Pieces_quantity()})
				return data
				#return self.get_Pieces_quantity()
			elif self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if data['density_pcs_per_lt'] is not None:
					data.update({'density_factor': data['density_pcs_per_lt'],'density_unit':'pcs/ltr','inverse':'','quantity':self.get_Volume_quantity() * data['density_pcs_per_lt']})
					return data
					#return self.get_Volume_quantity() * data['density_pcs_per_lt']
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'','quantity':0})
					return data
			elif self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if data['density_pcs_per_kg'] is not None:
					data.update({'density_factor': data['density_pcs_per_kg'],'density_unit':'pcs/kg','inverse':'','quantity':self.get_Mass_quantity() * data['density_pcs_per_kg']})
					return data
					#return self.get_Mass_quantity() * data['density_pcs_per_kg']
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/kg','inverse':'','quantity':0})
					return data
			else:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
		return data
		#return 0

	def get_custom_density_custom_ingredient(self,menu):
		data = menu.menu_get_custom_ingredient_density_dict(self.ingredient)
		if data['density_kg_per_lt'] == 0:
			if self.ingredient.density_kg_per_lt is None:
				data.update({'density_kg_per_lt':0})
			else:
				data.update({'density_kg_per_lt':self.ingredient.density_kg_per_lt})
		if data['density_pcs_per_kg'] == 0:
			if self.ingredient.density_pcs_per_kg is None:
				data.update({'density_pcs_per_kg':0})
			else:
				data.update({'density_pcs_per_kg':self.ingredient.density_pcs_per_kg})
		if data['density_pcs_per_lt'] == 0:
			if self.ingredient.density_pcs_per_lt is None:
				data.update({'density_pcs_per_lt':0})
			else:
				data.update({'density_pcs_per_lt':self.ingredient.density_pcs_per_lt})
		return data


	def get_cost_quantity_dict_custom_ingredient_custom_density(self,menu):
		data = self.get_custom_density_custom_ingredient(menu)
		if self.ingredient.munit == "kg":
			#print("inside mass")
			data.update({'cost_unit':'kg'})
			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				#print("inside mass1")
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Mass_quantity()})
				return data
				#return self.get_Mass_quantity()
			elif self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if data['density_kg_per_lt'] is not None:
					data.update({'density_factor': data['density_kg_per_lt'],'density_unit':'kg/ltr','inverse':'','quantity':self.get_Volume_quantity() * data['density_kg_per_lt']})
					return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'','quantity':0})
					return data
			elif self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				#print("inside mass3")
				if data['density_pcs_per_kg'] is not None:
					if data['density_pcs_per_kg'] != 0:
						#print("inside mass4")
						data.update({'density_factor': data['density_pcs_per_kg'],'density_unit':'pcs/kg','inverse':'1/','quantity':self.get_Pieces_quantity() / data['density_pcs_per_kg']})
						return data
						#return self.get_Pieces_quantity() / data['density_pcs_per_kg']
					else:
						data.update({'density_factor':'0','density_unit':'pcs/kg','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/kg','inverse':'1/','quantity':0})
					return data
			else:
				#print("inside mass 0 return")
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		if self.ingredient.munit == "lts":
			#print("inside liters")
			data.update({'cost_unit':'lts'})
			if self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Volume_quantity()})
				return data
				#return self.get_Volume_quantity()
			if self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if data['density_kg_per_lt'] is not None:
					if data['density_kg_per_lt'] != 0:
						data.update({'density_factor': data['density_kg_per_lt'],'density_unit':'kg/ltr','inverse':'1/','quantity':self.get_Mass_quantity() / data['density_kg_per_lt']})
						return data
						#return self.get_Mass_quantity() / data['density_kg_per_lt']
					else:
						data.update({'density_factor':'0','density_unit':'kg/ltr','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'kg/ltr','inverse':'1/','quantity':0})
					return data
			elif self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				if data['density_pcs_per_lt'] is not None:
					if data['density_pcs_per_lt'] != 0:
						data.update({'density_factor': data['density_pcs_per_lt'],'density_unit':'pcs/ltr','inverse':'1/','quantity':self.get_Pieces_quantity() / data['density_pcs_per_lt']})
						return data
						#return self.get_Pieces_quantity() / data['density_pcs_per_lt']
					else:
						data.update({'density_factor':'0','density_unit':'pcs/ltr','inverse':'1/','quantity':0})
						return data
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'1/','quantity':0})
					return data
			else:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		if self.ingredient.munit == "pcs":
			data.update({'cost_unit':'pcs'})
			#print("inside pieces")
			if self.pieces_unit is not None and self.pieces_quantity is not None and self.pieces_quantity > 0:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':self.get_Pieces_quantity()})
				return data
				#return self.get_Pieces_quantity()
			elif self.volume_unit is not None and self.volume_quantity is not None and self.volume_quantity > 0:
				if data['density_pcs_per_lt'] is not None:
					data.update({'density_factor': data['density_pcs_per_lt'],'density_unit':'pcs/ltr','inverse':'','quantity':self.get_Volume_quantity() * data['density_pcs_per_lt']})
					return data
					#return self.get_Volume_quantity() * data['density_pcs_per_lt']
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/ltr','inverse':'','quantity':0})
					return data
			elif self.mass_unit is not None and self.mass_quantity is not None and self.mass_quantity > 0:
				if data['density_pcs_per_kg'] is not None:
					data.update({'density_factor': data['density_pcs_per_kg'],'density_unit':'pcs/kg','inverse':'','quantity':self.get_Mass_quantity() * data['density_pcs_per_kg']})
					return data
					#return self.get_Mass_quantity() * data['density_pcs_per_kg']
				else:
					data.update({'density_factor':'Nil','density_unit':'pcs/kg','inverse':'','quantity':0})
					return data
			else:
				data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
				return data
				#return 0
		data.update({'density_factor':'--','density_unit':'--','inverse':'','quantity':0})
		return data
		#return 0








	def get_total_cost(self):
		if self.get_cost_quantity():
			#print("self.get_cost_quantity()")
			#print(self.get_cost_quantity())
			return self.get_cost_quantity() * self.ingredient.rate
		return 0


def create_slug_ingredient(instance, new_slug=None):
	#print(new_slug)
	#print(instance.recipe.name)
	slug = slugify(instance.recipe.name+"-"+instance.ingredient.name)
	#print(slug)
	if new_slug is not None:
		slug = new_slug
	qs = RecipePosition.objects.filter(recipeposition_slug=slug).order_by("-id")
	exists = qs.exists()
	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug_ingredient(instance, new_slug=new_slug)
	return slug





def pre_save_recipeposition_receiver(sender, instance, *args, **kwargs):
		instance.recipeposition_slug = create_slug_ingredient(instance)
		if instance.name == "":
			instance.name = instance.ingredient.name


pre_save.connect(pre_save_recipeposition_receiver, sender=RecipePosition)

def post_save_recipeposition_receiver(sender, instance, *args, **kwargs):
		instance.recipe.save()


post_save.connect(post_save_recipeposition_receiver, sender=RecipePosition)


def post_delete_recipeposition_receiver(sender, instance, *args, **kwargs):
		instance.recipe.save()


post_delete.connect(post_delete_recipeposition_receiver, sender=RecipePosition)


	# def get_ingredient_quantity_converted_to_the_cost_unit(self):
	# 	#print(self.ingredient.munit)
	# 	if self.ingredient.munit == 'kg':
	# 		# check whether its a purely liquid measuring unit
	# 		if self.munit.formtype == 'kg':	
	# 			return self.quantity * self.munit.quantity
	# 		elif self.munit.formtype == 'ltr':
	# 			if not self.ingredient.density:
	# 				density = 0;
	# 			else:
	# 				density = self.ingredient.density
	# 			return self.quantity * self.munit.quantity * density
	# 		else:
	# 			return 0
	# 	elif self.ingredient.munit == 'ltr':
	# 		if self.munit.formtype == 'kg':	
	# 			return 0
	# 		elif self.munit.formtype == 'ltr':
	# 			return self.munit.quantity * self.quantity
	# 		else:
	# 			return 0
	# 	else:
	# 		if self.munit.formtype == 'kg':
	# 			return 0
	# 		elif self.munit.formtype == 'ltr':
	# 			return 0
	# 		else:
	# 			return self.munit.quantity * self.quantity

	# def get_ingredient_quantity(self):
	# 	#print(self.ingredient.munit)
	# 	if self.ingredient.munit == 'kg':
	# 		# check whether its a purely liquid measuring unit
	# 		if self.munit.formtype == 'kg':	
	# 			return self.quantity * self.munit.quantity
	# 		elif self.munit.formtype == 'ltr':
	# 			#print("gauranga")
	# 			if not self.ingredient.density:
	# 				density = 0;
	# 			else:
	# 				density = self.ingredient.density
	# 			#print(self.quantity * self.munit.quantity)
	# 			return (self.quantity * self.munit.quantity)
	# 		else:
	# 			return 0

	# 	elif self.ingredient.munit == 'ltr':
	# 		#print("Nityananda")
	# 		if self.munit.formtype == 'kg':	
	# 			return 0
	# 		elif self.munit.formtype == 'ltr':
	# 			return self.munit.quantity * self.quantity
	# 		else:
	# 			return 0
	# 	else:
	# 		if self.munit.formtype == 'kg':
	# 			return 0
	# 		elif self.munit.formtype == 'ltr':
	# 			return 0
	# 		else:
	# 			return self.munit.quantity * self.quantity

	# def get_cost_of_the_ingredient(self):
	# 	return (self.ingredient.rate * self.get_ingredient_quantity_converted_to_the_cost_unit())

"""
class Recipe(models.Model):
	name = models.CharField(max_length=200)

class Ingredient(models.Model):
	recipe = models.ForeignKey(Recipe,related_name='recipe_positions', on_delete=models.CASCADE)
	ingredientname = models.CharField(max_length=200,unique=True,null=False)
	ingredientquantity = models.PositiveSmallIntegerField(help_text="select w.r.t grams")

# unit of measurement is grams required to make for one person


Example Data for Recipe Model:
1 bread and butter
2 tomato soup
3 veg noodles

Example Data for Ingredient Model:
1 recipe="bread and butter" ingredientname="bread" ingredientquantity="200"
2 recipe="bread and butter" ingredientname="butter" ingredientquantity="100"

3 recipe="tomato soup" ingredientname="tomato" ingredientquantity="500"
4 recipe="tomato soup" ingredientname="sugar" ingredientquantity="50"
5 recipe="tomato soup" ingredientname="salt" ingredientquantity="10"
6 recipe="tomato soup" ingredientname="pepper" ingredientquantity="5"

7 recipe="veg noodles" ingredientname="noodles" ingredientquantity="600"
8 recipe="veg noodles" ingredientname="salt" ingredientquantity="10"
8 recipe="veg noodles" ingredientname="vegetables" ingredientquantity="200"


class Event(models.Model):
	name = models.CharField(max_length=200)


class Menu(models.Model):
	event = models.ForeignKey(Event,related_name='event_related', on_delete=models.CASCADE)
	recipeevent = models.ForeignKey(Recipe, related_name='eventrecipe_related',null=False, blank=False,on_delete=models.CASCADE)
	quantityevent = models.PositiveSmallIntegerField(help_text="Number of people")

Example Data for Event:
1  "tourist group A breakfast"
2  "Anils conference"
3  "kids playtime"


Example Data for Ingredient Model:
1 recipe="tourist group A breakfast" recipeevent="tomato soup" quantityevent="20"
2 recipe="tourist group A breakfast" recipeevent="bread and butter" quantityevent=quantityevent"

3 recipe="Anils conference" recipeevent="tomato soup" quantityevent="10"
4 recipe="Anils conference" recipeevent="bread and butter" quantityevent="20"
5 recipe="Anils conference" recipeevent="veg noodles" quantityevent=quantityevent"

7 recipe="kids playtime" recipeevent="veg noodles" quantityevent="30"
8 recipe="kids playtime" recipeevent="tomato soup" quantityevent="30"



The data i want is the list of ingredientname and its total ingredientquantity for any single event
 
i want to create seperate html pages for each event with the ingredientname and total ingredientquantity required.

the total ingredientquantity should take care of quantityevent value (that the number of persons)

how to do the query in django to get the list of ingredientname and its total ingredientquantity

MenuPosition.objects.select_related('menurecipe').filter(menu__name="evening prasad")[0].menurecipe.recipe_positions.all()


**************************

volume_quantity = None

volume_quantity is not None or volume_quantity <=0
{TypeError}'<=' not supported between instances of 'NoneType' and 'int'

volume_quantity is not None and volume_quantity <=0
False

***********************

"""
