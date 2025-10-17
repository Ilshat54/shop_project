from django.db import models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=255, blank=True, null=True)  # путь к картинке


    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.name

    @property
    def id(self):
        return self.category_id 


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    characteristics = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, db_column="category_id")
    image = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name

    @property
    def id(self):
        return self.product_id

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "users"   # сказать Django: используй таблицу users
        managed = False      # Django НЕ будет создавать/изменять таблицу через миграции

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Новый")

    # добавленные вручную в БД
    address = models.CharField(max_length=255, blank=True, null=True)
    delivery_time = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "orders"  # чтобы Django понимал, что таблица уже есть

    def __str__(self):
        return f"Заказ #{self.order_id} от {self.user}"


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
