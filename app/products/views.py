from django.http import HttpResponse
from django.shortcuts import render
from .models import Product

# Create your views here.
def view_products(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'stockDisplay.html', context)

def productDetails(request, sku):
    product = Product.objects.get(sku=sku)
    context = {
        'product': product,
    }
    return render(request, 'productDetails.html', context)

def create_product(request):
    return render(request, 'create_product.html')