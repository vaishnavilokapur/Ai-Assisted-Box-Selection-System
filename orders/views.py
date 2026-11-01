"""
PackWise - Order & Box Recommendation Views
"""

from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from boxes.models import Box
from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem
from orders.services import recommend_box_for_order
from products.models import Product


def order_create_view(request):
    """
    Handles order creation with multiple products and separate quantities,
    then executes box recommendation logic.
    """
    products = Product.objects.all().order_by('name')
    boxes_count = Box.objects.count()

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        # Parse selected products and quantities
        # Supports both dynamic row arrays and checkbox-based rows
        raw_product_ids = request.POST.getlist('product_id')
        raw_quantities = request.POST.getlist('quantity')

        selected_items = []
        parsing_error = None

        if raw_product_ids and raw_quantities:
            # Dynamic rows submission
            for p_id_str, qty_str in zip(raw_product_ids, raw_quantities):
                p_id_str = p_id_str.strip()
                qty_str = qty_str.strip()
                if not p_id_str or not qty_str:
                    continue
                try:
                    p_id = int(p_id_str)
                    qty = int(qty_str)
                    if qty <= 0:
                        parsing_error = "Product quantities must be positive integers (at least 1)."
                        break
                    selected_items.append((p_id, qty))
                except ValueError:
                    parsing_error = "Invalid product ID or quantity provided."
                    break
        else:
            # Checkbox table fallback: 'selected_products' with 'quantity_<id>'
            checked_ids = request.POST.getlist('selected_products')
            for p_id_str in checked_ids:
                try:
                    p_id = int(p_id_str)
                    qty_str = request.POST.get(f'quantity_{p_id}', '1').strip()
                    qty = int(qty_str)
                    if qty <= 0:
                        parsing_error = "Product quantities must be positive integers (at least 1)."
                        break
                    selected_items.append((p_id, qty))
                except ValueError:
                    parsing_error = "Invalid quantity specified for selected product."
                    break

        # Validate that at least one product was selected
        if not selected_items and not parsing_error:
            parsing_error = "Please select at least one product with a valid quantity."

        if form.is_valid() and not parsing_error:
            # Verify all products exist in catalog
            product_id_map = {p.id: p for p in products}
            valid_items = []
            for p_id, qty in selected_items:
                if p_id in product_id_map:
                    valid_items.append((product_id_map[p_id], qty))
                else:
                    parsing_error = f"Product with ID {p_id} was not found."
                    break

            if not parsing_error and valid_items:
                # 1. Create and save the Order
                order = Order.objects.create(
                    order_number=form.cleaned_data['order_number']
                )

                # 2. Combine duplicate product entries if user selected same product twice
                consolidated: dict = {}
                for prod, qty in valid_items:
                    consolidated[prod] = consolidated.get(prod, 0) + qty

                # 3. Save OrderItem records
                for prod, qty in consolidated.items():
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        quantity=qty
                    )

                # Redirect to recommendation result view
                return redirect('order_recommendation', order_id=order.id)

        # If form or product parsing errors occurred
        if parsing_error:
            messages.error(request, parsing_error)

        return render(request, 'orders/order_form.html', {
            'form': form,
            'products': products,
            'boxes_count': boxes_count,
            'selected_post_items': selected_items,
        })

    else:
        form = OrderCreateForm()
        return render(request, 'orders/order_form.html', {
            'form': form,
            'products': products,
            'boxes_count': boxes_count,
        })


def order_recommendation_view(request, order_id):
    """
    Renders the box recommendation result for a specific order.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id
    )

    # Execute recommendation logic
    recommendation = recommend_box_for_order(order)

    # Detailed item breakdown for presentation
    items_breakdown = []
    total_qty = 0
    for item in order.items.all():
        prod = item.product
        vol = prod.length * prod.width * prod.height
        line_weight = prod.weight * item.quantity
        line_volume = vol * item.quantity
        total_qty += item.quantity
        items_breakdown.append({
            'name': prod.name,
            'dimensions': f"{prod.length} x {prod.width} x {prod.height} cm",
            'unit_weight': prod.weight,
            'unit_volume': vol,
            'quantity': item.quantity,
            'total_weight': line_weight,
            'total_volume': line_volume,
        })

    box = recommendation.get('box')

    context = {
        'order': order,
        'recommendation': recommendation,
        'box': box,
        'items_breakdown': items_breakdown,
        'total_quantity': total_qty,
        'total_weight': recommendation.get('total_weight', Decimal('0.00')),
        'total_volume': recommendation.get('total_volume', Decimal('0.00')),
        'success': recommendation.get('success', False),
        'message': recommendation.get('message', ''),
        'placements': recommendation.get('placements', []),
    }

    return render(request, 'orders/recommendation_result.html', context)


def order_list_view(request):
    """
    Lists recent orders and provides direct links to view box recommendations.
    """
    orders = Order.objects.prefetch_related('items__product').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


def dashboard_home_view(request):
    """
    Renders the central logistics dashboard with dynamic statistics,
    quick actions, recent orders, and workflow guide.
    """
    total_products = Product.objects.count()
    available_boxes = Box.objects.count()
    total_orders = Order.objects.count()
    orders_requiring_box = Order.objects.filter(items__isnull=False).distinct().count()

    recent_orders = Order.objects.prefetch_related('items__product').order_by('-created_at')[:5]

    recent_orders_data = []
    for ord_obj in recent_orders:
        item_count = sum(it.quantity for it in ord_obj.items.all())
        recent_orders_data.append({
            'order': ord_obj,
            'item_count': item_count,
        })

    current_date = timezone.now()

    context = {
        'total_products': total_products,
        'available_boxes': available_boxes,
        'total_orders': total_orders,
        'orders_requiring_box': orders_requiring_box,
        'recent_orders_data': recent_orders_data,
        'current_date': current_date,
    }
    return render(request, 'home.html', context)
