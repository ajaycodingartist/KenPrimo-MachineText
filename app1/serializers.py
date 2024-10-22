from rest_framework import serializers
from .models import RoomCategory, Room, Reservation

class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCategory
        fields = ['id', 'name', 'base_price']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'category', 'is_available']


class ReservationSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)  # Show room details in the response

    class Meta:
        model = Reservation
        fields = ['id', 'room', 'start_date', 'end_date', 'customer_name', 'total_price']

    def create(self, validated_data):
        room = validated_data.get('room')
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        # Check for overlapping reservations
        if Reservation.objects.filter(
            room=room,
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists():
            raise serializers.ValidationError("This room is already booked for the selected dates.")

        # Create the reservation and calculate the price
        reservation = Reservation.objects.create(**validated_data)
        reservation.total_price = reservation.calculate_total_price()
        reservation.save()
        return reservation
