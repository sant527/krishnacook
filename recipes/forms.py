from django import forms
from django.core.exceptions import ValidationError
from .models import Recipe, RecipePosition
from single_measurements.models import SingleMeasurements
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button, Div, Column, HTML
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper

class RecipePositionCreateFormSetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(RecipePositionCreateFormSetHelper, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.form_action = ''
		self.layout = Layout(
				Div(
					Div(HTML("<span id=\"{{ forloop.counter }}_formset\">{{ forloop.counter }}</span>"),css_class='col-xs-1', style='width:60px;padding-top: 30px;text-align:center'),
					Div(Div('DELETE', css_class='clearfix'),
						Div('sequence_number', css_class='clearfix'),
						css_class='col-xs-1', style='width:100px;'),
					Div(Div('ingredient', css_class='clearfix'),
						Div('name', css_class='clearfix'),
						css_class='col-xs-1', style='width:240px;'),
					Div(Div('title', css_class='clearfix'),
						Div('cooking_notes', css_class='clearfix'),
						css_class='col-xs-1', style='width:240px;'),
					Div(HTML('<h4 style="text-align:center;background-color: antiquewhite"> Enter one or mutliple or No units </h4>'),
						Div(Div('volume_unit', css_class='clearfix'),
							Div('volume_quantity', css_class='clearfix'),
							css_class='col-xs-1',style='width:150px;'),
						Div(Div('pieces_unit', css_class='clearfix'),
							Div('pieces_quantity', css_class='clearfix'),
							css_class='col-xs-1',style='width:150px;'),
						Div(Div('mass_unit', css_class='clearfix'),
							Div('mass_quantity', css_class='clearfix'),
							css_class='col-xs-1',style='width:150px;'),
						
						css_class='col-xs-8', style='width:500px;'),

			css_class='clearfix', style="border-top:1px solid;padding-top:20px"))
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True




class RecipeForm2CreateFormSetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(RecipeForm2CreateFormSetHelper, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.layout = Layout(
						Div(
							Div(HTML("{{ forloop.counter }}"),
								Div('DELETE', css_class='clearfix'),
								css_class='col-xs-2', style='width:100px;text-align:center'),
							Div(Div('name', css_class='display:table', style='width:400px;'),
								Div('tags', css_class='display:table', style='width:400px;'),
								css_class='col-xs-4', style='width:400px;'),
							Div(HTML('<h4 style="text-align:center;background-color: antiquewhite; margin:15px">Atlease one Unit should be entered</h4>'),
								Div(Div('volume_unit', css_class='display:table', style='width:200px;'),
									Div('volume_quantity', css_class='display:table', style='width:200px;'),
									css_class='col-xs-4'),
								Div(Div('pieces_unit', css_class='display:table', style='width:200px;'),
									Div('pieces_quantity', css_class='display:table', style='width:200px;'),
									css_class='col-xs-4'),
								Div(Div('mass_unit', css_class='display:table', style='width:200px;'),
									Div('mass_quantity', css_class='display:table', style='width:200px;'),
									css_class='col-xs-4', style='width:100px;'),
								
								css_class='col-xs-8', style='width:700px;'),

							css_class='clearfix',style="border-top:1px solid;padding-top:20px")
					)
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True


class RecipeForm23CreateFormSetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(RecipeForm23CreateFormSetHelper, self).__init__(*args, **kwargs)
		self.form_method = 'post'
		self.layout = Layout(
						Div(
							Div(HTML("{{ forloop.counter }}"),	
								css_class='col-xs-1', style='width:100px;padding-top:30px;text-align:center'),
							Div(Div('name', css_class='display:table', style='width:400px;'),
								Div('tags', css_class='display:table', style='width:400px;'),
								css_class='col-xs-4', style='width:400px;'),
							Div(HTML('<h4 style="text-align:center;background-color: antiquewhite; margin:15px">Atlease one Unit should be entered</h4>'),
								Div(Div('volume_unit', css_class='display:table', style='width:200px;'),
									Div('volume_quantity', css_class='display:table', style='width:200px;'),
									css_class='col-xs-4'),
								Div(Div('pieces_unit', css_class='display:table', style='width:200px;'),
									Div('pieces_quantity', css_class='display:table', style='width:200px;'),
									css_class='col-xs-4'),
								Div(Div('mass_unit', css_class='display:table', style='width:200px;'),
									Div('mass_quantity', css_class='display:table', style='width:200px;'),
									css_class='col-xs-4', style='width:100px;'),
								
								css_class='col-xs-8', style='width:700px;'),

							css_class='clearfix',style="border-top:1px solid;padding-top:20px")
					)
		self.add_input(Submit("submit", "Save"))
		self.render_required_fields = True



class RecipeForm2FormSet(forms.BaseModelFormSet):

	def clean_volume_unit(self):
		super(RecipeForm2FormSet, self).clean()

		for form in self.forms:
			volume_unit = form.cleaned_data['volume_unit']
			print('%s-%s' %(volume_unit,'volume_quantity'))
			volume_quantity = form.cleaned_data['volume_quantity']
			pieces_unit = form.cleaned_data['pieces_unit']
			pieces_quantity = form.cleaned_data['pieces_quantity']
			mass_unit = form.cleaned_data['mass_unit']
			mass_quantity = form.cleaned_data['mass_quantity']
			if volume_quantity and not volume_unit:
				#print('if volume_quantity and not volume_unit:')
				raise forms.ValidationError("Select the units")
			return volume_unit



class RecipeForm2(forms.ModelForm):
	volume_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="ltr"),required=False)
	pieces_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="pcs"),required=False)
	mass_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="kg"),required=False)
	class Meta:
		model = Recipe
		fields = [
			"name",
			"tags",
			"volume_quantity",
			"volume_unit",
			"pieces_quantity",
			"pieces_unit",
			"mass_quantity",
			"mass_unit",
		]

	def __init__(self, *args, **kwargs):
		super(RecipeForm2, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
				Div(
					Div(Div('name', css_class='display:table'),
						Div('tags', css_class='display:table'),
						css_class='col-xs-4'),
					Div(HTML('<h4 style="text-align:center;background-color: antiquewhite">Atlease one Unit should be entered</h4>'),
						Div(Div('volume_unit', css_class='display:table'),
							Div('volume_quantity', css_class='display:table'),
							css_class='col-xs-4'),
						Div(Div('pieces_unit', css_class='display:table'),
							Div('pieces_quantity', css_class='display:table'),
							css_class='col-xs-4'),
						Div(Div('mass_unit', css_class='display:table'),
							Div('mass_quantity', css_class='display:table'),
							css_class='col-xs-4'),
						
						css_class='col-xs-8'),

					css_class='clearfix'),
				FormActions(
					Submit('save', 'Submit'),
					)
			)

	def clean_volume_quantity(self):
		cleaned_data = super(RecipeForm2, self).clean()
		volume_quantity = cleaned_data.get("volume_quantity")
		if volume_quantity is not None and volume_quantity <=0:
			raise forms.ValidationError('%s' %("Quantity should be greater than zero"))
		return volume_quantity

	def clean_pieces_quantity(self):
		cleaned_data = super(RecipeForm2, self).clean()
		pieces_quantity = cleaned_data.get("pieces_quantity")
		if pieces_quantity is not None and pieces_quantity <= 0:
			raise forms.ValidationError('%s' % ("Quantity should be greater than zero"))
		return pieces_quantity

	def clean_mass_quantity(self):
		cleaned_data = super(RecipeForm2, self).clean()
		mass_quantity = cleaned_data.get("mass_quantity")
		if mass_quantity is not None and mass_quantity <= 0:
			raise forms.ValidationError('%s' % ("Quantity should be greater than zero"))
		return mass_quantity

	def clean_volume_unit(self):
		cleaned_data = super(RecipeForm2, self).clean()
		volume_unit = cleaned_data.get("volume_unit")
		volume_quantity = cleaned_data.get("volume_quantity")
		if volume_quantity is not None and volume_unit is None:
			raise forms.ValidationError('%s' %("Select the Volume units"))
		return volume_unit

	def clean_pieces_unit(self):
		cleaned_data = super(RecipeForm2, self).clean()
		pieces_unit = cleaned_data.get("pieces_unit")
		pieces_quantity = cleaned_data.get("pieces_quantity")
		if pieces_quantity is not None and pieces_unit is None:
			raise forms.ValidationError('%s' % ("Select the Pieces units"))
		return pieces_unit


	def clean_mass_unit(self):
		cleaned_data = super(RecipeForm2, self).clean()
		mass_unit = cleaned_data.get("mass_unit")
		mass_quantity = cleaned_data.get("mass_quantity")
		if mass_quantity is not None and mass_unit is None:
			raise forms.ValidationError('%s' % ("Select the Mass units"))
		return mass_unit

	def clean(self):
		cleaned_data = super(RecipeForm2, self).clean()
		volume_unit = cleaned_data.get("volume_unit")
		volume_quantity = cleaned_data.get("volume_quantity")
		pieces_unit = cleaned_data.get("pieces_unit")
		pieces_quantity = cleaned_data.get("pieces_quantity")
		mass_unit = cleaned_data.get("mass_unit")
		mass_quantity = cleaned_data.get("mass_quantity")
		if volume_unit is None and mass_unit is None and pieces_unit is None and volume_quantity is None and mass_quantity is None and pieces_quantity is None:
			raise forms.ValidationError("Atleast one of the units and the quantites > 0 have to be entered")
	


