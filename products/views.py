from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProductForm
from .models import Product


def product_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'products/product_list.html', {'products': products})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' created successfully.")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Add New Product',
        'button_text': 'Create Product',
    })


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'title': f"Edit Product: {product.name}",
        'button_text': 'Update Product',
    })


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            name = product.name
            product.delete()
            messages.success(request, f"Product '{name}' deleted successfully.")
            return redirect('product_list')
        except ProtectedError:
            messages.error(
                request,
                f"Cannot delete product '{product.name}' because it is linked to existing packaging orders."
            )
            return redirect('product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})
