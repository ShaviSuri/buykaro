from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse
from .utils import cookieCart, cartData, guestOrder

def emptycart(view_func):
	def wrapper_func(request,*args,**kwargs):
		data = cartData(request)
		cartItems = data['cartItems']
		if cartItems == 0:
			return redirect("store")
		else:
			return view_func(request,*args,**kwargs)
	return wrapper_func