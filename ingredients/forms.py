from django import forms

from .models import Ingredient

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button, Div, Column, HTML
from crispy_forms.bootstrap import StrictButton, FormActions
from crispy_forms.helper import FormHelper

class ExampleFormSetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(ExampleFormSetHelper, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.layout = Layout(
			Div(
				Div(HTML("{{ forloop.counter }}"),
					Div('DELETE', css_class='clearfix'),
					css_class='col-xs-2', style='width:100px;text-align:center'),
				Div('name', css_class='col-xs-2', style='width:250px'),
				Div('munit', css_class='col-xs-2', style='width:150px'),
				Div('rate', css_class='col-xs-2', style='width:150px'),
				Div('typeofingredient', css_class='col-xs-2', style='width:120px'),
				Div('density_kg_per_lt', css_class='col-xs-2', style='width:120px'),
				Div('density_pcs_per_kg', css_class='col-xs-1', style='width:120px'),
				Div('density_pcs_per_lt', css_class='col-xs-1', style='width:120px'),
				css_class='row',style="border-top:1px solid;padding-top:20px")
			)
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True


#*************** used in recipes/views/ingredient_recipe_update
class RecipeIngredientFormSetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		formset = kwargs.pop('formset', None)
		super(RecipeIngredientFormSetHelper, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.form_tag = False
		self.layout = Layout(
			Div(
				Div(HTML("{{ forloop.counter }}"),
					css_class='col-xs-2', style='width:100px;text-align:center'),
				Div('name', css_class='col-xs-2', style='width:250px'),
				Div('munit', css_class='col-xs-2', style='width:150px'),
				Div('rate', css_class='col-xs-2', style='width:150px'),
				Div('typeofingredient', css_class='col-xs-2', style='width:120px'),
				Div('density_kg_per_lt', css_class='col-xs-2', style='width:120px'),
				Div('density_pcs_per_kg', css_class='col-xs-1', style='width:120px'),
				Div('density_pcs_per_lt', css_class='col-xs-1', style='width:120px'),
				css_class='row',style="border-top:1px solid;padding-top:20px")
			)
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True

#*************** used in recipes/views/ingredient_recipe_update
class RecipeIngredientFormSetHelper2 (FormHelper):
	def __init__(self, *args, **kwargs):
		formset = kwargs.pop('formset', None)
		super(RecipeIngredientFormSetHelper2, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.layout = Layout(
			Div(
				Div(HTML("{{ forloop.counter }}"),
					css_class='col-xs-2', style='width:100px;text-align:center'),
				css_class='row',style="border-top:1px solid;padding-top:20px")
			)
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True



class IngredientCreateFormSetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(IngredientCreateFormSetHelper, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.layout = Layout(
			Div(
				Div(HTML("{{ forloop.counter }}"),css_class='col-xs-2', style='width:100px;padding: 30px;text-align:center'),
				Div('name', css_class='col-xs-2', style='width:300px'),
				Div('munit', css_class='col-xs-2', style='width:150px'),
				Div('rate', css_class='col-xs-2', style='width:150px'),
				Div('typeofingredient', css_class='col-xs-2', style='width:120px'),
				Div('density_kg_per_lt', css_class='col-xs-2', style='width:120px'),
				Div('density_pcs_per_kg', css_class='col-xs-1', style='width:120px'),
				Div('density_pcs_per_lt', css_class='col-xs-1', style='width:120px'),
				css_class='row',style="border-top:1px solid;padding-top:20px")
			)
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True


class IngredientCreateFormSetHelper2(FormHelper):
	def __init__(self, *args, **kwargs):
		super(IngredientCreateFormSetHelper2, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.layout = Layout(
			Div(
				Div(HTML("{{ forloop.counter }}"),css_class='col-xs-2', style='width:60px;padding: 5px;text-align:center'),
				Div('name', css_class='col-xs-2', style='width:300px'),
				Div('munit', css_class='col-xs-2', style='width:150px'),
				Div('rate', css_class='col-xs-2', style='width:150px'),
				Div('typeofingredient', css_class='col-xs-2', style='width:120px'),
				Div('density_kg_per_lt', css_class='col-xs-2', style='width:120px'),
				Div('density_pcs_per_kg', css_class='col-xs-1', style='width:120px'),
				Div('density_pcs_per_lt', css_class='col-xs-1', style='width:120px'),
				css_class='row',style="border-top:1px solid;padding-top:20px")
			)
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True


class IngredientForm2(forms.ModelForm):
	# helper = FormHelper()
	# helper.label_class = 'col-xs-1'
	# helper.field_class = 'col-xs-2'
	class Meta:
		model = Ingredient
		fields = [
			"name",
			"munit",
			"rate",
			"typeofingredient",
			"density_kg_per_lt",
			"density_pcs_per_kg",
			"density_pcs_per_lt",
			]
		labels = {
			"name" : "",
			"munit" : "",
			"rate" : "",
			"typeofingredient" : "",
			"density_kg_per_lt" : "",
			"density_pcs_per_kg" : "",
			"density_pcs_per_lt" : "",
			}

	def __init__(self, *args, **kwargs):
		super(IngredientForm2, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		#self.fields['name'].widget.attrs['disabled'] = True (diabled fields will not be submitted)
		self.fields['name'].widget.attrs['readonly'] = True

class IngredientForm21(forms.ModelForm):
	# helper = FormHelper()
	# helper.label_class = 'col-xs-1'
	# helper.field_class = 'col-xs-2'
	class Meta:
		model = Ingredient
		fields = [
			"name",
			"munit",
			"rate",
			"typeofingredient",
			"density_kg_per_lt",
			"density_pcs_per_kg",
			"density_pcs_per_lt",
			]
		labels = {
			"name" : "",
			"munit" : "",
			"rate" : "",
			"typeofingredient" : "",
			"density_kg_per_lt" : "",
			"density_pcs_per_kg" : "",
			"density_pcs_per_lt" : "",
			}

	def __init__(self, *args, **kwargs):
		super(IngredientForm21, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		#self.fields['name'].widget.attrs['disabled'] = True (diabled fields will not be submitted)
		#self.fields['name'].widget.attrs['readonly'] = True


class IngredientForm31(forms.ModelForm):
	class Meta:
		model = Ingredient
		fields = [
			"rate",
			"density_kg_per_lt",
			"density_pcs_per_kg",
			"density_pcs_per_lt",
			]
		labels = {
			"rate" : "",
			"density_kg_per_lt" : "",
			"density_pcs_per_kg" : "",
			"density_pcs_per_lt" : "",
			}


class IngredientForm3(forms.ModelForm):
	# helper = FormHelper()
	# helper.label_class = 'col-xs-1'
	# helper.field_class = 'col-xs-2'
	class Meta:
		model = Ingredient
		fields = [
			"name",
			"munit",
			"rate",
			"typeofingredient",
			"density_kg_per_lt",
			"density_pcs_per_kg",
			"density_pcs_per_lt",
			]
		labels = {
			"name" : "name",
			"munit" : "munit",
			"rate" : "rate",
			"typeofingredient" : "Type",
			"density_kg_per_lt" : "Kg/lt",
			"density_pcs_per_kg" : "Pcs/kg",
			"density_pcs_per_lt" : "Pcs/lt",
			}

	def __init__(self, *args, **kwargs):
		super(IngredientForm3, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
			Div(
				Div(HTML("{{ forloop.counter }}"),
					css_class='col-xs-2', style='width:100px;text-align:center'),
				Div('name', css_class='col-xs-2', style='width:250px'),
				Div('munit', css_class='col-xs-2', style='width:150px'),
				Div('rate', css_class='col-xs-2', style='width:150px'),
				Div('typeofingredient', css_class='col-xs-2', style='width:120px'),
				Div('density_kg_per_lt', css_class='col-xs-2', style='width:120px'),
				Div('density_pcs_per_kg', css_class='col-xs-1', style='width:120px'),
				Div('density_pcs_per_lt', css_class='col-xs-1', style='width:120px'),
				css_class='row',style="border-top:1px solid;padding-top:20px")
			)




class IngredientForm(forms.ModelForm):
	# helper = FormHelper()
	# helper.label_class = 'col-xs-1'
	# helper.field_class = 'col-xs-2'
	class Meta:
		model = Ingredient
		fields = [
			"name",
			"munit",
			"rate",
			"typeofingredient",
			"density_kg_per_lt",
			"density_pcs_per_kg",
			"density_pcs_per_lt",
		]


	def __init__(self, *args, **kwargs):
		super(IngredientForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
				HTML('<h3> Add/Edit Ingredients </h3>'),
				Div(
					Div('name', css_class='col-xs-3'),
					Div('munit', css_class='col-xs-3'),
					Div('rate', css_class='col-xs-3'),
					Div('typeofingredient', css_class='col-xs-3'),
					css_class='row'),
				Div(
					Div('density_kg_per_lt', css_class='col-xs-3'),
					Div('density_pcs_per_kg', css_class='col-xs-3'),
					Div('density_pcs_per_lt', css_class='col-xs-3'),
					css_class='row'),
				HTML('<input type="hidden" name="next" value="{{ request.GET.next }}">'),
				FormActions(
					Submit('save', 'Submit'),
					)

			)