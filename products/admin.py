from django.contrib import admin
from .models import (
    Category,
    Brand,
    Color,
    Size,
    Tag,
    Product,
    ProductImage,
    ProductVariant,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("vendor",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    search_fields = ("name",)
    list_filter = ("vendor",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    search_fields = ("name",)
    list_filter = ("vendor",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    search_fields = ("name",)
    list_filter = ("vendor",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    search_fields = ("name",)
    list_filter = ("vendor",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "vendor",
        "category",
        "brand",
        "is_active",
        "is_featured",
        "is_custom_price",
        "current_price",
    )
    search_fields = ("name", "description")
    list_filter = ("vendor", "category", "brand", "is_active", "is_featured")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline]
    filter_horizontal = ("tag", "sizes")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "brand", "color", "stock", "current_price")
    list_filter = ("brand", "color")
    search_fields = ("product__name",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image")
    search_fields = ("product__name",)
