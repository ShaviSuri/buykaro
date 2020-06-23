from django.db import models
from django.db.models import CharField
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name= models.CharField(max_length=200, null=True)
	phone= models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)
	date_created= models.DateTimeField(auto_now_add=True, null=True)

	# def __str__(self):
	# 	return self.name
	
def create_profile(sender, **kwargs):
	if kwargs['created']:
		user_profile=Customer.objects.create(user=kwargs['instance'])
post_save.connect(create_profile, sender=User)

class Tag(models.Model):
	name= models.CharField(max_length=200, null=True,blank=True)

	def __str__(self):
		return self.name

class Product(models.Model):
	CATEGORY = (
			('Input','Input'),
	    	('Output','Output')
	    )
	
	name = models.CharField(max_length=200)
	price = models.FloatField()
	digital = models.BooleanField(default=False,null=True, blank=True)
	image = models.ImageField(null=True, blank=True)
	# category= models.CharField(max_length=200,null=True,choices=CATEGORY)
	description= models.CharField(max_length=200,null=True,blank=True)
	date_created= models.DateTimeField(auto_now_add=True,null=True)
	# tags = models.ManyToManyField(Tag)

	def __str__(self):
		return self.name

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url

class Order(models.Model):
	STATUS = (
	    	('Pending','Pending'),
	    	('Out for delivery','Out for delivery'),
	    	('Delivered','Delivered')
	    	)
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	Product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
	date_ordered = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=200,null= True,choices=STATUS)
	note = models.CharField(max_length=1000,null= True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	
	def __str__(self):
		name = str(self.Product)
		return name
		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

class OrderItem(models.Model):
	
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address