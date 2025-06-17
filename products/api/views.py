from rest_framework.views import APIView
from rest_framework.response import Response
from products.models import Product
from products.api.serializers import ProductSerializer


class ProductApiView(APIView):
    def get(self, request):
        asdasd = (
            Product.objects.select_related("vendor", "category", "brand")
            .prefetch_related("colors", "sizes", "tag", "product_images")
            .get(id=5)
        )

        serializer = ProductSerializer(asdasd)
        return Response(serializer.data)
