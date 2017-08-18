from django.shortcuts import render
from .models import Recipe, RecipePosition
from ingredients.models import Ingredient
from .forms import RecipeForm, RecipePoistionForm, RecipeForm2CreateFormSetHelper, RecipeForm2, RecipeForm2FormSet, RecipePositionCreateFormSetHelper, RecipeForm23CreateFormSetHelper
from ingredients.forms import IngredientForm, ExampleFormSetHelper, IngredientCreateFormSetHelper, IngredientForm2, RecipeIngredientFormSetHelper, IngredientForm3, RecipeIngredientFormSetHelper2
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Count, Value, Sum
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from tags.models import Tag
from django.forms import formset_factory
from django.forms import modelformset_factory
from django.forms import inlineformset_factory
import datetime
from django.forms import BaseModelFormSet
from django.db.models import Case, When



def recipe_testing(request,slug=None):

	#form to create an recipes
	form = RecipeForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		form.save_m2m()
		# message success
		messages.success(request, "Successfully Created", extra_tags='alert')
		#print(form.cleaned_data)
		return HttpResponseRedirect('')
	#context variables passed to the recipes
	context = {
		"form": form,
	}

	return render(request, "recipe_testing.html", context)


def ingredient_recipe_update(request,slug=None):
	recipe = get_object_or_404(Recipe, slug=slug)
	recipepositions = recipe.recipe_positions.all()
	pk_list = recipepositions.values_list('ingredient_id',flat=True)
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
	ingredients_dictinct = Ingredient.objects.filter(pk__in=pk_list).order_by(preserved)

	#ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe=recipe).distinct()

	#ingredients_dictinct = Ingredient.objects.filter(id__in=recipepositions.values('ingredient_id')) #this will not give in the same order

	IngredientFormSet = modelformset_factory(Ingredient, form=IngredientForm2, extra=0)
	


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
		"recipe":recipe
	}
	
	print(request.__dict__)
	return render(request, "recipe_ingredient_update.html", context)

@login_required
def recipe_ingredients_formset_update(request,slug=None):
	instance = get_object_or_404(Recipe.objects.prefetch_related('recipe_positions__volume_unit','recipe_positions__mass_unit','recipe_positions__pieces_unit','recipe_positions__ingredient'), slug=slug)
	object_list=instance.recipe_positions.all()
	RecipeIngredientsFormSet = inlineformset_factory(Recipe,RecipePosition,form=RecipePoistionForm,  can_delete=True, extra=5)
	if request.method == "POST":
		formset = RecipeIngredientsFormSet(request.POST, request.FILES, instance=instance)
		helper = RecipePositionCreateFormSetHelper()
		if formset.is_valid():
			formset.save()
			# Do something. Should generally end with a redirect. For example:
			messages.success(request, "Successfully Updated", extra_tags='alert')
			return HttpResponseRedirect('')
	else:
		formset = RecipeIngredientsFormSet(instance=instance)
		helper = RecipePositionCreateFormSetHelper()

	context = {
		"instance":instance,
		"formset":formset,
		"helper":helper,
		"object_list":object_list,
		"url":instance.get_absolute_url_recipe_update_inline_bulk_ingredients()
		}

	return render(request, 'recipe_recipositions_bulk_edit.html', context)


@login_required
def recipe_list_testing1(request):
	return render(request, "recipe_formset_update.html")

