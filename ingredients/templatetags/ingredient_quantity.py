from django import template
import arrow

register = template.Library()

@register.simple_tag
def ingredient_quantity_final_cost_based_on_type_of_ingredient(menu):
	return menu.ingredient_quantity_final_cost_based_on_type_of_ingredient()

@register.simple_tag
def typeofingredients_from_menu(menu):
	return menu.typeofingredients_from_menu()

@register.simple_tag
def  ingredient_quantity_for_the_menu(ingredient, menu):
	return ingredient.ingredient_quantity_for_the_menu(menu)

@register.simple_tag
def ingredient_quantity_final_cost_for_the_menu(menu):
	return menu.ingredient_quantity_final_cost_for_the_menu()

@register.simple_tag
def get_cost_per_bulk_units_and_kg_ltr_pcs_custom_ingredient_prices(recipe,menu):
	return recipe.get_cost_per_bulk_units_and_kg_ltr_pcs_custom_ingredient_prices(menu)

@register.simple_tag
def  ingredient_quantity_for_the_menu_recipe(ingredient, menupostion):
	return ingredient.ingredient_quantity_for_the_menu_recipe(menupostion)

@register.simple_tag
def  ingredient_quantity_bulk_units_for_the_menu_recipe(ingredient, menupostion):
	return ingredient.ingredient_quantity_bulk_units_for_the_menu_recipe(menupostion)

@register.simple_tag
def  ingredient_quantity_bulk_units_for_the_menu_recipe_multiply_with_menuposition_factor(ingredient, menupostion):
	return ingredient.ingredient_quantity_bulk_units_for_the_menu_recipe_multiply_with_menuposition_factor(menupostion)
	
@register.simple_tag
def ingredient_quantity_kg_ltr_pcs_for_the_menu_recipe_multiply_with_menuposition_factor(ingredient, menupostion):
	return ingredient.ingredient_quantity_kg_ltr_pcs_for_the_menu_recipe_multiply_with_menuposition_factor(menupostion)

@register.simple_tag
def get_all_quantity_with_bulk_units_dict_multiply_with_factor(recipeposition,factor):
	return recipeposition.get_all_quantity_with_bulk_units_dict_multiply_with_factor(factor)

@register.simple_tag
def cost_quantity_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(recipeposition,factor):
	return recipeposition.cost_quantity_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(factor)

@register.simple_tag
def get_cost_quantity_dict(recipeposition):
	return recipeposition.get_cost_quantity_dict()

@register.simple_tag
def get_cost_quantity_dict_custom_ingredient_mixed_density(recipeposition,menu):
	return recipeposition.get_cost_quantity_dict_custom_ingredient_mixed_density(menu)

@register.simple_tag
def get_cost_quantity_dict_custom_ingredient_custom_density(recipeposition,menu):
	return recipeposition.get_cost_quantity_dict_custom_ingredient_custom_density(menu)	

@register.simple_tag
def get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(recipeposition,factor):
	return recipeposition.get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(factor)

@register.simple_tag
def custom_cost_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(recipeposition,factor,menu):
	return recipeposition.custom_cost_get_all_quantity_with_kg_ltr_pcs_units_dict_multiply_with_factor(factor,menu)

@register.simple_tag
def cost_quantity_kg_ltr_pcs_units_dict_multiply_with_factor_custom_ingredient_mixed_density(recipeposition,factor,menu):
	return recipeposition.cost_quantity_kg_ltr_pcs_units_dict_multiply_with_factor_custom_ingredient_mixed_density(factor,menu)

@register.simple_tag
def get_mixed_density_custom_ingredient_with_factor(ingredient,menuposition):
	return ingredient.get_mixed_density_custom_ingredient_with_factor(menuposition)

@register.simple_tag
def get_mixed_density_custom_ingredient_with_factor2(ingredient,instance):
	return ingredient.get_mixed_density_custom_ingredient_with_factor(instance)


