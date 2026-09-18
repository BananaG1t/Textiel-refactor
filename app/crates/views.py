from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Crate
from orders.models import Order, OrderItemAllocation
from orders.services import complete_order, get_print_list, complete_printing

# Create your views here.
def displayCrates(request):
    template = loader.get_template('cratesDisplay.html')
    products = Crate.objects.all()
    context = {
        'crates': products,
    }
    return HttpResponse(template.render(context, request))

def crateDetails(request, id):
    crate = get_object_or_404(Crate, id=id)
    if crate.has_order:
        if crate.status == Crate.CrateStatus.PICKING:
            template = loader.get_template('cratePicking.html')
            allocations = (
                OrderItemAllocation.objects.filter(order=crate.order)
                .select_related("product")
                .order_by("product__name")
            )
            context = {'crate': crate, 'allocations': allocations}

        elif crate.status == Crate.CrateStatus.PRINTING:
            template = loader.get_template('cratePrinting.html')
            print_list = get_print_list(crate.order)
            context = {'crate': crate, 'print_list': print_list}
        else:
            template = loader.get_template('crateDetails.html')
    
            items = crate.order.items.select_related("product").all()
            context = {
                'crate': crate,
                'items': items,
            }

    else:
        template = loader.get_template('crateAssignment.html')

        available_orders = Order.objects.filter(crate=None, status=Order.OrderStatus.RESERVED)
        context = {
            'crate': crate,
            'orders': available_orders,
        }

    return HttpResponse(template.render(context, request))

@require_POST
@transaction.atomic
def assign_crate(request, crate_id, order_id):
    crate = get_object_or_404(Crate.objects.select_for_update(), id=crate_id)
    order = get_object_or_404(
        Order.objects.select_for_update(),
        id=order_id,
        status=Order.OrderStatus.RESERVED,
        crate=None,
    )

    if crate.has_order:
        return HttpResponse(status=409)

    crate.status = Crate.CrateStatus.PICKING
    order.crate = crate
    order.status = Order.OrderStatus.PROCESSING
    crate.save()
    order.save()

    return HttpResponse(status=204)

@require_POST
def complete_picking(request, crate_id):
    crate = get_object_or_404(Crate, id=crate_id)

    if not crate.has_order:
            return HttpResponse(status=409)
    
    order = crate.order

    if order.status != Order.OrderStatus.PROCESSING:
        return HttpResponse(status=409)

    if get_print_list(crate.order):
        crate.status = Crate.CrateStatus.PRINTING
    else:
        crate.status = Crate.CrateStatus.PROCESSING
    crate.save()

    return HttpResponse(status=204)

@require_POST
@transaction.atomic
def complete_crate(request, crate_id):
    crate = get_object_or_404(Crate.objects.select_for_update(), id=crate_id)

    if not crate.has_order:
        return HttpResponse(status=409)

    order = crate.order

    if order.status != Order.OrderStatus.PROCESSING:
        return HttpResponse(status=409)

    try:
        complete_order(crate.order)
    except ValueError:
        return HttpResponse(status=400)

    order.crate = None
    crate.status = Crate.CrateStatus.IDLE
    crate.save()
    order.save()

    return HttpResponse(status=204)

@require_POST
@transaction.atomic
def complete_crate_printing(request, crate_id):
    crate = get_object_or_404(Crate.objects.select_for_update(), id=crate_id)
    
    if not crate.has_order:
        return HttpResponse(status=409)

    order = crate.order

    if order.status != Order.OrderStatus.PROCESSING:
        return HttpResponse(status=409)

    try:
        complete_printing(order)
    except ValueError:
        return HttpResponse(status=400)

    crate.status = Crate.CrateStatus.PROCESSING
    crate.save(update_fields=["status"])

    return HttpResponse(status=204)