@login_required
def recipe_list(request):


	try:
		item1 = request.GET.get("item1")
		print(item1)
	except:
		item1 = False

	try:
		item2 = request.GET.get("item2")
		print(item2)
	except:
		item2 = False

	try:
		sort1 = request.GET.get("sort1")
	except:
		sort1 = False

	try:
		sort2 = request.GET.get("sort2")
	except:
		sort2 = False

	try:
		count = int(request.GET.get("count"))
	except:
		count = 10

	sort2_dict = {
	"ingredient": 'lower(ingredients_ingredient.name)',
	"recipeposition":'lower(recipes_recipeposition.name)',
	"name": "lower_name1",
	"-name": "-lower_name1",
	"sequence_number":"sequence_number",
	"-sequence_number":"-sequence_number",
	}


	if item2 and sort2:
		prefetch1 = Prefetch('recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit').extra(select={'lower_name1':sort2_dict[item2]}).order_by(sort2_dict[sort2]))
	else:
		prefetch1 = Prefetch('recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit').order_by('sequence_number'))


	print(prefetch1)
	queryset_list = (Recipe.objects
		.prefetch_related(
			prefetch1,
			Prefetch('tags',queryset=Tag.objects.order_by('name')))
		.select_related('mass_unit','volume_unit','pieces_unit').all())
	
	sort1_dict = {
		"name":"lower_name",
		"-name":"-lower_name",
		"id":"pk",
		"-id":"-pk",
		"-updated":"-updated",
		"updated":"updated",
		}


	if item1 and sort1 and sort1 not in ["cost","-cost","cost_liter","-cost_liter","cost_kg","-cost_kg","cost_pcs","-cost_pcs"]:
		queryset_list = queryset_list.extra(select={'lower_name':'lower(recipes_recipe.name)'}).order_by(sort1_dict[sort1])
	else:
		queryset_list = queryset_list.extra(select={'lower_name':'lower(recipes_recipe.name)'}).order_by('lower_name')

	
	# the reason for doing the below is because fitler does not work on sorted lists
	query = request.GET.get("q")
	if query and sort1 == "cost":
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))
		queryset_list = sorted(queryset_list, key=lambda a: a.const_total_cost_recipe())
	elif query and sort1 == "-cost":
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))
		queryset_list = sorted(queryset_list, key=lambda a: a.const_total_cost_recipe(), reverse=True)
	elif query and sort1 == "cost_liter":
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[2]['basic']['cost'])
	elif query and sort1 == "-cost_liter":
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[2]['basic']['cost'], reverse=True)
	elif query and sort1 == "cost_kg":
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[1]['basic']['cost'])
	elif query and sort1 == "-cost_kg":
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[1]['basic']['cost'], reverse=True)
	elif query and sort1 == "cost_pcs":
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[0]['basic']['cost'])
	elif query and sort1 == "-cost_pcs":
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[0]['basic']['cost'], reverse=True)
	elif query:
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))

	if sort1 == 'cost':
		queryset_list = sorted(queryset_list, key=lambda a: a.const_total_cost_recipe())
	elif sort1 == '-cost':
		queryset_list = sorted(queryset_list, key=lambda a: a.const_total_cost_recipe(), reverse=True)
	elif sort1 == 'cost_liter':
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[1]['basic']['cost'])
	elif sort1 == '-cost_liter':
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[1]['basic']['cost'], reverse=True)
	elif sort1 == 'cost_kg':
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[0]['basic']['cost'])
	elif sort1 == '-cost_kg':
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[0]['basic']['cost'], reverse=True)
	elif sort1 == 'cost_pcs':
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[2]['basic']['cost'])
	elif sort1 == '-cost_pcs':
		queryset_list = sorted(queryset_list, key=lambda a: a.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[2]['basic']['cost'], reverse=True)






	#pagination
	paginator = Paginator(queryset_list, count) # Show 25 contacts per page
	page_request_var = "page"
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
		#MYQQ SELECT COUNT(*) AS "__count" FROM "recipes_recipe"
		#MYQQRR 95
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)



	#form to create an recipes
	form = RecipeForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		form.save_m2m()
		# message success
		messages.success(request, "Successfully Created", extra_tags='alert')
		#print(form.cleaned_data)
		return HttpResponseRedirect('')
	#context variables passed to the recipes
	context = {
		"object_list":queryset,
		"form": form,
		"page_request_var": page_request_var,
		"count": count,
	}
	print ("near context")

	return render(request, "recipe_list.html", context)


