from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class RoomCategory(models.Model):
    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name
    
class Room(models.Model):
    room_number = models.CharField(max_length=10)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number}"
    
class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    customer_name = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Reservation by {self.customer_name} for {self.room}"

    def save(self, *args, **kwargs):
        # Ensure no overlapping reservations
        if Reservation.objects.filter(
            room=self.room,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exists():
            raise ValueError("This room is already booked for the selected dates.")
        # Calculate the total price
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def calculate_total_price(self):
        # Default to base price of the room category
        total_price = 0
        days = (self.end_date - self.start_date).days
        special_rates = SpecialRate.objects.filter(
            room_category=self.room.category,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        )

        for day in range(days):
            current_date = self.start_date + timedelta(days=day)
            rate_multiplier = 1
            # Check if a special rate applies for the current day
            for rate in special_rates:
                if rate.start_date <= current_date <= rate.end_date:
                    rate_multiplier = rate.rate_multiplier
                    break
            total_price += self.room.category.base_price * rate_multiplier

        return total_price

class SpecialRate(models.Model):
    room_category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    rate_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    def __str__(self):
        return f"Special rate for {self.room_category}"