@register.simple_tag
def get_mixed_density_custom_ingredient(ingredient,menuposition):
	return ingredient.get_mixed_density_custom_ingredient(menuposition)


@register.simple_tag
def average_number_of_people_dict_custom_ingredient(menu):
	return menu.average_number_of_people_dict_custom_ingredient()

@register.simple_tag
def get_cost_of_the_recipe_custom_price_ingredient_factor_per_person(recipe,factor,menu,menuposition):
	return recipe.get_cost_of_the_recipe_custom_price_ingredient_factor_per_person(factor,menu,menuposition)

@register.simple_tag
def get_cost_of_the_recipe_custom_price_ingredient_factor(recipe,factor,menu):
	return recipe.get_cost_of_the_recipe_custom_price_ingredient_factor(factor,menu)

@register.simple_tag
def get_cost_of_the_recipe_custom_price_ingredient(recipe,menu):
	return recipe.get_cost_of_the_recipe_custom_price_ingredient(menu)

@register.simple_tag
def cost_for_given_quantity(ingredient,quantity):
	return ingredient.cost_for_given_quantity(quantity)


@register.simple_tag
def ingredient_get_cost_quantity_data(ingredient,menupostion):
	return ingredient.ingredient_get_cost_quantity_data(menupostion)

@register.simple_tag
def ingredient_get_cost_quantity_data_multiply_with_menuposition_factor(ingredient,menupostion):
	return ingredient.ingredient_get_cost_quantity_data_multiply_with_menuposition_factor(menupostion)

@register.simple_tag
def total_cost_ingredient(rate, quantity):
	return rate * quantity

@register.simple_tag
def  ingredient_menu_recipes(ingredient, menu):
	return ingredient.ingredient_menu_recipes(menu)


@register.simple_tag
def get_quantity_with_bulk_units_dict(ingredient,menupostion):
	return ingredient.get_quantity_with_bulk_units_dict(menupostion)

@register.simple_tag
def menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(ingredient,menupostion):
	return ingredient.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(menupostion)

@register.filter(name='zip')
def zip_lists(a, b):
  return zip(a, b)

@register.simple_tag
def zip_lists2(a, b):
  return zip(a, b)

@register.simple_tag
def zip_lists3(a,b,c):
	return zip(a,b,c)

@register.simple_tag
def zip_lists2_units(a,c):
	data = dict()
	data.update({"ml-ltr":1000})
	data.update({"g-kg":1000})
	data.update({"pcs":1})
	return zip(a,data.items(),c)

@register.simple_tag
def zip_lists4(a,b,c,d):
	return zip(a,b,c,d)

@register.simple_tag
def mvwith(a):
	return a

@register.filter
def ditem(dictionary):
	return dictionary.get(key)

@register.filter
def thuman(time):
	return arrow.get(time).humanize()

@register.filter
def dkey(dictionary, key):
	return dictionary.get(key)


@register.filter
def index(List, i):
	return List[int(i)]


@register.filter
def updatedtime(recipe):
	a = recipe.recipe_positions.order_by('-updated').first().updated
	b = recipe.updated
	if a > b:
		return arrow.get(a).humanize()
	else:
		return arrow.get(b).humanize()

@register.filter(name='times') 
def times(number):
	return range(number)




@register.simple_tag
def menu_get_custom_ingredient_rate(menu,ingredient):
	return menu.menu_get_custom_ingredient_rate(ingredient)

@register.simple_tag
def ingredient_quantity_for_the_menu_custom_ingredient(ingredient,menu):
	return ingredient.ingredient_quantity_for_the_menu_custom_ingredient(menu)

@register.simple_tag
def ingredient_quantity_final_cost_for_the_menu_custom_ingredient(menu):
	return menu.ingredient_quantity_final_cost_for_the_menu_custom_ingredient()