class RecipeForm(forms.ModelForm):
	volume_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="ltr"),required=False)
	pieces_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="pcs"),required=False)
	mass_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="kg"),required=False)
	class Meta:
		model = Recipe
		fields = [
			"name",
			"tags",
			"volume_quantity",
			"volume_unit",
			"pieces_quantity",
			"pieces_unit",
			"mass_quantity",
			"mass_unit",
		]

	def __init__(self, *args, **kwargs):
		super(RecipeForm, self).__init__(*args, **kwargs)
		#self.fields['pieces_unit'].label = '' #if we want not to show the label
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		#self.helper.form_show_labels = False
		self.helper.layout = Layout(
				HTML('<h3> Add/Edit New Recipes</h3>'),
				Div(
					Div(Div('name', css_class='clearfix'),
						Div('tags', css_class='clearfix'),
						css_class='col-xs-4'),
					Div(HTML('<h4 style="text-align:center;background-color: antiquewhite">Atlease one Unit should be entered</h4>'),
						Div(Div('volume_unit', css_class='clearfix'),
							Div('volume_quantity', css_class='clearfix'),
							css_class='col-xs-4'),
						Div(Div('pieces_unit', css_class='clearfix'),
							Div('pieces_quantity', css_class='clearfix'),
							css_class='col-xs-4'),
						Div(Div('mass_unit', css_class='clearfix'),
							Div('mass_quantity', css_class='clearfix'),
							css_class='col-xs-4'),
						HTML('<input type="hidden" name="next" value="{{ request.GET.next }}">'),
						css_class='col-xs-8'),

					css_class='clearfix'),
				FormActions(
					Submit('save', 'Submit'),
					)
			)


	def clean_volume_quantity(self):
		cleaned_data = super(RecipeForm, self).clean()
		volume_quantity = cleaned_data.get("volume_quantity")
		if volume_quantity is not None and volume_quantity <=0:
			raise forms.ValidationError('%s' %("Quantity should be greater than zero"))
		return volume_quantity

	def clean_pieces_quantity(self):
		cleaned_data = super(RecipeForm, self).clean()
		pieces_quantity = cleaned_data.get("pieces_quantity")
		if pieces_quantity is not None and pieces_quantity <= 0:
			raise forms.ValidationError('%s' % ("Quantity should be greater than zero"))
		return pieces_quantity

	def clean_mass_quantity(self):
		cleaned_data = super(RecipeForm, self).clean()
		mass_quantity = cleaned_data.get("mass_quantity")
		if mass_quantity is not None and mass_quantity <= 0:
			raise forms.ValidationError('%s' % ("Quantity should be greater than zero"))
		return mass_quantity

	def clean_volume_unit(self):
		cleaned_data = super(RecipeForm, self).clean()
		volume_unit = cleaned_data.get("volume_unit")
		volume_quantity = cleaned_data.get("volume_quantity")
		if volume_quantity is not None and volume_unit is None:
			raise forms.ValidationError('%s' %("Select the Volume units"))
		return volume_unit

	def clean_pieces_unit(self):
		cleaned_data = super(RecipeForm, self).clean()
		pieces_unit = cleaned_data.get("pieces_unit")
		pieces_quantity = cleaned_data.get("pieces_quantity")
		if pieces_quantity is not None and pieces_unit is None:
			raise forms.ValidationError('%s' % ("Select the Pieces units"))
		return pieces_unit


	def clean_mass_unit(self):
		cleaned_data = super(RecipeForm, self).clean()
		mass_unit = cleaned_data.get("mass_unit")
		mass_quantity = cleaned_data.get("mass_quantity")
		if mass_quantity is not None and mass_unit is None:
			raise forms.ValidationError('%s' % ("Select the Mass units"))
		return mass_unit

	def clean(self):
		cleaned_data = super(RecipeForm, self).clean()
		volume_unit = cleaned_data.get("volume_unit")
		volume_quantity = cleaned_data.get("volume_quantity")
		pieces_unit = cleaned_data.get("pieces_unit")
		pieces_quantity = cleaned_data.get("pieces_quantity")
		mass_unit = cleaned_data.get("mass_unit")
		mass_quantity = cleaned_data.get("mass_quantity")
		if volume_unit is None and mass_unit is None and pieces_unit is None and volume_quantity is None and mass_quantity is None and pieces_quantity is None:
			raise forms.ValidationError("Atleast one of the units and the quantites > 0 have to be entered")
	



