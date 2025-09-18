from rest_framework import viewsets, mixins
from .models import Team, TeamMember, Category, Product, Order
from .serializers import (
  TeamSerializer, TeamMemberSerializer, CategorySerializer,
  ProductSerializer, OrderSerializer
)

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Team.objects.all()
  serializer_class = TeamSerializer


class TeamMemberViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = TeamMember.objects.all()
  serializer_class = TeamMemberSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Category.objects.all()
  serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer

  def get_queryset(self):
    queryset = Product.objects.all()
    category_id = self.request.query_params.get('category')
    if category_id is not None:
      queryset = queryset.filter(category_id=category_id)
    return queryset


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, 
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Order.objects.all().select_related("by").prefetch_related("items__product")
  serializer_class = OrderSerializer
