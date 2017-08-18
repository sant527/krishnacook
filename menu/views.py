from django.shortcuts import render
from itertools import chain
from .models import Menu, MenuPosition, IngredientCustom
from .forms import MenuForm, MenuPoistionForm, MenuPositionCreateFormSetHelper, IngredientCustomForm, MenuCustomIngredientFormSetHelper
from ingredients.forms import IngredientForm2, RecipeIngredientFormSetHelper, IngredientForm31
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, CharField, PositiveSmallIntegerField
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Count, Value, Sum
from recipes.models import RecipePosition, Recipe
from ingredients.models import Ingredient
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.forms import formset_factory
from django.forms import modelformset_factory
from django.forms import inlineformset_factory
from django.db.models import Case, When
from django.utils import timezone


def menu_ingredient_custom_clear_all_values(request,slug=None):
	instance = get_object_or_404(Menu, slug=slug)
	custom_ingredients = instance.menu_positions_customingredients.all().update(
									rate=0,
									density_kg_per_lt = 0,
									density_pcs_per_kg = 0,
									density_pcs_per_lt =0,
									updated = timezone.now()
									)
	return HttpResponseRedirect(reverse("menus:list"))
	#return render(request, "clear_custom_ingredient.html")


def menu_ingredient_custom_sync_with_default(request,slug=None):
	instance = get_object_or_404(Menu, slug=slug)
	custom_ingredients = instance.menu_positions_customingredients.select_related('ingredient').all()
	for custom_ingredient in custom_ingredients:
		if custom_ingredient.rate <= 0:
			custom_ingredient.rate = custom_ingredient.ingredient.rate
		if custom_ingredient.density_kg_per_lt <= 0:
			custom_ingredient.density_kg_per_lt = custom_ingredient.ingredient.density_kg_per_lt
		if custom_ingredient.density_pcs_per_kg <= 0:
			custom_ingredient.density_pcs_per_kg = custom_ingredient.ingredient.density_pcs_per_kg
		if custom_ingredient.density_pcs_per_lt <= 0:
			custom_ingredient.density_pcs_per_lt = custom_ingredient.ingredient.density_pcs_per_lt
		custom_ingredient.save()
	return HttpResponseRedirect(reverse("menus:list"))







def menu_testing2(request,slug=None):
	instance = get_object_or_404(Menu.objects.all().prefetch_related(Prefetch('menu_positions_customingredients',queryset=IngredientCustom.objects.select_related('ingredient','ingredient__typeofingredient'))),slug=slug)
	

	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')
	objects_list = instance.menu_positions_customingredients.filter(ingredient__in=ingredients_dictinct).all()

	MenuCustomIngredientFormSet = modelformset_factory(IngredientCustom, form=IngredientCustomForm, can_delete=False, extra=0)

	#form to create an ingredient
	if request.method == 'POST':
		formset = MenuCustomIngredientFormSet(request.POST or None, request.FILES or None)
		helper = MenuCustomIngredientFormSetHelper()
		if formset.is_valid():
			formset.save()
			messages.success(request, "Successfully Updated", extra_tags='alert')
			return HttpResponseRedirect('')
	else:
		formset = MenuCustomIngredientFormSet(queryset=objects_list)
		helper = MenuCustomIngredientFormSetHelper()

	context = {
		"instance":instance,
		"formset":formset,
		"helper":helper,
		"url":instance.get_absolute_url_menu_update_inline_bulk_recipes()
		}

	return render(request, 'menus_testing2.html', context)

def menu_testing(request,slug=None):
	instance = get_object_or_404(Menu, slug=slug)
	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
	
		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())

	context = {
		"instance": instance,
		"form":form,
	}

	return render(request, 'menus_testing.html', context)	



@login_required
def menu_ingredient_custom_recipe_ingredient(request,slug=None):
	queryset_list = (Menu.objects
				.prefetch_related(
					Prefetch('menu_positions',queryset=MenuPosition.objects.select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')),
					Prefetch('menu_positions__menurecipe__recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit')),
					Prefetch('menu_positions_customingredients',queryset=IngredientCustom.objects.select_related('ingredient','ingredient__typeofingredient')),
					)
				.all()
				.extra(select={'lower_name':'lower(menu_menu.name)'}).order_by('lower_name'))
	#print("test")
	instance = get_object_or_404(queryset_list, slug=slug)
	object_list=instance.menu_positions.all()
	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient','name')


	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}

	return render(request, 'menus_detail_custom_and_default_ingredients.html', context)	





