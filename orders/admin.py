from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'created_at', 'get_total_items')
    search_fields = ('order_number',)
    inlines = [OrderItemInline]

    @admin.display(description='Total Items')
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__order_number', 'product__name')
    list_filter = ('product',)
