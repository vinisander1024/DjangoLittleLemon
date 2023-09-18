from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Menu,Category,Cart,Booking,BookingItem
from .serializers import MenuSerializer, CategorySerializer, CartSerializer,BookingSerializer,BookingItemSerializer
from rest_framework.permissions import IsAuthenticated,BasePermission
import datetime
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


class ManagerGroupPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Manager').exists() or request.user.is_superuser


class ManagerGroupView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            group = Group.objects.get(name='Manager')
            users = group.user_set.all()
            return Response(users.values())
        else:
            return Response({'error': 'You are not authorized to access this view.'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            group = Group.objects.get(name='Manager')
            user.groups.add(group)
            return Response({'message': 'User added to the Manager group.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'You are not authorized to access this view.'}, status=status.HTTP_401_UNAUTHORIZED)
        
    def delete(self, request, id):
        user = get_object_or_404(User, id=id)
        if user.groups.filter(name="Manager").exists():
            if request.user.groups.filter(name="Manager").exists():
                group = Group.objects.get(name='Manager')
                user.groups.remove(group)
                return Response({'message': 'User removed from the Manager group.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You are not authorized to access this view.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'The provided ID does not belong to the Manager group.'}, status=status.HTTP_404_NOT_FOUND)


class deliveryCrewGroupView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            group = Group.objects.get(name='DeliveryCrew')
            users = group.user_set.all()
            return Response(users.values())
        else:
            return Response({'error': 'You are not authorized to access this view.'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            group = Group.objects.get(name='DeliveryCrew')
            user.groups.add(group)
            return Response({'message': 'User added to the delivery crew group.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'You are not authorized to access this view.'}, status=status.HTTP_401_UNAUTHORIZED)
            
    def delete(self, request, id):
        print("in delete view")
        user = get_object_or_404(User, id=id)
        print("user",user)
        if user.groups.filter(name="DeliveryCrew").exists():
            if request.user.groups.filter(name="Manager").exists():
                group = Group.objects.get(name='DeliveryCrew')
                user.groups.remove(group)
                return Response({'message': 'User removed from the delivery crew group.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You are not authorized to access this view.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'The provided ID does not belong to the delivery crew group.'}, status=status.HTTP_404_NOT_FOUND)


# Category Views

class categoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        return [IsAuthenticated(), ManagerGroupPermission()]


class singleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        return [IsAuthenticated(), ManagerGroupPermission()]


    
class menuView(generics.ListCreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    ordering_fileds = ['price','title','category']
    filterset_fields = ['price','feature','category']
    search_fields = ['category','title']

    def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        return [IsAuthenticated(), ManagerGroupPermission()]


class singleMenuView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        return [IsAuthenticated(), ManagerGroupPermission()]

# cart view 
class cartView(generics.GenericAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get(self, request):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# Booking view 
class BookingView(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='DeliveryCrew').exists():
            bookings = Booking.objects.filter(delivery_crew=user)
        else:
            bookings = Booking.objects.filter(user=user)
        return bookings

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Retrieve related BookingItem objects for each Booking
        for i, booking_data in enumerate(data):
            booking = queryset[i]
            booking_items = booking.bookingitem_set.all()
            booking_item_serializer = BookingItemSerializer(booking_items, many=True)
            booking_data['booking_items'] = booking_item_serializer.data

        return Response(data)

    def post(self, request):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)

        # Create the Booking instance
        booking_data = {
            'user': user.pk,
            'delivery_crew': None,
            'status': False,
            'total': 0,
            'date': datetime.date.today()
        }
        booking_serializer = BookingSerializer(data=booking_data)
        if booking_serializer.is_valid():
            booking = booking_serializer.save()
        else:
            errors = booking_serializer.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        booking_items = []
        for cart_item in cart_items:
            booking_item_data = {
                'booking_id': booking.pk,
                'menu': cart_item.menu.pk,
                'quantity': cart_item.quantity,
                'unit_price': cart_item.unit_price,
                'price': cart_item.price
            }
            booking_item_serializer = BookingItemSerializer(data=booking_item_data)
            if booking_item_serializer.is_valid():
                booking_item_serializer.save()
                booking_items.append(booking_item_serializer.data)
            else:
                errors = booking_item_serializer.errors
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(booking_serializer.data, status=status.HTTP_201_CREATED)



class singleBookingView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        elif self.request.method == 'PATCH' and self.request.user.groups.filter(name='DeliveryCrew').exists():
            return []  
        else:
            return [IsAuthenticated(), ManagerGroupPermission()]
        

