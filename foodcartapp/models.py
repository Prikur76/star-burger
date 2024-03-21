from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Count,Sum, Prefetch
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=250,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def total_cost(self):
        return self.prefetch_related(
            Prefetch(
                'products',
                queryset=OrderItem.objects.select_related('product')
            )
        ).annotate(
            cost=Sum(F('products__quantity') * F('products__product__price'))
        )


class Order(models.Model):
    STATUSES = [
        ('CREATED', 'создан'),
        ('IN_PROGRESS', 'готовится'),
        ('IN_DELIVERY', 'доставляется'),
        ('COMPLETED', 'завершен'),
    ]
    PAYMENT_METHODS = [
        ('CASH', 'наличные'),
        ('CARD', 'карта')
    ]

    firstname = models.CharField(
        'имя',
        max_length=50,
        db_index=True
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        db_index=True
    )
    phonenumber = PhoneNumberField(
        'телефон',
        region='RU',
        max_length=20
    )
    address = models.CharField(
        'адрес',
        max_length=150,
        db_index=True
    )
    status = models.CharField(
        'статус',
        max_length=20,
        choices=STATUSES,
        default='CREATED',
        db_index=True
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=20,
        choices=PAYMENT_METHODS,
        default='CASH',
        db_index=True
    )
    comment = models.TextField(
        'комментарий',
        blank=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='ресторан',
        null=True,
        blank=True
    )
    registered_at = models.DateTimeField(
        'создан',
        auto_now_add=True,
        db_index=True
    )
    called_at = models.DateTimeField(
        'звонок',
        blank=True,
        null=True
    )
    delivered_at = models.DateTimeField(
        'доставлен',
        blank=True,
        null=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"Order #{self.id}: {self.firstname} {self.lastname} - {self.address}"

    def get_available_restaurants(self):
        available_restaurants = None
        if not self.restaurant:
            available_restaurants = Restaurant.objects.filter(
                menu_items__product__in=self.products.values_list('product', flat=True),
                menu_items__availability=True
            ).annotate(
                availability_count=Count('menu_items__product')
            ).filter(
                availability_count__gt=0
            ).distinct()
        return available_restaurants


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='продукт',
    )
    quantity = models.PositiveIntegerField(
        'количество',
        validators=[MinValueValidator(0)]
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'позиция в заказе'
        verbose_name_plural = 'позиции в заказе'

    def __str__(self):
        return f"Order {self.order.id}: {self.quantity} x {self.product.name}"
