from django.shortcuts import render

# Create your views here.
def view_orders(request):
    return render(request, 'orders.html')

def view_errors(request):
    return render(request, 'errors.html')

def create_order(request):
    return render(request, 'create_order.html')