from django.shortcuts import render, get_object_or_404, redirect
from .models import Ingredient
from .forms import IngredientForm, ExampleFormSetHelper, IngredientCreateFormSetHelper, IngredientForm2, IngredientForm31,RecipeIngredientFormSetHelper, IngredientForm21, IngredientCreateFormSetHelper2
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.utils.http import is_safe_url
from django.forms import formset_factory
from django.forms import modelformset_factory
from django.forms import inlineformset_factory
from typeofingredient.models import TypeOfIngredient
from django.db.models import Case, When
from django.utils import timezone
#http://stackoverflow.com/questions/35894990/django-how-to-return-to-previous-url
@login_required
def ingredients_densities_list(request):

	ingredients_dictinct = Ingredient.objects.all().extra(select={'lower_name':'lower(name)'}).order_by('lower_name')

	pk_list = [o.id for o in ingredients_dictinct if o.ingredient_qty_rate_cost_default_ingredient_all_recipes()['density_factor_exists']]

	#queryset_list = sorted(ingredients_dictinct, key=lambda a: a.ingredient_qty_rate_cost_default_ingredient_all_recipes()['density_factor_exists'], reverse=True)

	#pk_list=[]
	# for query in queryset_list:

	# 	pk_list.append(query.id)

	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
	ingredients_dictinct = Ingredient.objects.filter(pk__in=pk_list).order_by(preserved)

	context = {
		"ingredients":ingredients_dictinct,
	}
	
	print(request.__dict__)
	return render(request, "ingredients_densities_list.html", context)


@login_required
def ingredient_density_formset_create(request):

	ingredients_dictinct = Ingredient.objects.all().extra(select={'lower_name':'lower(name)'}).order_by('lower_name')

	pk_list = [o.id for o in ingredients_dictinct if o.ingredient_qty_rate_cost_default_ingredient_all_recipes()['density_factor_exists']]

	#queryset_list = sorted(ingredients_dictinct, key=lambda a: a.ingredient_qty_rate_cost_default_ingredient_all_recipes()['density_factor_exists'], reverse=True)

	#pk_list=[]
	# for query in queryset_list:

	# 	pk_list.append(query.id)

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
			return HttpResponseRedirect(reverse("ingredients:formsetdensity"))
	else:
		formset = IngredientFormSet(queryset=ingredients_dictinct)
		helper = RecipeIngredientFormSetHelper()

	context = {
		"formset":formset,
		"helper":helper,
	}
	
	print(request.__dict__)
	return render(request, "ingredients_bulk_edit_density.html", context)


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
def ingredient_list(request):

	
	try:
		sort = request.GET.get("sort")
	except:
		sort = False

	try:
		count = int(request.GET.get("count"))
	except:
		count = 25


	sort1_dict = {
		"name":"lower_name",
		"-name":"-lower_name",
		"id":"pk",
		"-id":"-pk",
		"-date":"-updated",
		"date":"updated",
		"type":"lower_name",
		"-type":"-lower_name"
		}
	
	if sort and sort not in ('type','-type'):
		queryset_list = Ingredient.objects.all().select_related('typeofingredient').extra(select={'lower_name':'lower(ingredients_ingredient.name)'}).order_by(sort1_dict[sort])
	elif sort and sort in ('type','-type'):
		queryset_list = Ingredient.objects.all().select_related('typeofingredient')	.extra(select={'lower_name':'lower(typeofingredient_typeofingredient.name)'}).order_by(sort1_dict[sort])
	else:
		queryset_list = Ingredient.objects.all().extra(select={'lower_name':'lower(name)'}).order_by('lower_name')

	#search logic
	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
			Q(name__icontains=query)).distinct()
	
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



	#form to create an ingredient
	form = IngredientForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False) #use commit = false if we have to add few more parameters before saving
		instance.save()
		# message success
		messages.success(request, "Successfully Created", extra_tags='alert')
		#print(form.cleaned_data) # to print to the terminal
		return HttpResponseRedirect(reverse("ingredients:list"))  # add this so that the form will no longer contain the data.

	#context variables passed to the ingredients
	context = {
		"object_list":queryset,
		"form": form,
		"page_request_var": page_request_var,
	}
	
	print(request.__dict__)
	return render(request, "ingredients_list.html", context)

