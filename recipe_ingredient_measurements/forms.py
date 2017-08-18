from django import forms

from .models import RecipeIngredientMeasurements

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

class RecipeIngredientMeasurementsForm(forms.ModelForm):
	# helper = FormHelper()
	# helper.label_class = 'col-xs-1'
	# helper.field_class = 'col-xs-2'
	class Meta:
		model = RecipeIngredientMeasurements
		fields = [
			"name",
			"slug",
			"formtype",
			"volume_Liters",
			"mass_KiloGrams",
			"pieces_Numbers",
		]



	def clean_mass_KiloGrams(self):
		cleaned_data = super(RecipeIngredientMeasurementsForm, self).clean()
		mass_KiloGrams = cleaned_data.get("mass_KiloGrams")
		formtype = cleaned_data.get("formtype")
		#print(mass_KiloGrams)
		#print(formtype)
		if formtype == "kg" and not mass_KiloGrams:
			raise forms.ValidationError("Mass value compulsory")
		return mass_KiloGrams


	def clean_volume_Liters(self):
		cleaned_data = super(RecipeIngredientMeasurementsForm, self).clean()
		volume_Liters = cleaned_data.get("volume_Liters")
		formtype = cleaned_data.get("formtype")
		#print(volume_Liters)
		#print(formtype)
		if formtype == "ltr" and not volume_Liters:
			raise forms.ValidationError("Volume value compulsory")
		return volume_Liters


	def clean_pieces_Numbers(self):
		cleaned_data = super(RecipeIngredientMeasurementsForm, self).clean()
		pieces_Numbers = cleaned_data.get("pieces_Numbers")
		formtype = cleaned_data.get("formtype")
		#print(pieces_Numbers)
		#print(formtype)
		if formtype == "pcs" and not pieces_Numbers:
			raise forms.ValidationError("Pieces value compulsory")
		return pieces_Numbers
