from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from shop.models import Category, Order, OrderItem, Payment, Product, Team, TeamMember
from django.utils.html import format_html
from django.db.models import Sum, F

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  readonly_fields = ("total_amount", "datetime")

  def has_add_permission(self, request, obj=None):
    return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
  def has_add_permission(self, request, obj=None):
    return False
    

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
  list_display = ("name", "balance")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
  change_form_template = "admin/payment_changeform.html"

  readonly_fields = ("proof_preview",)

  def proof_preview(self, obj):
    if obj.proof_picture:
      return format_html('<img src="{}" style="max-height: 200px;"/>', obj.proof_picture.url)
    return "No image uploaded"
  
  proof_preview.short_description = "Proof Preview"

  def get_urls(self):
    urls = super().get_urls()
    custom_urls = [
      path(
        "<int:pk>/complete/",
        self.admin_site.admin_view(self.process_complete),
        name="payment-complete",
      ),
    ]
    return custom_urls + urls

  def process_complete(self, request, pk, *args, **kwargs):
    payment = Payment.objects.get(pk=pk)
    if not payment.completed:
      payment.by.balance += payment.amount
      payment.by.save()
      payment.completed = True
      payment.save()
      self.message_user(request, "Payment completed and balance updated!", messages.SUCCESS)
    else:
      self.message_user(request, "Payment already completed.", messages.WARNING)
    return redirect(f"../../{pk}/change/")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  change_list_template = "admin/product_dashboard.html"

  def changelist_view(self, request, extra_context=None):
    # Top products (by quantity sold)
    top_products = (
      OrderItem.objects
      .values("product__name")
      .annotate(total_sold=Sum("quantity"))
      .order_by("-total_sold")[:10]
    )
    labels_products = [p["product__name"] for p in top_products]
    values_products = [float(p["total_sold"]) for p in top_products]

    # Top users (by money spent)
    top_users = (
      TeamMember.objects
      .values("name")
      .annotate(total_spent=Sum(F("orders__items__quantity") * F("orders__items__unit_price")))
      .order_by("-total_spent")[:10]
    )
    labels_users = [u["name"] for u in top_users]
    values_users = [float(u["total_spent"]) for u in top_users]

    # Total balances across all team members
    total_balance = TeamMember.objects.aggregate(total_balance=Sum("balance"))["total_balance"] or 0

    # Total amount spent across all orders
    total_spent = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0

    extra_context = extra_context or {}
    extra_context.update({
      "labels_products": labels_products,
      "values_products": values_products,
      "labels_users": labels_users,
      "values_users": values_users,
      "total_balance": float(total_balance),
      "total_spent": float(total_spent),
    })
    return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Team)
admin.site.register(Category)
