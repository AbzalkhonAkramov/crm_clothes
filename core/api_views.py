from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ClothesProduct, Order
from .serializers import ClothesProductSerializer, OrderSerializer, OrderCreateSerializer


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClothesProduct.objects.all()
    serializer_class = ClothesProductSerializer
    permission_classes = [IsAuthenticated]


class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer