from rest_framework import serializers
from .models import Payment, Team, TeamMember, Category, Product, Order, OrderItem


class TeamSerializer(serializers.ModelSerializer):
  class Meta:
    model = Team
    fields = "__all__"


class TeamMemberSerializer(serializers.ModelSerializer):
  team = TeamSerializer(read_only=True)

  class Meta:
    model = TeamMember
    fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
  category = CategorySerializer(read_only=True)

  class Meta:
    model = Product
    fields = "__all__"
    fields = ["id", "name", "image", "description", "cost_price", "price", "category", "visible"]
    read_only_fields = ["price"]


class OrderItemSerializer(serializers.ModelSerializer):
  product = ProductSerializer(read_only=True)
  product_id = serializers.PrimaryKeyRelatedField(
    queryset=Product.objects.all(), source="product", write_only=True
  )

  class Meta:
    model = OrderItem
    fields = ["id", "product", "product_id", "unit_price", "quantity"]
    read_only_fields = ["unit_price"]


class OrderSerializer(serializers.ModelSerializer):
  items = OrderItemSerializer(many=True)

  class Meta:
    model = Order
    fields = ["id", "datetime", "by", "items", "total_amount"]
    read_only_fields = ["id", "datetime", "total_amount"]

  def create(self, validated_data):
    items_data = validated_data.pop("items")
    order = Order.objects.create(**validated_data)

    for item_data in items_data:
      OrderItem.objects.create(order=order, **item_data)

    order.save()
    return order


class PaymentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Payment
    fields = ["id", "by", "description", "amount", "proof_picture", "completed"]
    read_only_fields = ["completed"]
