from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BoxForm
from .models import Box


def box_list(request):
    boxes = Box.objects.all().order_by('name')
    return render(request, 'boxes/box_list.html', {'boxes': boxes})


def box_create(request):
    if request.method == 'POST':
        form = BoxForm(request.POST)
        if form.is_valid():
            box = form.save()
            messages.success(request, f"Box '{box.name}' created successfully.")
            return redirect('box_list')
    else:
        form = BoxForm()
    return render(request, 'boxes/box_form.html', {
        'form': form,
        'title': 'Add New Packaging Box',
        'button_text': 'Create Box',
    })


def box_update(request, pk):
    box = get_object_or_404(Box, pk=pk)
    if request.method == 'POST':
        form = BoxForm(request.POST, instance=box)
        if form.is_valid():
            box = form.save()
            messages.success(request, f"Box '{box.name}' updated successfully.")
            return redirect('box_list')
    else:
        form = BoxForm(instance=box)
    return render(request, 'boxes/box_form.html', {
        'form': form,
        'box': box,
        'title': f"Edit Box: {box.name}",
        'button_text': 'Update Box',
    })


def box_delete(request, pk):
    box = get_object_or_404(Box, pk=pk)
    if request.method == 'POST':
        name = box.name
        box.delete()
        messages.success(request, f"Box '{name}' deleted successfully.")
        return redirect('box_list')
    return render(request, 'boxes/box_confirm_delete.html', {'box': box})
