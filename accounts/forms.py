from django.forms import ModelForm
from .views import *
from store.models import Order

# class HelpDeskModelAdmin(admin.ModelAdmin):
#     readonly_fields=('help_num',)
#     form = HelpDeskModelForm

class OrderForm(ModelForm):
	class Meta:
		model = Order
		fields = '__all__'

class CustomerForm(ModelForm):
	class Meta:
		model = Customer
		fields = '__all__'