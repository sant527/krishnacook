from django import forms
from django.core.exceptions import ValidationError
from ingredients.models import Ingredient
from .models import Menu, MenuPosition, IngredientCustom
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button, Div, Column, HTML
from crispy_forms.bootstrap import StrictButton, FormActions
from crispy_forms.helper import FormHelper
from django.db import models
from django.utils.safestring import mark_safe

class MenuCustomIngredientFormSetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(MenuCustomIngredientFormSetHelper, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.form_action = ''
		self.layout =Layout(
				Div(
					Div(HTML("{{ forloop.counter }}{{ form }}"),
					css_class='col-xs-2', style='width:100px;text-align:center;padding-top:30px'),
					Div('ingredient', css_class='col-xs-1', style="width:300px"),
					Div('rate', css_class='col-xs-1', style="width:150px"),
					Div('density_kg_per_lt', css_class='col-xs-1', style="width:150px"),
					Div('density_pcs_per_kg', css_class='col-xs-1', style="width:150px"),
					Div('density_pcs_per_lt', css_class='col-xs-1', style="width:150px"),
					#Div('menu', css_class='col-xs-1', style="width:300px"),
				css_class='row'),
		)
		self.add_input(Submit("submit", "Save"))





class MenuPositionCreateFormSetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(MenuPositionCreateFormSetHelper, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.form_action = ''
		self.layout =Layout(
				Div(
					Div(HTML("{{ forloop.counter }}"),
						Div('DELETE', css_class='clearfix'),
					css_class='col-xs-2', style='width:100px;text-align:center'),
					Div('sequence_number', css_class='col-xs-1', style="width:120px"),
					Div('name', css_class='col-xs-1', style="width:200px"),
					Div('menurecipe', css_class='col-xs-1', style="width:200px"),
					Div('persons', css_class='col-xs-1', style="width:120px"),
					Div('consumption_milli_liters', css_class='col-xs-1', style="width:120px"),
					Div('consumption_grams', css_class='col-xs-1', style="width:120px"),
					Div('consumption_pieces', css_class='col-xs-1', style="width:120px"),
					Div('title', css_class='col-xs-1', style="width:300px"),
					Div('recipe_notes', css_class='col-xs-1', style="width:300px"),
				css_class='row'),
		)
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True



class PlainTextWidget(forms.Widget):
	def render(self, name, value, attrs):
		if value is not None:
			mark = mark_safe("<input type='hidden' name='%s' value='%s' />" % (name,value))
			return mark
		else:
			return '-'

class MenuForm(forms.ModelForm):
	class Meta:
		model = Menu
		fields = [
			"name",
		]

class IngredientCustomForm(forms.ModelForm):
	#ingredient = forms.CharField(widget=PlainTextWidget)
	class Meta:
		model = IngredientCustom
		fields = [
			'ingredient',
			'rate',
			]
		widgets = {
			'ingredient': PlainTextWidget
		}
		labels = {
			'ingredient':'',
			'rate': '',
		}

	def __init__(self, *args, **kwargs):
		
		# Accessing the model instance in a ModelForm's widget
		super(IngredientCustomForm, self).__init__(*args, **kwargs)
		if hasattr(self, 'instance'):
			self.fields['ingredient'].widget.instance = self.instance


class MenuPoistionForm(forms.ModelForm):
	class Meta:
		model = MenuPosition
		fields = [
			'sequence_number',
			'name',
			'menurecipe',
			'persons',
			'consumption_milli_liters',
			'consumption_grams',
			'consumption_pieces',
			'recipe_notes',
			'title'
		]
		labels = {
			'name':'name: if blank = Recipe',
			'consumption_milli_liters': 'ml/person',
			'consumption_grams': 'grams/person',
			'consumption_pieces': 'pcs/person',
			'sequence_number':'Sq No:'
		}
		help_texts = {
			'name':'',
			'menurecipe':'',
			'persons':'',
			'consumption_milli_liters': '',
			'consumption_grams': '',
			'consumption_pieces': '',
		}

	def __init__(self, *args, **kwargs):
		super(MenuPoistionForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
				HTML('<h3> Add/Edit Recipes to the Event </h3>'),
				Div(
					Div('sequence_number', css_class='col-xs-1', style="width:200px"),
					Div('name', css_class='col-xs-1', style="width:200px"),
					Div('menurecipe', css_class='col-xs-1', style="width:200px"),
					Div('persons', css_class='col-xs-1', style="width:120px"),
					css_class='row'),
				HTML('<h4> Consumption per Person(enter only one value) </h4>'),
				Div(
					Div('consumption_milli_liters', css_class='col-xs-4', style="width:120px"),
					Div('consumption_grams', css_class='col-xs-4', style="width:120px"),
					Div('consumption_pieces', css_class='col-xs-4', style="width:120px"),
					css_class='row'),
				Div(
				  
					Div('title', css_class='col-xs-4', style="width:200px"),
					Div('recipe_notes', css_class='col-xs-4', style="width:2	00px"),
					css_class='row'),
				FormActions(
					Submit('save', 'Submit'),
					)
		)

	def clean(self):
		cleaned_data = super(MenuPoistionForm, self).clean()
		consumption_milli_liters = cleaned_data.get("consumption_milli_liters")
		consumption_grams = cleaned_data.get("consumption_grams")
		consumption_pieces = cleaned_data.get("consumption_pieces")
		if (not consumption_milli_liters) and (not consumption_grams) and (not consumption_pieces):
			#print("not consumption_pieces and not consumption_grams and not consumption_pieces:")
			raise forms.ValidationError("Atleast one unit should be entered")
		if consumption_milli_liters and consumption_grams and not consumption_pieces:
			#print("consumption_pieces and consumption_grams and not consumption_pieces:")
			raise forms.ValidationError("Only one unit can be entered")
		if consumption_milli_liters and not consumption_grams and consumption_pieces:
			#print("consumption_pieces and not consumption_grams and consumption_pieces:")
			raise forms.ValidationError("Only one unit can be entered")
		if not consumption_milli_liters and consumption_grams and consumption_pieces:
			#print("not consumption_pieces and consumption_grams and consumption_pieces:")
			raise forms.ValidationError("Only one unit can be entered")
		if consumption_milli_liters and consumption_grams and consumption_pieces:
			#print("consumption_pieces and consumption_grams and consumption_pieces:")
			raise forms.ValidationError("Only one unit can be entered")


	def clean_consumption_milli_liters(self):
		cleaned_data = super(MenuPoistionForm, self).clean()
		consumption_milli_liters = cleaned_data.get("consumption_milli_liters")
		menurecipe = cleaned_data.get("menurecipe")
		if consumption_milli_liters:
			if menurecipe.volume_unit and menurecipe.volume_quantity > 0:
				return consumption_milli_liters
			else:
				raise forms.ValidationError('{} {}'.format('Not a valid Unit for',menurecipe.name))

	def clean_consumption_grams(self):
		cleaned_data = super(MenuPoistionForm, self).clean()
		consumption_grams = cleaned_data.get("consumption_grams")
		menurecipe = cleaned_data.get("menurecipe")
		if consumption_grams:
			if menurecipe.mass_unit and menurecipe.mass_quantity > 0:
				return consumption_grams
			else:
				raise forms.ValidationError('{} {}'.format('Not a valid Unit for',menurecipe.name))

	def clean_consumption_pieces(self):
		cleaned_data = super(MenuPoistionForm, self).clean()
		consumption_pieces = cleaned_data.get("consumption_pieces")
		menurecipe = cleaned_data.get("menurecipe")
		if consumption_pieces:
			if menurecipe.pieces_unit and menurecipe.pieces_quantity > 0:
				return consumption_pieces
			else:
				raise forms.ValidationError('{} {}'.format('Not a valid Unit for',menurecipe.name))


	



#{} {}'.format('Unit should be in',menurecipe.primary_unit.form_type3()