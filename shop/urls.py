from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PaymentViewSet, TeamViewSet, TeamMemberViewSet, CategoryViewSet, ProductViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'team-members', TeamMemberViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
  path('api/', include(router.urls)),
]