@login_required
def menu_ingredient_custom_recipe_recipe(request,slug=None):
	queryset_list = (Menu.objects
				.prefetch_related(
					Prefetch('menu_positions',queryset=MenuPosition.objects.select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')),
					Prefetch('menu_positions__menurecipe__recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit')),
					Prefetch('menu_positions_customingredients',queryset=IngredientCustom.objects.select_related('ingredient','ingredient__typeofingredient')),
					)
				.all()
				.extra(select={'lower_name':'lower(menu_menu.name)'}).order_by('lower_name'))
	#print("test")
	instance = get_object_or_404(queryset_list, slug=slug)
	object_list=instance.menu_positions.all()
	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient','name')


	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}

	return render(request, 'menus_detail_custom_and_default_recipes.html', context)	




@login_required
def menu_ingredient_custom_recipe_report(request,slug=None):
	queryset_list = (Menu.objects
				.prefetch_related(
					Prefetch('menu_positions',queryset=MenuPosition.objects.select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')),
					Prefetch('menu_positions__menurecipe__recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit')),
					Prefetch('menu_positions_customingredients',queryset=IngredientCustom.objects.select_related('ingredient','ingredient__typeofingredient')),
					)
				.all()
				.extra(select={'lower_name':'lower(menu_menu.name)'}).order_by('lower_name'))
	#print("test")
	instance = get_object_or_404(queryset_list, slug=slug)
	object_list=instance.menu_positions.all()
	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient','name')


	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}

	return render(request, 'menus_detail_custom_and_default.html', context)	

@login_required
def menu_ingredient_custom_list(request,slug=None):
	instance = get_object_or_404(Menu.objects.all().prefetch_related(Prefetch('menu_positions_customingredients',queryset=IngredientCustom.objects.select_related('ingredient','ingredient__typeofingredient'))),slug=slug)

	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')
	for ingredient in ingredients_dictinct:
		new_ingredient, created = IngredientCustom.objects.get_or_create(
							menu = instance,
							ingredient = ingredient,
							defaults = {
								"rate":0,
								"density_kg_per_lt":0,
								"density_pcs_per_kg":0,
								"density_pcs_per_lt":0,
							}
						)


	objects_list = instance.menu_positions_customingredients.filter(ingredient__in=ingredients_dictinct).all()


	context = {
	'objects_list' : objects_list,
	}

	return render(request, 'menu_customingredients_list.html', context)



@login_required
def menu_ingredient_custom_inlineformset_bulk_edit(request,slug=None):
	#instance = get_object_or_404(Menu.objects.all().prefetch_related(Prefetch('menu_positions_customingredients',queryset=IngredientCustom.objects.select_related('ingredient','ingredient__typeofingredient'))),slug=slug)

	instance = get_object_or_404(Menu,slug=slug)
	

	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')
	objects_list = instance.menu_positions_customingredients.filter(ingredient__in=ingredients_dictinct).all()



	MenuCustomIngredientFormSet = modelformset_factory(IngredientCustom, form=IngredientCustomForm, can_delete=False, extra=0)

	#form to create an ingredient
	if request.method == 'POST':
		formset = MenuCustomIngredientFormSet(request.POST or None, request.FILES or None)
		helper = MenuCustomIngredientFormSetHelper()
		if formset.is_valid():
			formset.save()
			messages.success(request, "Successfully Updated", extra_tags='alert')
			return HttpResponseRedirect('')
	else:
		formset = MenuCustomIngredientFormSet(queryset=objects_list)
		helper = MenuCustomIngredientFormSetHelper()


	context = {
		"instance":instance,
		"formset":formset,
		"helper":helper,
		"url":instance.get_absolute_url_menu_update_inline_bulk_recipes()
		}

	return render(request, 'menus_customingredients_bulk_edit.html', context)


