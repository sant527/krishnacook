from django import forms

from .models import TypeOfIngredient

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

class TypeOfIngredientForm(forms.ModelForm):
	# helper = FormHelper()
	# helper.label_class = 'col-xs-1'
	# helper.field_class = 'col-xs-2'
	class Meta:
		model = TypeOfIngredient
		fields = [
			"name",
		]