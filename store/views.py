from django.urls import reverse
from django.shortcuts import render,redirect, get_list_or_404, get_object_or_404
from django.http import JsonResponse , HttpResponse , HttpResponseRedirect
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder, token_generator
from .forms import CreateUserForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate , login, logout
from .decorators import emptycart
from django.contrib.auth.models import User

# for user activation
from django.views import View
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
import threading


class EmailThread(threading.Thread):
	def __init__(self, email):
		self.email = email
		threading.Thread.__init__(self)

	def run(self):
		self.email.send()



def registerPage(request):

	data = cartData(request)
	cartItems = data['cartItems']

	form = CreateUserForm()
		
	if request.user.is_authenticated:
		return redirect("store")
	else:
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				email_id = form.cleaned_data.get("email")
				user=form.save()
				user.is_active = False
				user.save()

				uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
				domain = get_current_site(request).domain
				link = reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
				activate_url = 'https://'+domain+link

				email_subject = 'Activate Your Account'
				email_body = 'Hi '+user.username+', Please use the following link to verify your account for BuyKaro\n'+activate_url

				email = EmailMessage(
			    email_subject,
			    email_body,
			    'noreply@buykaro.com',
			    [email_id],
				)

				# email.send(fail_silently=False) 

				EmailThread(email).start()
				
				user1  = form.cleaned_data.get('username')
				messages.success(request,"Account created successfully for "+user1+".\
				 A verification mail has been sent\n"+"to your entered email address. Please verify your email address to login. ")
				return redirect("login")

		context = {'form':form,'cartItems':cartItems}
		return render(request,'store/register.html',context)

class VerificationView(View):
	def get(self,request,uidb64,token):
		id = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=id)

		if user.is_active:
			messages.info(request,'Account already Activated')
			return redirect("login")
		else:
			user.is_active = True
			user.save()
			messages.success(request,'Account has been successfully Activated')
			return redirect("login")
		
		# except Exception as ex:
		# 	pass

		# return redirect("login")

def loginPage(request):
	data = cartData(request)

	cartItems = data['cartItems']

	if request.user.is_authenticated:
		return redirect("store")
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request,username=username,password=password)
			
			if user is not None:
				login(request,user)
				return redirect("store")
			else:
				messages.info(request,"username OR passoword is incorrect")
		context = {'cartItems':cartItems}
		return render(request,'store/login.html',context)

def logoutPage(request):
	logout(request)
	return redirect("login")

def search(request):
	data = cartData(request)

	cartItems = data['cartItems']

	query=request.GET['query']
	products= Product.objects.filter(name__icontains=query)
	context={'products':products,'query':query,'cartItems':cartItems}
	
	return render(request,'store/search.html',context)

def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

def product(request,pk):
	data = cartData(request)
	domain = get_current_site(request).domain
	url = 'https://'+domain
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	products = Product.objects.filter(id=pk)
	context = {'products':products,'cartItems':cartItems,'domain':domain}
	return render(request,'store/product.html', context)

def removeitem(request, pk):
    product1 = Product.objects.get(id=pk)
    name = product1.name
    product = OrderItem.objects.filter(product__name__icontains=name)
    product.delete()
    data = cartData(request)
    cartItems = data['cartItems']
    if cartItems >0:
    	return redirect('cart')
    context= {'cartItems':cartItems,'product':product}
    return render(request, 'store/cart.html', context)

def cart(request):

	# if "delete_cart" in request.GET:
	# 	name = request.GET["delete_cart"]
		
	# 	cart_obj = get_object_or_404(OrderItem,product=name)
	# 	cart_obj.delete()
	# 	return HttpResponse(1)

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']


	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

@emptycart
def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)
	