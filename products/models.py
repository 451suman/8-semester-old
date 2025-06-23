from django.db import models
from django.utils.text import slugify
from common.models import TimeStampedModel  # Created/Updated timestamp
from vendor.models import Vendor


class Category(TimeStampedModel):
    ARRANGE_CHOICES = [(i, str(i)) for i in range(1, 7)]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    arranged = models.PositiveIntegerField(choices=ARRANGE_CHOICES, null=True, blank=True)

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
    name = models.CharField(max_length=10)  # e.g., S, M, L or 42, 44

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
    slug = models.SlugField(unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_custom_price = models.BooleanField(default=False, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="products")
    tag = models.ManyToManyField(Tag, blank=True)

    # Fallback prices (used if variant pricing not available)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ManyToMany to Size directly (for global size availability)
    sizes = models.ManyToManyField(Size, blank=True)

    # Colors handled through ProductVariant
    colors = models.ManyToManyField(Color, through="ProductVariant", related_name="products")

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_price_for(self, color=None, size=None):
        try:
            variant = ProductVariant.objects.get(product=self, color=color, size=size)
            return variant.current_price or self.current_price
        except ProductVariant.DoesNotExist:
            return self.current_price


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)

    previous_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ("product", "color", "size")
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"

    def __str__(self):
        parts = [self.product.name]
        if self.color: parts.append(self.color.name)
        if self.size: parts.append(self.size.name)
        return " - ".join(parts)


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to="products/images/")

    def __str__(self):
        return f"{self.product.name} image"
