from django.contrib import admin
from shop.models import Category, Order, OrderItem, Product, Team, TeamMember

class OrderAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False


class OrderItemAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
