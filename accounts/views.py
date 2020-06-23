from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .forms import *
from .filters import *
from store.models import Product , Order

def home(request):

	orders = Order.objects.all()

	total_orders = orders.count()
	Pending = orders.filter(status='Pending').count()
	delivered = orders.filter(status='Delivered').count()
	
	context = {'orders':orders,'total_orders':total_orders,
	'Pending':Pending,'delivered':delivered}
	return render(request, 'accounts/dashboard.html',context)

def customers(request, pk_test):
	customer = Customer.objects.get(id=pk_test)
	orders = customer.order_set.all()
	orders_count= orders.count()
	myFilter = OrderFilter(request.GET, queryset=orders)
	orders = myFilter.qs
	
	context = {'customer':customer,'orders':orders,
	'orders_count':orders_count,'myFilter':myFilter}
	return render(request,'accounts/customers.html',context)

def products(request):

	products = Product.objects.all()
 
	return render(request,'accounts/products.html', {'products':products})

def CreateOrder(request):

	form = OrderForm()
	if request.method == "POST":
		form = OrderForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/seller')


	context = {'form': form}

	return render(request, 'accounts/orders_form.html',context)

def UpdateOrder(request, pk):



	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)

	if request.method == "POST":
		form = OrderForm(request.POST, instance = order)
		if form.is_valid():
			form.save()
			return redirect('/')


	context = {'form':form}

	return render(request, 'accounts/orders_form.html',context)

def DeleteOrder(request, pk):

	order = Order.objects.get(id = pk)
	if request.method == "POST":
		order.delete()
		return redirect('/')

	context={'order':order}

	return render(request, 'accounts/delete.html', context)

def CreateUser(request):

	form = CustomerForm()
	if request.method == "POST":
		form = CustomerForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}

	return render(request, 'accounts/create_user.html',context)

def CreateSorder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields =('Product','status'), extra=7)
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
	if request.method == "POST":
		formset = OrderFormSet(request.POST,instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/customers/'+pk)


	context = {'formset': formset,'customer':customer}

	return render(request, 'accounts/Sorder_form.html',context)