@login_required
def menu_ingredient_default_inlineformset_bulk_edit(request,slug=None):
	instance = get_object_or_404(Menu,slug=slug)
	

	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)

	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')

	queryset_list = sorted(ingredients_dictinct, key=lambda a: a.ingredient_qty_rate_cost_default_ingredient(instance)['density_factor_exists'], reverse=True)

	pk_list=[]
	for query in queryset_list:
		pk_list.append(query.id)

	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
	ingredients_dictinct = Ingredient.objects.filter(pk__in=pk_list).order_by(preserved)

	IngredientFormSet = modelformset_factory(Ingredient, form=IngredientForm31, extra=0)
	


	#form to create an ingredient
	if request.method == 'POST':
		formset = IngredientFormSet(request.POST or None, request.FILES or None)
		helper = RecipeIngredientFormSetHelper()
		if formset.is_valid():
			formset.save()
			messages.success(request, "Successfully Updated", extra_tags='alert')
			return HttpResponseRedirect(reverse("ingredients:formsetedit"))
	else:
		formset = IngredientFormSet(queryset=ingredients_dictinct)
		helper = RecipeIngredientFormSetHelper()

	context = {
		"formset":formset,
		"helper":helper,
		"instance":instance
	}
	
	print(request.__dict__)
	return render(request, "menus_default_ingredients_bulk_edit.html", context)


@login_required
def menu_recipe_formset_update(request,slug=None):
	instance = get_object_or_404(Menu,slug=slug)
	MenuRecipesFormSet = inlineformset_factory(Menu,MenuPosition,form=MenuPoistionForm,  can_delete=True, extra=5)

	if request.method == "POST":
		formset = MenuRecipesFormSet(request.POST, request.FILES, instance=instance)
		helper = MenuPositionCreateFormSetHelper()
		if formset.is_valid():
			for form in formset:
				delete = form.cleaned_data.get('DELETE')
				if not delete:
					if form.has_changed():
						if form.instance.pk is not None: #check for empty forms
							name = form.cleaned_data.get("name")
							menurecipe = form.cleaned_data.get('menurecipe')
							obj = MenuPosition.objects.filter(name=name,menurecipe=menurecipe).first()
							if obj is not None:
								if obj.pk == form.instance.pk:
									form.save()
									messages.success(request, "Successfully Updated", extra_tags='alert')
								else:
									messages.error(request, "<p>Cant have duplicate Menu Name</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
							else:
								form.save()
								messages.success(request, "Successfully Updated", extra_tags='alert')

						else:
							menu_obj = instance
							name_obj = form.cleaned_data.get("name")
							
							if not name_obj:
								name_obj = form.cleaned_data.get('menurecipe').name
						
							new_ingredient, created = MenuPosition.objects.get_or_create(
												menu = menu_obj,
												name = name_obj,
												defaults = {
													"menurecipe" : form.cleaned_data.get("menurecipe"),
													"persons" : form.cleaned_data.get("persons"),
													"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
													"consumption_grams" : form.cleaned_data.get("consumption_grams"),
													"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
													"recipe_notes" : form.cleaned_data.get("recipe_notes"),
												}
											)
							if created is False:
								messages.error(request, "<p>Cant have duplicate Menu Name</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
							else:
								messages.success(request, "Successfully Created", extra_tags='alert')
					
				else:
					instances = formset.save(commit=False)
					for obj in formset.deleted_objects:
						obj.delete()
					messages.success(request, "Successfully Deleted", extra_tags='alert')


			#formset.save()

			#*********************
			#the ingredient will not be deleted if the recipe is removed from the menu.
			recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
			ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('id')
			for ingredient in ingredients_dictinct:
				new_ingredient, created = IngredientCustom.objects.get_or_create(
								menu = instance,
								ingredient = ingredient,
								defaults = {
									"rate":0,
									"density_kg_per_lt":0,
									"density_pcs_per_kg":0,
									"density_pcs_per_lt":0,
								}
							)
			#*******************


			# Do something. Should generally end with a redirect. For example:
			#messages.success(request, "Successfully Updated", extra_tags='alert')
			return HttpResponseRedirect('')
	else:
		formset = MenuRecipesFormSet(instance=instance)
		helper = MenuPositionCreateFormSetHelper()

	context = {
		"instance":instance,
		"formset":formset,
		"helper":helper,
		"url":instance.get_absolute_url_menu_update_inline_bulk_recipes()
		}

	return render(request, 'menu_menupositions_bulk_edit.html', context)






@login_required
def menu_list(request):
	#queryset_list = Menu.objects.all()
	queryset_list = (Menu.objects
				.prefetch_related(
					Prefetch('menu_positions',queryset=MenuPosition.objects.select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')),
					Prefetch('menu_positions__menurecipe__recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit')),
					)
				.all()
				.extra(select={'lower_name':'lower(menu_menu.name)'}).order_by('lower_name'))


	#search logic
	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
			Q(name__icontains=query)).distinct()
	
	#pagination
	paginator = Paginator(queryset_list, 10) # Show 25 contacts per page
	page_request_var = "page"
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)



	#form to create an recipes
	form = MenuForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		# message success
		messages.success(request, "Successfully Created")
		#print(form.cleaned_data)
		return HttpResponseRedirect(reverse("menus:list"))
	

	#context variables passed to the recipes
	context = {
		"object_list":queryset,
		"form": form,
		"page_request_var": page_request_var
	}
	

	return render(request, "menus_list.html", context)

