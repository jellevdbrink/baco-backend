from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator

class Team(models.Model):
  number = models.PositiveIntegerField('Number', unique=True)
  start_date = models.DateField('Start date')

  def __str__(self):
    return f"EST {self.number}.0"
  
  class Meta:
    verbose_name = "Team"
    verbose_name_plural = "Teams"
    ordering = ['-number']
    get_latest_by = "start_date"


class TeamMember(models.Model):
  name = models.CharField('Name', max_length=50)
  email = models.EmailField('Email')
  team = models.ForeignKey(Team, verbose_name='Team', related_name='team_members', on_delete=models.RESTRICT)
  balance = models.DecimalField('Balance', max_digits=10, decimal_places=2, default=0)

  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name = "Team member"
    verbose_name_plural = "Team members"
    constraints = [
      models.UniqueConstraint(fields=["name", "team"], name="unique_team_member_name")
    ]


class Category(models.Model):
  name = models.CharField('Name', unique=True, max_length=50)
  icon = models.CharField('Icon', max_length=20)

  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name = "Category"
    verbose_name_plural = "Categories"


class Product(models.Model):
  name = models.CharField('Name', max_length=100)
  image = models.ImageField('Image', upload_to='product_images')
  description = models.TextField('Description', max_length=255, blank=True)
  price = models.DecimalField('Price', decimal_places=2, max_digits=5)
  category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.RESTRICT)

  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name = "Product"
    verbose_name_plural = "Products"
    # ordering = by most frequently bought?


class Order(models.Model):
  datetime = models.DateTimeField(auto_now_add=True, editable=False)
  by = models.ForeignKey(TeamMember, verbose_name='Made by', related_name='orders', on_delete=models.CASCADE)

  @property
  def total_amount(self):
    return self.items.aggregate(
        total=Sum(
          F("quantity") * F("product__price"),
          output_field=models.DecimalField(max_digits=6, decimal_places=2)
        )
      )["total"] or 0
  
  def __str__(self):
    return f"Order on {self.datetime.strftime('%d/%m/%y')} by {self.by.name}"
  
  class Meta:
    verbose_name = "Order"
    verbose_name_plural = "Orders"
    ordering = ['-datetime']
    get_latest_by = "datetime"


class OrderItem(models.Model):
  product = models.ForeignKey(Product, verbose_name='Product', on_delete=models.CASCADE)
  order = models.ForeignKey(Order, verbose_name='Order', related_name='items', on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField('Quantity', validators=[MinValueValidator(1)])

  def __str__(self):
    return f'{self.quantity}x {self.product.name}'
  
  class Meta:
    verbose_name = "Order item"
    verbose_name_plural = "Order items"
    constraints = [
      models.UniqueConstraint(fields=["product", "order"], name="unique_product_per_order")
    ]

