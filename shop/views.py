from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from datetime import date, timedelta
from django.db.models.functions import TruncDate
from django.utils.timezone import now
from .models import OrderItem, Team, TeamMember, Category, Product, Order, Payment
from .serializers import (
  TeamSerializer, TeamMemberSerializer, CategorySerializer,
  ProductSerializer, OrderSerializer, PaymentSerializer
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


class PaymentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Payment.objects.all()
  serializer_class = PaymentSerializer


class AnalyticsViewSet(viewsets.ViewSet):
  @action(detail=False, methods=["get"], url_path='top-products')
  def top_products(self, request):
    qs = (
      OrderItem.objects
      .values("product__name")
      .annotate(total_sold=Sum("quantity"))
      .order_by("-total_sold")[:5]
    )
    labels = [item["product__name"] for item in qs]
    values = [item["total_sold"] for item in qs]
    return Response({"labels": labels, "values": values})

  @action(detail=False, methods=["get"], url_path='top-users')
  def top_users(self, request):
    qs = (
      Order.objects
      .values("by__name")
      .annotate(total_spent=Sum("total_amount"))
      .order_by("-total_spent")[:5]
    )
    labels = [item["by__name"] for item in qs]
    values = [item["total_spent"] for item in qs]
    return Response({"labels": labels, "values": values})

  @action(detail=False, methods=["get"])
  def summary(self, request):
    user_id = request.query_params.get("user_id")

    if user_id:
      orders = Order.objects.filter(by_id=user_id)
    else:
      orders = Order.objects.all()
    
    total_spent = orders.aggregate(total=Sum("total_amount"))["total"] or 0
    total_orders = orders.count()

    avg_order_value = round(total_spent / total_orders, 2) if total_orders > 0 else 0.00

    start_date = date(2025, 9, 23)
    end_date = now().date()

    if total_orders > 0 and end_date >= start_date:
        total_days = sum(
            1 for i in range((end_date - start_date).days + 1)
            if (start_date + timedelta(days=i)).weekday() < 5
        )
        total_days = max(total_days, 1)
        avg_orders_per_day = round(total_orders / total_days, 1)
    else:
        avg_orders_per_day = 0.0

    return Response({
      "total_spent": total_spent,
      "total_orders": total_orders,
      "avg_order_value": avg_order_value,
      "avg_orders_per_day": avg_orders_per_day,
    })
  
  @action(detail=False, methods=["get"], url_path='sales-over-time')
  def sales_over_time(self, request):
    days = int(request.query_params.get("days", 30))
    start_date = now().date() - timedelta(days=days)
    end_date = now().date()

    qs = (
      OrderItem.objects
      .filter(order__datetime__date__gte=start_date)
      .annotate(date=TruncDate("order__datetime"))
      .values("date")
      .annotate(total=Sum("quantity"))
    )
    totals_by_date = {item["date"]: float(item["total"]) for item in qs}

    labels, values = [], []
    current = start_date
    while current <= end_date:
      labels.append(current.strftime("%d-%m"))
      values.append(totals_by_date.get(current, 0.0))
      current += timedelta(days=1)

    return Response({"labels": labels, "values": values})