@login_required
def menu_detail(request, slug=None):
	queryset_list = (Menu.objects
				.prefetch_related(
					Prefetch('menu_positions',queryset=MenuPosition.objects.select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')),
					Prefetch('menu_positions__menurecipe__recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit')),
					)
				.all()
				.extra(select={'lower_name':'lower(menu_menu.name)'}).order_by('lower_name'))
	#print("test")
	instance = get_object_or_404(queryset_list, slug=slug)
	object_list=instance.menu_positions.all()

	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			#************************************
			recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
			ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')
			for ingredient in ingredients_dictinct:
				new_ingredient, created = IngredientCustom.objects.get_or_create(
								menu = instance,
								ingredient = ingredient,
								defaults = {
									"rate":ingredient.rate,
									"density_kg_per_lt":ingredient.density_kg_per_lt,
									"density_pcs_per_kg":ingredient.density_pcs_per_kg,
									"density_pcs_per_lt":ingredient.density_pcs_per_lt,
								}
							)
			#***************************************
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient','name')

	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}
	return render(request, "menus_detail.html", context)


@login_required
def menu_detail2(request, slug=None):
	queryset_list = (Menu.objects
				.prefetch_related(
					Prefetch('menu_positions',queryset=MenuPosition.objects.select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')),
					Prefetch('menu_positions__menurecipe__recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit')),
					)
				.all()
				.extra(select={'lower_name':'lower(menu_menu.name)'}).order_by('lower_name'))
	#print("test")
	instance = get_object_or_404(queryset_list, slug=slug)
	object_list=instance.menu_positions.all()

	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient','name')

	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}
	return render(request, "menus_detail2.html", context)

@login_required
def menu_detail_ingredient(request, slug=None):
	queryset_list = (Menu.objects
				.prefetch_related(
					Prefetch('menu_positions',queryset=MenuPosition.objects.select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')),
					Prefetch('menu_positions__menurecipe__recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit')),
					)
				.all()
				.extra(select={'lower_name':'lower(menu_menu.name)'}).order_by('lower_name'))
	#print("test")
	instance = get_object_or_404(queryset_list, slug=slug)
	object_list=instance.menu_positions.all()

	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient','name')

	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}
	return render(request, "menus_detail_ingredient.html", context)

@login_required
def menu_report(request, slug=None):
	queryset_list = (Menu.objects
				.prefetch_related(
					Prefetch('menu_positions',queryset=MenuPosition.objects.select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')),
					Prefetch('menu_positions__menurecipe__recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit')),
					)
				.all()
				.extra(select={'lower_name':'lower(menu_menu.name)'}).order_by('lower_name'))
	#print("test")
	instance = get_object_or_404(queryset_list, slug=slug)
	object_list=instance.menu_positions.all()
	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient','name')


	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}
	return render(request, "menus_report.html", context)


@login_required
def menu_print(request, slug=None):
	#print("test")
	instance = get_object_or_404(Menu, slug=slug)
	object_list=instance.menu_positions.all()
	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')

	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}
	return render(request, "menus_report.html", context)


@login_required
def menu_default_ingredients(request, slug=None):
	#print("test")
	instance = get_object_or_404(Menu, slug=slug)
	object_list=instance.menu_positions.all()
	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')

	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}
	return render(request, "menus_default_ingredients.html", context)


