from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from shop.models import Category, Order, OrderItem, Payment, Product, Team, TeamMember
from django.utils.html import format_html

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
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


admin.site.register(Team)
admin.site.register(Category)
admin.site.register(Product)
