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
  visible = models.BooleanField('Visible', default=True)

  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name = "Product"
    verbose_name_plural = "Products"
    # ordering = by most frequently bought?


class Order(models.Model):
  datetime = models.DateTimeField(auto_now_add=True, editable=False)
  by = models.ForeignKey(TeamMember, verbose_name='Made by', related_name='orders', on_delete=models.CASCADE)
  total_amount = models.DecimalField('Total amount', max_digits=10, decimal_places=2)

  def calculate_total(self):
    return self.items.aggregate(
      total=Sum(F("quantity") * F("unit_price"), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    )["total"] or 0

  def save(self, *args, **kwargs):
    if self.pk:
      self.total_amount = self.calculate_total()
    else:
      self.total_amount = 0 # Should be temporary if all goes well
    super().save(*args, **kwargs)
  
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
  unit_price = models.DecimalField('Unit price', max_digits=5, decimal_places=2)

  def save(self, *args, **kwargs):
    if not self.unit_price:
      self.unit_price = self.product.price
    super().save(*args, **kwargs)

  def __str__(self):
    return f'{self.quantity}x {self.product.name} @ €{self.unit_price}'
  
  class Meta:
    verbose_name = "Order item"
    verbose_name_plural = "Order items"
    constraints = [
      models.UniqueConstraint(fields=["product", "order"], name="unique_product_per_order")
    ]


class Payment(models.Model):
  by = models.ForeignKey(TeamMember, verbose_name='Made by', on_delete=models.CASCADE)
  description = models.TextField('Description', blank=True)
  amount = models.DecimalField('Amount', max_digits=5, decimal_places=2)
  proof_picture = models.ImageField('Proof picture', upload_to="payment_proofs", blank=True)
  completed = models.BooleanField('Completed', default=False)

  def __str__(self):
    return f"Request by {self.by.name} - {self.amount} ({'Completed' if self.completed else 'Pending'})"
  
  class Meta:
    verbose_name = "Payment"
    verbose_name_plural = "Payments"
    ordering = ['completed']

