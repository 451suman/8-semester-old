from django.db import models

from common.models import TimeStampedModel
from django.utils.text import slugify
from vendor.models import Vendor


class Category(TimeStampedModel):
    arrange_choices = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(
        max_length=100,
    )
    slug = models.SlugField()
    arranged = models.PositiveIntegerField(choices=arrange_choices, null = True, blank = True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Brand(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="brands_logo/", null=True, blank=True)

    def __str__(self):
        return self.name


class Color(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Size(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=10)  # E.g., S, M, L, XL or 42, 44

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    tag = models.ManyToManyField(Tag)
    is_featured = models.BooleanField(default=False)
    # --------------------------------------------------------------------------------------
    is_custom_price = models.BooleanField(default=False, null=True, blank=True)
    stock = models.PositiveIntegerField(null=True, blank=True)
    colors = models.ManyToManyField(Color, blank=True, null=True)
    sizes = models.ManyToManyField(Size, blank=True, null=True)
    previous_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    current_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    # ---------------------------
    colors = models.ManyToManyField(
        Color, through="ProductVariant", related_name="products"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Only update slug if it's not already set or if name has changed
        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = models.ImageField(upload_to="products/images/")

    def __str__(self):
        return f"{self.product.name} image"


class ProductVariant(models.Model):  # This is the `through` model
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    previous_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    current_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        unique_together = ("product", "brand", "color")  # Optional but recommended
