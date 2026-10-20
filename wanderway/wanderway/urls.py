from django.contrib import admin
from django.urls import path

from tours.views import (
    home,
    signup,
    login_view,
    logout_view,
    tours,
    book_tour,
    confirm_booking,
    booking_success,
    my_bookings,
    cancel_booking,
    payment,
    demo_payment,
    payment_success,
    admin_dashboard,
)


urlpatterns = [
    path('', home, name='home'),

    # Django built-in admin
    path('admin/', admin.site.urls),

    # Custom Admin Dashboard
    path(
        'admin-dashboard/',
        admin_dashboard,
        name='admin_dashboard'
    ),

    # Authentication
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Tours
    path('tours/', tours, name='tours'),

    # Booking
    path(
        'book/<int:tour_id>/',
        book_tour,
        name='book_tour'
    ),
    path(
        'confirm-booking/<int:tour_id>/',
        confirm_booking,
        name='confirm_booking'
    ),
    path(
        'booking-success/',
        booking_success,
        name='booking_success'
    ),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path(
        'cancel-booking/<int:booking_id>/',
        cancel_booking,
        name='cancel_booking'
    ),

    # Payment
    path(
        'payment/<int:booking_id>/',
        payment,
        name='payment'
    ),
    path(
        'demo-payment/<int:booking_id>/',
        demo_payment,
        name='demo_payment'
    ),
    path(
        'payment-success/<int:booking_id>/',
        payment_success,
        name='payment_success'
    ),
]