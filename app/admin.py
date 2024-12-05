from django.contrib import admin
from .models import *
from django.contrib import admin
from .models import OrderItem
from django.db.models import Sum,F
from django.http import HttpResponseForbidden

# Register your models here.
# admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(InputProduct)
# admin.site.register(Order)
# admin.site.register(ShippingAddress)
# admin.site.register(Payment_VNPay)
# admin.py


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'order', 'quantity', 'date_added', 'get_total')
    search_fields = ('product__name', 'order__id')
    verbose_name = "Mặt hàng trong đơn"
    verbose_name_plural = "Mặt hàng trong đơn"
# @admin.register(Invoice)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'customer', 'product', 'order', 'quantity', 'date_added', 'get_total','state',)
#     search_fields = ('product__name', 'order__id')
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'product_name', 'quantity', 'get_total', 'state', 'date_added')

    def changelist_view(self, request, extra_context=None):
        # Giới hạn quyền xem trang cho admin
        if not request.user.is_superuser:
            return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")

        # Tính tổng doanh thu và tổng số đơn hàng đã thanh toán
        total_revenue = Invoice.objects.filter(state='paid').aggregate(total=Sum('product__price'))['total'] or 0
        total_orders = Invoice.objects.filter(state='paid').count()

        # Tính tổng số lượng sản phẩm đã bán
        total_quantity = Invoice.objects.filter(state='paid').aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

        # Tính doanh thu và số lượng bán theo sản phẩm
        revenue_by_product = Invoice.objects.filter(state='paid').values('product__name').annotate(
            total_quantity_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('product__price'))
        )

        extra_context = extra_context or {}
        extra_context['total_revenue'] = total_revenue
        extra_context['total_orders'] = total_orders
        extra_context['total_quantity'] = total_quantity
        extra_context['revenue_by_product'] = revenue_by_product

        return super().changelist_view(request, extra_context=extra_context)
    class Meta:
        verbose_name = "Hóa đơn"
        verbose_name_plural = "Hóa đơn"
admin.site.register(Invoice, InvoiceAdmin)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    verbose_name = "Danh mục sản phẩm"
    verbose_name_plural = "Danh mục sản phẩm"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    verbose_name = "Sản phẩm"
    verbose_name_plural = "Sản phẩm"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    verbose_name = "Đơn hàng"
    verbose_name_plural = "Đơn hàng"


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    verbose_name = "Địa chỉ giao hàng"
    verbose_name_plural = "Địa chỉ giao hàng"

@admin.register(Payment_VNPay)
class PaymentVNPayAdmin(admin.ModelAdmin):
    verbose_name = "Thanh toán VNPay"
    verbose_name_plural = "Thanh toán VNPay"
