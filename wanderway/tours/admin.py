from django.contrib import admin
from .models import (
    TourPackage,
    Booking,
    CustomerProfile,
    Payment,
)


# =========================
# TOUR PACKAGE
# =========================

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'destination',
        'price',
        'duration',
        'available_slots',
    )

    search_fields = (
        'name',
        'destination',
    )

    list_filter = (
        'destination',
    )


# =========================
# CUSTOMER
# =========================

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'username',
        'email',
        'phone_number',
    )

    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__username',
        'user__email',
        'phone_number',
    )

    @admin.display(description='Full Name')
    def full_name(self, obj):

        full_name = (
            f'{obj.user.first_name} '
            f'{obj.user.last_name}'
        ).strip()

        if full_name:
            return full_name

        return obj.user.username

    @admin.display(description='Username')
    def username(self, obj):
        return obj.user.username

    @admin.display(description='Email')
    def email(self, obj):
        return obj.user.email


# =========================
# BOOKINGS
# =========================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'booker_name',
        'booker_email',
        'booker_phone',
        'tour',
        'number_of_people',
        'booking_date',
        'status',
    )

    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__username',
        'user__email',
        'user__customerprofile__phone_number',
        'tour__name',
        'tour__destination',
    )

    list_filter = (
        'status',
        'tour',
        'booking_date',
    )

    ordering = (
        '-booking_date',
    )

    @admin.display(description='Booker Name')
    def booker_name(self, obj):

        full_name = (
            f'{obj.user.first_name} '
            f'{obj.user.last_name}'
        ).strip()

        if full_name:
            return full_name

        return obj.user.username

    @admin.display(description='Email')
    def booker_email(self, obj):
        return obj.user.email

    @admin.display(description='Phone')
    def booker_phone(self, obj):

        try:
            return obj.user.customerprofile.phone_number

        except CustomerProfile.DoesNotExist:
            return 'No phone number'

    # -------------------------
    # DELETE BOOKING
    # -------------------------

    def delete_model(self, request, obj):

        tour = obj.tour
        people = obj.number_of_people

        tour.available_slots += people
        tour.save()

        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):

        for booking in queryset:

            tour = booking.tour

            tour.available_slots += (
                booking.number_of_people
            )

            tour.save()

        super().delete_queryset(
            request,
            queryset
        )


# =========================
# PAYMENTS
# =========================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        'customer_name',
        'tour_name',
        'payment_method',
        'amount',
        'payment_status',
        'payment_date',
    )

    search_fields = (
        'booking__user__first_name',
        'booking__user__last_name',
        'booking__user__username',
        'booking__user__email',
        'booking__tour__name',
    )

    list_filter = (
        'payment_method',
        'payment_status',
        'payment_date',
    )

    ordering = (
        '-payment_date',
    )

    @admin.display(description='Customer Name')
    def customer_name(self, obj):

        full_name = (
            f'{obj.booking.user.first_name} '
            f'{obj.booking.user.last_name}'
        ).strip()

        if full_name:
            return full_name

        return obj.booking.user.username

    @admin.display(description='Tour')
    def tour_name(self, obj):
        return obj.booking.tour.name