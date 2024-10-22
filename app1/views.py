import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from .models import RoomCategory, Room, Reservation, SpecialRate
from .serializers import RoomCategorySerializer, ReservationSerializer

# Create your views here.
def index(request):
    return render(request,'index.html')

@api_view(['GET'])
def room_categories_view(request):
    """
    Fetch all room categories.
    """
    categories = RoomCategory.objects.all()
    serializer = RoomCategorySerializer(categories, many=True)
    return Response(serializer.data)


def calculate_total_price_with_special_rates(room_category, start_date, end_date):
    """
    Calculate total price for a room category considering special rates for the selected date range.
    """
    total_days = (end_date - start_date).days
    total_price = 0

    # Fetch all special rates that overlap with the reservation period
    special_rates = SpecialRate.objects.filter(
        room_category=room_category,
        start_date__lte=end_date,
        end_date__gte=start_date
    )

    # Loop through each day in the reservation period
    for day in range(total_days):
        current_date = start_date + timedelta(days=day)
        rate_multiplier = 1  # Default to base rate

        # Check if a special rate applies for the current day
        for rate in special_rates:
            if rate.start_date <= current_date <= rate.end_date:
                rate_multiplier = rate.rate_multiplier
                break

        # Calculate the price for the day, considering the special rate
        total_price += room_category.base_price * rate_multiplier

    return total_price


# Room Availability Check API
# @api_view(['GET'])
# def available_rooms_view(request):
#     """
#     Check available rooms based on category and date range.
#     """
#     category_id = request.GET.get('category_id')
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')

#     # Fetch all rooms in the selected category
#     rooms = Room.objects.filter(category_id=category_id)

#     # Filter out rooms that are booked during the selected date range
#     reserved_rooms = Reservation.objects.filter(
#         room__in=rooms,
#         start_date__lt=end_date,
#         end_date__gt=start_date
#     ).values_list('room_id', flat=True)

#     available_rooms = rooms.exclude(id__in=reserved_rooms)
#     available_room_numbers = available_rooms.values_list('room_number', flat=True)
#     return Response({'available_rooms': list(available_room_numbers)})

@api_view(['GET'])
def available_rooms_view(request):
    """
    Check available rooms based on category and date range, and calculate base price with special rates.
    """
    category_id = request.GET.get('category_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Convert start_date and end_date to date objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Fetch all rooms in the selected category
    rooms = Room.objects.filter(category_id=category_id)

    # Filter out rooms that are booked during the selected date range
    reserved_rooms = Reservation.objects.filter(
        room__in=rooms,
        start_date__lt=end_date,
        end_date__gt=start_date
    ).values_list('room_id', flat=True)

    available_rooms = rooms.exclude(id__in=reserved_rooms)
    available_room_numbers = available_rooms.values_list('room_number', flat=True)
    # return Response({'available_rooms': list(available_room_numbers)})

    # Calculate the total price for each available room
    room_data = []
    for room in available_rooms:
        base_price = room.category.base_price
        total_price = calculate_total_price_with_special_rates(room.category, start_date, end_date)
        
        room_data.append({
            'room_number': room.room_number,
            'base_price': base_price,
            'total_price': total_price,
        })

    # return Response({'available_rooms': room_data})
    return Response({'available_rooms': list(available_room_numbers)})




@csrf_exempt
def make_reservation_view(request):

    print(request.body)
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({'error': 'Empty request body.'}, status=400)
        
        try:
            # Log the raw request body for debugging
            # print(request.body)
            print("Raw request body:", request.body)

            # Parse the incoming JSON data
            data = json.loads(request.body)
            room_number = data.get('room_number')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            customer_name = data.get('customer_name')

            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            if end_date <= start_date:
                return JsonResponse({'error': 'End date must be after start date.'}, status=400)


            # Fetch the room object
            room = Room.objects.get(room_number=room_number)


            # Create the reservation
            reservation = Reservation.objects.create(
                room=room,
                start_date=start_date,
                end_date=end_date,
                customer_name=customer_name
            )

            # return JsonResponse({'message': 'Reservation successful!'}, status=201)

            return JsonResponse({
                'total_price': reservation.total_price,
                'room_number': room_number,
                'start_date': str(start_date),
                'end_date': str(end_date)
            }, status=201)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Room not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)