from django.shortcuts import render, get_object_or_404, redirect
from .models import TypeOfIngredient
from .forms import TypeOfIngredientForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required


@login_required
def typeofingredient_list(request):
	queryset_list = TypeOfIngredient.objects.all()

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



	#form to create an ingredient
	form = TypeOfIngredientForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False) #use commit = false if we have to add few more parameters before saving
		instance.save()
		# message success
		messages.success(request, "Successfully Created")
		#print(form.cleaned_data) # to print to the terminal
		return HttpResponseRedirect(reverse("typeofingredient:list"))  # add this so that the form will no longer contain the data.
	

	#context variables passed to the typeofingredient
	context = {
		"object_list":queryset,
		"form": form,
		"page_request_var": page_request_var
	}
	

	return render(request, "typeofingredient_list.html", context)

@login_required
def typeofingredient_update(request, slug=None):
	instance = get_object_or_404(TypeOfIngredient, slug=slug)
	form = TypeOfIngredientForm(request.POST or None, request.FILES or None,instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
		return HttpResponseRedirect(reverse("typeofingredient:list"))

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "typeofingredient_update.html", context)

@login_required
def typeofingredient_confirm(request,slug=None):
	instance = get_object_or_404(TypeOfIngredient, slug=slug)
	context = {
		"instance": instance,
	}
	return render(request, "typeofingredient_confirm_delete.html", context)


@login_required
def typeofingredient_delete(request, slug=None):
	instance = get_object_or_404(TypeOfIngredient, slug=slug)
	instance.delete()
	messages.success(request, "Successfully deleted")
	return redirect("typeofingredient:list")