@login_required
def recipe_formset_update(request):


	try:
		item1 = request.GET.get("item1")
	except:
		item1 = False

	try:
		sort1 = request.GET.get("sort1")
	except:
		sort1 = False

	try:
		count = int(request.GET.get("count"))
	except:
		count = 10

	
	prefetch1 = Prefetch('recipe_positions', queryset=RecipePosition.objects.select_related('ingredient','mass_unit','volume_unit','pieces_unit').order_by('sequence_number'))


	print(prefetch1)
	queryset_list = (Recipe.objects
		.prefetch_related(
			prefetch1,
			Prefetch('tags',queryset=Tag.objects.order_by('name')))
		.select_related('mass_unit','volume_unit','pieces_unit').all())
	
	sort1_dict = {
		"name":"lower_name",
		"-name":"-lower_name",
		"id":"pk",
		"-id":"-pk",
		"-updated":"-updated",
		"updated":"updated",
		}


	if item1 and sort1:
		queryset_list = queryset_list.extra(select={'lower_name':'lower(recipes_recipe.name)'}).order_by(sort1_dict[sort1])
	else:
		queryset_list = queryset_list.extra(select={'lower_name':'lower(recipes_recipe.name)'}).order_by('lower_name')

	
	# the reason for doing the below is because fitler does not work on sorted lists
	query = request.GET.get("q")

	if query:
		queryset_list = queryset_list.filter(
			Q(name__icontains=query))

	#pagination
	paginator = Paginator(queryset_list, count) # Show 25 contacts per page
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

	RecipeFormSet = modelformset_factory(Recipe, form=RecipeForm2, can_delete=True, extra=0)

	#form to create an ingredient
	if request.method == 'POST':
		formset = RecipeFormSet(request.POST or None, request.FILES or None)
		helper = RecipeForm2CreateFormSetHelper()
		if formset.is_valid():
			formset.save()
			messages.success(request, "Successfully Updated", extra_tags='alert')
			return HttpResponseRedirect('')
	else:
		formset = RecipeFormSet(queryset=queryset.object_list)
		helper = RecipeForm2CreateFormSetHelper()

	context = {
		"formset":formset,
		"object_list": queryset,
		"helper":helper,
		"page_request_var": page_request_var,
	}
	
	print(request.__dict__)
	return render(request, "recipe_formset_update.html", context)


@login_required
def recipe_formset_create(request):

	RecipeFormSet = modelformset_factory(Recipe, form=RecipeForm2, extra=10)

	print('%s-%s' %(request.method,"request.method"))

	if request.method == 'POST':
		formset = RecipeFormSet(request.POST or None, request.FILES or None)
		helper = RecipeForm23CreateFormSetHelper()
		if formset.is_valid():
			formset.save()
			messages.success(request, "Successfully Created", extra_tags='alert')
			return HttpResponseRedirect('')
			#return HttpResponseRedirect(reverse("ingredients:list"))
	else:
		formset = RecipeFormSet(queryset=Recipe.objects.none())
		helper = RecipeForm23CreateFormSetHelper()
		print('%s-%s' %(formset.errors,"formset.errors"))


	print('%s' %("before context"))
	context = {
		"formset":formset,
		"helper":helper
	}
	
	print(request.__dict__)
	return render(request, "recipe_formset_create.html", context)


