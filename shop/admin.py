from django.contrib import admin
from shop.models import Category, Order, OrderItem, Product, Team, TeamMember

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


admin.site.register(Team)
admin.site.register(Category)
admin.site.register(Product)
