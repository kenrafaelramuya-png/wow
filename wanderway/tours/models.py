from django.db import models
from django.contrib.auth.models import User


class TourPackage(models.Model):

    name = models.CharField(
        max_length=200
    )

    destination = models.CharField(
        max_length=200
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    duration = models.CharField(
        max_length=100
    )

    available_slots = models.PositiveIntegerField(
        default=20
    )

    def __str__(self):
        return self.name


class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    tour = models.ForeignKey(
        TourPackage,
        on_delete=models.CASCADE
    )

    number_of_people = models.PositiveIntegerField(
        default=1
    )

    booking_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.tour.name}"
        )


class CustomerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone_number = models.CharField(
        max_length=20
    )

    def __str__(self):
        return self.user.username


class Payment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ('GCash', 'GCash'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.booking.user.username} - "
            f"{self.payment_method} - "
            f"{self.payment_status}"
        )