@login_required
def recipe_detail(request, slug=None):

	instance = get_object_or_404(Recipe, slug=slug)
	object_list=instance.recipe_positions.all()
	form = RecipePoistionForm(initial={'primary_unit': "ltr"})	
	form = RecipePoistionForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		recipe_obj = instance
		ingredientname_obj = form.cleaned_data.get("ingredient")
		name_obj = form.cleaned_data.get("name")
		# if not name_obj:
		# 	#print("not name_obj")
		# else:
		# 	#print("yes name_obj")

		if not name_obj:
			name_obj = form.cleaned_data.get('ingredient').name
			#print("not name obj")
			#print(name_obj)
		# else:
		# 	#print("yes name_obj")
		
		instance = form.save(commit=False)
		instance.recipe = recipe_obj
		instance.name_obj = name_obj
		instance.save()
		return HttpResponseRedirect(instance.get_absolute_url_detail())
	# 	new_ingredient, created = RecipePosition.objects.get_or_create(
	# 						defaults = {
	# 						'recipe' : recipe_obj,
	# 						'name' : name_obj,
	# 						'ingredient' : form.cleaned_data.get('ingredient'),
	# 						'primary_unit' : form.cleaned_data.get('primary_unit'),
	# 						'mass_unit' : form.cleaned_data.get('mass_unit'),
	# 						'mass_quantity' : form.cleaned_data.get('mass_quantity'),
	# 						'volume_unit' : form.cleaned_data.get('volume_unit'),
	# 						'volume_quantity' : form.cleaned_data.get('volume_quantity'),
	# 						'pieces_unit' : form.cleaned_data.get('pieces_unit'),
	# 						'pieces_quantity' : form.cleaned_data.get('pieces_quantity'),
	# 						'cooking_notes' : form.cleaned_data.get('cooking_notes'),
	# 						}
	# 					)
		
	# 	#print('%s::%s-%s' %(recipe_obj.name,name_obj,form.cleaned_data.get('ingredient').name))
	# 	#print(new_ingredient)

	# 	if created is False:
	# 		messages.error(request, "<p>Ingredient already exists</p>", extra_tags='html_safe error text-warning alert bg-warning alert-warning')
	# 		#print("Ingredient already exists")
	# 	else:
	# 		return HttpResponseRedirect(instance.get_absolute_url_detail())
	# else:
	# 	print('%s-%s' %(instance.name,"form not valid"))
	
	context = {
		"instance": instance,
		"form":form,
		"object_list": object_list,
	}
	return render(request, "recipes_detail.html", context)


@login_required
def recipe_update(request, slug=None):
	instance = get_object_or_404(Recipe, slug=slug)
	form = RecipeForm(request.POST or None, request.FILES or None,instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		next = request.POST.get('next', '/')
		return HttpResponseRedirect(next)
		#messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
		#return HttpResponseRedirect(instance.get_absolute_url_detail())

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "recipes_update.html", context)


@login_required
def recipe_confirm(request,slug=None):
	instance = get_object_or_404(Recipe, slug=slug)
	context = {
		"instance": instance,
		"name": instance.name
	}
	return render(request, "recipes_confirm_delete.html", context)


@login_required
def recipe_delete(request, slug=None):
	instance = get_object_or_404(Recipe, slug=slug)
	instance.delete()
	messages.success(request, "Successfully deleted", extra_tags='alert')
	return redirect("recipes:list")




@login_required
def recipeposition_update(request, slug=None):
	instance = get_object_or_404(RecipePosition, recipeposition_slug=slug)
	form = RecipePoistionForm(request.POST or None, request.FILES or None,instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Successfully Updated", extra_tags='alert')
		next = request.POST.get('next', '/')
		return HttpResponseRedirect(next)
		#return HttpResponseRedirect(instance.recipe.get_absolute_url_detail())
		#return HttpResponseRedirect(reverse("recipes:list"))

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "recipes_update.html", context)


@login_required
def recipeposition_confirm(request,slug=None):
	instance = get_object_or_404(RecipePosition, recipeposition_slug=slug)
	context = {
		"instance": instance,
		"name": instance.ingredient.name
	}
	return render(request, "recipes_confirm_delete.html", context)

@login_required
def recipeposition_delete(request, slug=None):
	instance = get_object_or_404(RecipePosition, recipeposition_slug=slug)
	recipe = instance.recipe
	instance.delete()
	messages.success(request, "Successfully deleted", extra_tags='alert')
	return HttpResponseRedirect(recipe.get_absolute_url_detail())