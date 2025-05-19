from rest_framework import serializers
from .models import ClothesProduct, Customer, Order, OrderItem


class ClothesProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothesProduct
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'total_amount', 'items']
        read_only_fields = ['order_date', 'total_amount']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['customer', 'status', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # Calculate total amount
        total_amount = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            total_amount += product.price * quantity

        # Create order
        order = Order.objects.create(
            **validated_data,
            total_amount=total_amount
        )

        # Create order items
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            # Update product stock
            product.stock_quantity -= quantity
            product.save()

        return order