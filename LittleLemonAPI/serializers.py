from rest_framework import serializers
from .models import Menu,Category,Cart,Booking,BookingItem
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

# Category Serializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']

# Menu Serializer

class MenuSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nested CategorySerializer for GET request
    category_id = serializers.IntegerField(
        write_only=True
    )
    class Meta:
        model = Menu
        fields = ['id','title','price','featured','category','category_id']
        validators=[
        UniqueTogetherValidator(
        queryset=Menu.objects.all(),
        fields=['title', 'category_id']
        )
        ]

# Cart Serializer

class CartSerializer(serializers.ModelSerializer):
    menu = MenuSerializer(read_only=True)  
    menu_id = serializers.IntegerField(
        write_only=True
    )
    class Meta:
        model = Cart
        fields = ['user','menu','quantity','unit_price','price',"menu_id"]

# Booking Serializer

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id','user', 'delivery_crew', 'status', 'total', 'date']



class BookingItemSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)  # Nested BookingSerializer for GET request
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(),
        write_only=True,
        source='vooking'
    )

    class Meta:
        model = BookingItem
        fields = ['booking', 'vooking_id', 'menu', 'quantity', 'unit_price', 'price']