class RecipePoistionForm(forms.ModelForm):
	volume_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="ltr").select_related(),required=False)
	mass_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="kg"),required=False)
	pieces_unit = forms.ModelChoiceField(queryset=SingleMeasurements.objects.filter(formtype="pcs"),required=False)
	class Meta:
		model = RecipePosition
		fields = [
			"sequence_number",
			"ingredient",
			"name",
			"title",
			"mass_unit",
			"mass_quantity",
			"volume_unit",
			"volume_quantity",
			"pieces_unit",
			"pieces_quantity",
			"cooking_notes",
		]


	def __init__(self, *args, **kwargs):
		super(RecipePoistionForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
				HTML('<h3> Add/Edit New Ingredients</h3>'),
				Div(
					Div(Div('ingredient', css_class='clearfix'),
						Div('name', css_class='clearfix'),
						css_class='col-xs-4',style="padding-top:40px"),
					Div(HTML('<h4 style="text-align:center;background-color: antiquewhite"> Enter one or mutliple or No units </h4>'),
						Div(Div('volume_unit', css_class='clearfix'),
							Div('volume_quantity', css_class='clearfix'),
							css_class='col-xs-4'),
						Div(Div('pieces_unit', css_class='clearfix'),
							Div('pieces_quantity', css_class='clearfix'),
							css_class='col-xs-4'),
						Div(Div('mass_unit', css_class='clearfix'),
							Div('mass_quantity', css_class='clearfix'),
							css_class='col-xs-4'),
						
						css_class='col-xs-8'),

					css_class='clearfix'),
				Div(Div('sequence_number',css_class='col-xs-2'),
					Div('title',css_class='col-xs-4'),
					Div('cooking_notes',css_class='col-xs-4'),
					css_class='clearfix'),
				HTML('<input type="hidden" name="next" value="{{ request.GET.next }}">'),
				FormActions(
					Submit('save', 'Submit'),
					)
			)



	# def clean(self):
	# 	cleaned_data = super(RecipePoistionForm, self).clean()
	# 	volume_unit = cleaned_data.get("volume_unit")
	# 	volume_quantity = cleaned_data.get("volume_quantity")
	# 	pieces_unit = cleaned_data.get("pieces_unit")
	# 	pieces_quantity = cleaned_data.get("pieces_quantity")
	# 	mass_unit = cleaned_data.get("mass_unit")
	# 	mass_quantity = cleaned_data.get("mass_quantity")
	# 	#print("i am here")
	# 	#print(cleaned_data)
	# 	#print("cleaned_data")
	# 	if not volume_unit and not mass_unit and not pieces_unit:
	# 		#print("i am also here")
	# 		raise forms.ValidationError("Atleast one of the units have to be entered")

	# def clean_name(self):
	# 	cleaned_data = super(RecipePoistionForm, self).clean()
	# 	name = cleaned_data.get("name")
	# 	ingredient = cleaned_data.get("ingredient")
	


	#if (not volume_unit and volume_quantity <= 0) or (not mass_unit and mass_quantity  <= 0) or (not pieces_unit and pieces_quantity <= 0) or (volume_unit and volume_quantity <= 0) or (mass_unit and mass_quantity  <= 0) or (pieces_unit and pieces_quantity <= 0):

	# def clean_munit(self):
	# 	cleaned_data = super(RecipePoistionForm, self).clean()
	# 	ingredient = cleaned_data.get("ingredient")
	# 	munit = cleaned_data.get("munit")
	# 	if ((ingredient.munit == 'pcs') and (munit.slug != 'pcs')):
	# 		raise forms.ValidationError("Unit shoudl be pieces when MUnit is pieces")

	# 	if ((ingredient.munit == 'ltr') and (munit.slug == 'kg')) or ((ingredient.munit == 'ltr') and (munit.slug == 'pcs')):
	# 		#print("ingredient.munit == 'ltr'")
	# 		raise forms.ValidationError("Unit cannot be Kg or Pieces when MUnit is Liters")

	# 	if ((ingredient.munit == 'kg') and (munit.slug == 'pcs')):
	# 		raise forms.ValidationError("Unit cannot be Pieces when MUnit is Kg")

	# 	return munit