@login_required
def ingredient_formset_update(request):

	try:
		sort = request.GET.get("sort")
	except:
		sort = False

	try:
		count = int(request.GET.get("count"))
	except:
		count = 25


	sort1_dict = {
		"name":"lower_name",
		"-name":"-lower_name",
		"id":"pk",
		"-id":"-pk",
		"-date":"-updated",
		"date":"updated",
		"type":"lower_name",
		"-type":"-lower_name"
		}
	
	if sort and sort not in ('type','-type'):
		queryset_list = Ingredient.objects.all().select_related('typeofingredient').extra(select={'lower_name':'lower(ingredients_ingredient.name)'}).order_by(sort1_dict[sort])
	elif sort and sort in ('type','-type'):
		queryset_list = Ingredient.objects.all().select_related('typeofingredient').extra(select={'lower_name':'lower(typeofingredient_typeofingredient.name)'}).order_by(sort1_dict[sort])
	else:
		queryset_list = Ingredient.objects.all().select_related('typeofingredient').extra(select={'lower_name':'lower(ingredients_ingredient.name)'}).order_by('lower_name')

	#search logic
	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
			Q(name__icontains=query)).distinct()
	
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

	IngredientFormSet = modelformset_factory(Ingredient, form=IngredientForm2, can_delete=True, extra=0)



	#form to create an ingredient
	if request.method == 'POST':
		formset = IngredientFormSet(request.POST or None, request.FILES or None)
		helper = ExampleFormSetHelper()
		if formset.is_valid():
			formset.save()
			messages.success(request, "Successfully Updated", extra_tags='alert')
			return HttpResponseRedirect(reverse("ingredients:formsetedit"))
	else:
		formset = IngredientFormSet(queryset=queryset.object_list)
		helper = ExampleFormSetHelper()

	context = {
		"formset":formset,
		"object_list": queryset,
		"helper":helper,
		"page_request_var": page_request_var,
	}
	
	print(request.__dict__)
	return render(request, "ingredient_formset_update.html", context)


@login_required
def ingredient_formset_create(request):

	IngredientFormSet = modelformset_factory(Ingredient, form=IngredientForm21, extra=10)

	print('%s-%s' %(request.method,"request.method"))



	if request.method == 'POST':
		formset = IngredientFormSet(request.POST or None, request.FILES or None)

		helper = IngredientCreateFormSetHelper2()
		if formset.is_valid():
			formset.save()
			messages.success(request, "Successfully Created", extra_tags='alert')
			return HttpResponseRedirect(reverse("ingredients:formsetcreate"))
			#return HttpResponseRedirect(reverse("ingredients:list"))
	else:
		formset = IngredientFormSet(queryset=Ingredient.objects.none())
		helper = IngredientCreateFormSetHelper2()
		print('%s-%s' %(formset.errors,"formset.errors"))


	print('%s' %("before context"))
	context = {
		"formset":formset,
		"helper":helper
	}
	
	print(request.__dict__)
	return render(request, "ingredient_formset_create.html", context)


@login_required
def ingredient_update(request, slug=None):
	instance = get_object_or_404(Ingredient, slug=slug)
	form = IngredientForm(request.POST or None, request.FILES or None,instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request,"Successfully Updated", extra_tags='alert')
		next = request.POST.get('next', '/')
		return HttpResponseRedirect(next)
		#return HttpResponseRedirect(reverse("ingredients:list"))

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "ingredients_update.html", context)

@login_required
def ingredient_confirm(request,slug=None):
	instance = get_object_or_404(Ingredient, slug=slug)
	context = {
		"instance": instance,
	}
	return render(request, "ingredients_confirm_delete.html", context)

@login_required
def ingredient_delete(request, slug=None):
	instance = get_object_or_404(Ingredient, slug=slug)
	instance.delete()
	messages.success(request, "Successfully deleted", extra_tags='alert')
	return redirect("ingredients:list")