@login_required
def menu_default_recipes(request, slug=None):
	#print("test")
	instance = get_object_or_404(Menu, slug=slug)
	object_list=instance.menu_positions.all()
	form = MenuPoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		menu_obj = instance
		name_obj = form.cleaned_data.get("name")
		
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('menurecipe').name
		# else:
		# 	#print("yes name_obj")


		new_ingredient, created = MenuPosition.objects.get_or_create(
							menu = menu_obj,
							name = name_obj,
							defaults = {
								"menurecipe" : form.cleaned_data.get("menurecipe"),
								"persons" : form.cleaned_data.get("persons"),
								"consumption_milli_liters" : form.cleaned_data.get("consumption_milli_liters"),
								"consumption_grams" : form.cleaned_data.get("consumption_grams"),
								"consumption_pieces" : form.cleaned_data.get("consumption_pieces"),
								"recipe_notes" : form.cleaned_data.get("recipe_notes"),
							}
						)
		if created is False:
			messages.error(request, "<p>Recipe already Added	</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
		else:
			return HttpResponseRedirect(instance.get_absolute_url_detail())


	recipes = Recipe.objects.filter(menurecipe_positions__menu=instance)
	ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')

	context = {
		"ingredients_dictinct" : ingredients_dictinct,
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}
	return render(request, "menus_default_recipes.html", context)

@login_required
def menu_update(request, slug=None):
	#print("test")
	instance = get_object_or_404(Menu, slug=slug)
	form = MenuForm(request.POST or None, request.FILES or None,instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		#messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
		return HttpResponseRedirect(instance.get_absolute_url_detail())

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "recipes_update.html", context)


@login_required
def menu_confirm(request,slug=None):
	#print("test")
	instance = get_object_or_404(Menu, slug=slug)
	context = {
		"instance": instance,
		"name": instance.name
	}
	return render(request, "menus_confirm_delete.html", context)


@login_required
def menu_delete(request, slug=None):
	#print("test")
	instance = get_object_or_404(Menu, slug=slug)
	instance.delete()
	messages.success(request, "Successfully deleted")
	return redirect("menus:list")




@login_required
def menuposition_update(request, slug=None):
	#print("test")
	instance = get_object_or_404(MenuPosition, id=slug)
	form = MenuPoistionForm(request.POST or None, request.FILES or None,instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
		return HttpResponseRedirect(instance.menu.get_absolute_url_detail())
		#return HttpResponseRedirect(reverse("menus:list"))

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "menus_update.html", context)

@login_required
def menuposition_confirm(request,slug=None):
	#print("test")
	instance = get_object_or_404(MenuPosition, id=slug)
	context = {
		"instance": instance,
		"name": instance.menurecipe
	}
	return render(request, "menus_confirm_delete.html", context)

@login_required
def menuposition_delete(request, slug=None):
	#print("test")
	instance = get_object_or_404(MenuPosition, id=slug)
	menu = instance.menu

	instance.delete()
	messages.success(request, "Successfully deleted")
	return HttpResponseRedirect(menu.get_absolute_url_detail())

@login_required
def menu_total_ingredients(request,slug=None):
	instance = get_object_or_404(Menu, slug=slug)
	ingredientlist = instance.menu_ingredient.values('ingredientname','munit','typeofingredient__name') \
		.annotate(total_quantity_ingredient=Sum('quantitytotal'))\
		.order_by('typeofingredient','-total_quantity_ingredient')
	context = {
		"menurecipe_list": ingredientlist,
		"name": instance.name
		}
	#print(context)
	return render(request, "menus_total_ingredients.html", context)


# def menu_total_ingredients(request,slug=None):
# 	instance = get_object_or_404(Menu, slug=slug)
# 	final = MenuIngredients.objects.filter(menu=instance)
# 	menurecipelist = MenuPosition.objects.select_related('menurecipe').filter(menu__name=slug)
# 	for menurecipefor in menurecipelist:
# 		test =  menurecipefor.menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * menurecipefor.quantity)
# 		final = chain(final, test)

# 	#newfinal = final

# 	# item2 = menurecipelist[1]
# 	# # newfinal2 = item2.menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * item2.quantity, total_total=Value(item2.quantity, output_field=CharField()))

# 	# #print(item2.quantity)

# 	# newfinal2 = item2.menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * item2.quantity).annotate(total_total=Value(item2.quantity, output_field=PositiveSmallIntegerField()))
# 	# final = final | newfinal2


# 	# item1 = menurecipelist[0]
# 	# #newfinal1 = item1.menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * item1.quantity, total_total=Value(item1.quantity, output_field=CharField()))

# 	# #print(item1.quantity)


# 	# newfinal1 = item1.menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * item1.quantity).annotate(total_total=Value(item1.quantity, output_field=PositiveSmallIntegerField()))

# 	# final = final | newfinal1


# 	#newfinal = newfinal2|newfinal1 

# 	#newfinal = newfinal2
# 	#newfinal = newfinal1 


# 	##print(newfinal)

# 	context = {
# 		"menurecipe_list": final,
# 		"name": slug
# 	}
# 	#print(context)
# 	return render(request, "menus_total_ingredients.html", context)


"""
import itertools
final = RecipePosition.objects.none()
menurecipelist = MenuPosition.objects.select_related('menurecipe').filter(menu__name='lunch')
for menurecipefor in menurecipelist:
	test =  menurecipefor.menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * menurecipefor.quantity)
	final = itertools.chain(final, test)



final = Recipe.objects.none()
from django.db.models import F, Count, Value
from django.db.models import Q, CharField, PositiveSmallIntegerField
menurecipelist = MenuPosition.objects.select_related('menurecipe').filter(menu__name='lunch')
item2 = menurecipelist[1]
#print(item2.quantity)
newfinal2 = item2.menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * item2.quantity).annotate(total_total=Value(item2.quantity, output_field=PositiveSmallIntegerField()))
item1 = menurecipelist[0]
#print(item1.quantity)
newfinal1 = item1.menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * item1.quantity).annotate(total_total=Value(item1.quantity, output_field=PositiveSmallIntegerField()))


newfinal2.__dict__
newfinal1.__dict__
newfinal = newfinal2|newfinal1 
newfinal.__dict__


from django.db.models import F, Count, Value
from django.db.models import Q, CharField, PositiveSmallIntegerField
instance = Menu.objects.get(slug='breakfast')
testingredient = instance.menu_ingredient.annotate(total_total=Value('hare',output_field=CharField()))
for test in testingredient:
	#print(test.total_total)


testingredient = instance.menu_ingredient \
  .annotate(total_quantity_ingredient=Sum('quantitytotal'))
for test in testingredient:
	#print(test.ingredientname)
	#print(test.total_quantity_ingredient)



testingredient = instance.menu_ingredient.values('ingredientname','munit','typeofingredient__name') \
	.annotate(total_quantity_ingredient=Sum('quantitytotal'))\
	.order_by('typeofingredient','-total_quantity_ingredient')
for test in testingredient:
	for k, v in test.items():
		#print(k, v)

from django.db.models import F, Count, Value
from django.db.models import Q, CharField, PositiveSmallIntegerField
from django.shortcuts import render, get_object_or_404, redirect
instance = get_object_or_404(Menu, slug='lunch')
ingredientlist = instance.menuingredient_menu.values('ingredient__name','ingredient__typeofingredient__name','ingredient__munit','ingredient__rate') \
	.annotate(total_quantity_ingredient=Sum(F('menuposition__quantity')*F('ingredient_rate'))\
	.order_by('ingredient__typeofingredient__name')


instance.menuingredient_menu.values('ingredient__name','ingredient__typeofingredient__name','ingredient__munit','ingredient__rate')


from django.db.models import F, Count, Value
from django.db.models import Q, CharField, PositiveSmallIntegerField
from django.shortcuts import render, get_object_or_404, redirect
instance = get_object_or_404(Menu, slug='lunch')
MenuIngredients.objects.filter(menu=instance).delete()
menupositions = instance.menu_positions.all()
for menuposition in menupositions:
	menupostion_recipe_recipepositions = menuposition.menurecipe.recipe_positions.all()
	for recipeposition in menupostion_recipe_recipepositions:
		#print('inside loop')
		new_menuingredient, menucreated = MenuIngredients.objects.get_or_create(
			menuposition = menuposition,
			menu = instance,
			recipe = menuposition.menurecipe,
			recipeposition = recipeposition,
			ingredient = recipeposition.ingredient,
			)
		#print(recipeposition)
		#print(menucreated)


menupostion_recipe_recipepositions = menupositions[0].menurecipe.recipe_positions.all()
menupostion_recipe_recipepositions[0]


ingredientlist = instance.menuingredient_menu.values('ingredient__name','ingredient__typeofingredient__name','ingredient__munit','recipeposition__quantity','menuposition__quantity') \
	.annotate(total_quantity_ingredient=Sum(F('menuposition__quantity')*F('recipeposition__quantity')))\
	.order_by('ingredient__typeofingredient__name')
ingredientlist



	ingredientlist = instance.menuingredient_menu.values('ingredient__name','ingredient__typeofingredient__name','ingredient__munit','ingredient__rate','recipeposition__quantity','menuposition__menurecipe__name','menuposition__quantity') \
		.annotate(total_quantity_ingredient=F('menuposition__quantity')*F('recipeposition__quantity'))\
		.annotate(total_cost=F('menuposition__quantity')*F('total_quantity_ingredient'))\
		.order_by('ingredient__typeofingredient__name','ingredient__name')





"""