@register.simple_tag
def ingredient_quantity_final_cost_based_on_type_of_ingredient_custom_ingredient(menu):
	return menu.ingredient_quantity_final_cost_based_on_type_of_ingredient_custom_ingredient()


@register.simple_tag
def urlparams2(request):
	a=""
	if request.method == 'GET':
		if 'q' in request.GET and request.GET['q']:
			a=a+"&q="+request.GET['q']
		
		if 'count' in request.GET and request.GET['count']:
			a=a+"&count="+request.GET['count']
	return a


@register.simple_tag
def urlparams(request, *args):
	b = ""
	for key, value in request.GET.items():
		a = 0
		for arg in args:
			if key==arg:
				a=a+1
		if a == 0:
			b=b+"&"+key+"="+value
	return b

@register.simple_tag
def list_factor_qty_unit_bulk_and_kg_ltr_pcs_list_recipeposition(recipeposition,factor):
	return recipeposition.list_factor_qty_unit_bulk_and_kg_ltr_pcs_list_recipeposition(factor)

@register.simple_tag
def dict_factor_qty_unit_density_bulk_and_kg_ltr_pcs_list_recipeposition(recipeposition,factor):
	return recipeposition.dict_factor_qty_unit_density_bulk_and_kg_ltr_pcs_list_recipeposition(factor)

@register.simple_tag
def list_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe(recipe,factor):
	return recipe.list_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe(factor)

@register.simple_tag
def dict_factor_total_cost_recipe(recipe,factor):
	return recipe.dict_factor_total_cost_recipe(factor)


@register.simple_tag
def dict_factor_custom_total_cost_recipe(recipe,factor):
	return recipe.dict_factor_custom_total_cost_recipe(factor)



#*********************************

@register.simple_tag
def list_factor_qty_unit_bulk_and_kg_ltr_pcs_list_recipeposition(recipeposition,factor):
	return recipeposition.list_factor_qty_unit_bulk_and_kg_ltr_pcs_list_recipeposition(factor)

@register.simple_tag
def dict_factor_density_cost_default_ing_recipeposition(recipeposition,factor):
	return recipeposition.dict_factor_density_cost_default_ing_recipeposition(factor)

@register.simple_tag
def dict_total_and_fact_cost_recipe(recipe,factor):
	return recipe.dict_total_and_fact_cost_recipe(factor)

@register.simple_tag
def list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe(recipeposition,factor):
	return recipeposition.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe(factor)


#**************************************8
@register.simple_tag
def dict_factor_density_cost_custom_ing_recipeposition(recipeposition,menu,factor):
	return recipeposition.dict_factor_density_cost_custom_ing_recipeposition(menu,factor)

@register.simple_tag
def list_custom_cost_per_bulk_units_and_kg_ltr_pcs_recipe(recipe,menu):
	return recipe.list_custom_cost_per_bulk_units_and_kg_ltr_pcs_recipe(menu)


@register.simple_tag
def dict_total_and_fact_cost_custom_ing_recipe(recipe,menu,factor):
	return recipe.dict_total_and_fact_cost_custom_ing_recipe(menu,factor)

@register.simple_tag
def ingredient_recipepositions(ingredient,menuposition):
	return ingredient.ingredient_recipepositions(menuposition)

@register.simple_tag
def ingredient_qty_rate_cost_default_ingredient(ingredient,menu):
	return ingredient.ingredient_qty_rate_cost_default_ingredient(menu)

@register.simple_tag
def ingredient_qty_rate_cost_custom_ingredient(ingredient,menu):
	return ingredient.ingredient_qty_rate_cost_custom_ingredient(menu)

@register.simple_tag
def ingredient_recipepositions_recipe(ingredient,recipe):
	return ingredient.ingredient_recipepositions_recipe(recipe)

@register.simple_tag
def ingredient_qty_rate_cost_default_ingredient_all_recipes(ingredient):
	return ingredient.ingredient_qty_rate_cost_default_ingredient_all_recipes()
