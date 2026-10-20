from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count

from .models import (
    TourPackage,
    Booking,
    CustomerProfile,
    Payment,
)


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')

        if not username or not password:
            return render(request, 'signup.html', {
                'error': 'Username and password are required.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {
                'error': 'Username already exists.'
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        CustomerProfile.objects.create(
            user=user,
            phone_number=phone_number or ''
        )

        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')

            return redirect('home')

        return render(request, 'login.html', {
            'error': 'Invalid username or password.'
        })

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# =========================
# ADMIN DASHBOARD
# =========================

@staff_member_required(login_url='login')
def admin_dashboard(request):
    total_bookings = Booking.objects.count()

    total_customers = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).count()

    total_tours = TourPackage.objects.count()

    pending_bookings = Booking.objects.filter(
        status='Pending'
    ).count()

    confirmed_bookings = Booking.objects.filter(
        status='Confirmed'
    ).count()

    recent_bookings = (
        Booking.objects
        .select_related('user', 'tour')
        .order_by('-booking_date')[:8]
    )

    monthly_stats = []
    current_date = timezone.localtime().date()

    for offset in range(5, -1, -1):
        month_index = current_date.month - offset
        year = current_date.year

        while month_index <= 0:
            month_index += 12
            year -= 1

        count = Booking.objects.filter(
            booking_date__year=year,
            booking_date__month=month_index
        ).count()

        month_date = timezone.datetime(
            year, month_index, 1
        )

        monthly_stats.append({
            'month': month_date.strftime('%b'),
            'total': count,
        })

    context = {
        'total_bookings': total_bookings,
        'total_customers': total_customers,
        'total_tours': total_tours,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'recent_bookings': recent_bookings,
        'monthly_stats': monthly_stats,
    }

    return render(
        request,
        'admin_dashboard.html',
        context
    )


# =========================
# TOURS
# =========================

def tours(request):
    tour_packages = TourPackage.objects.all()

    return render(request, 'tours.html', {
        'tours': tour_packages
    })


# =========================
# BOOK TOUR
# =========================

@login_required
def book_tour(request, tour_id):
    tour = get_object_or_404(TourPackage, id=tour_id)

    if request.method == 'POST':
        try:
            number_of_people = int(
                request.POST.get('number_of_people')
            )
        except (TypeError, ValueError):
            return render(request, 'book_tour.html', {
                'tour': tour,
                'error': 'Please enter a valid number of people.'
            })

        if number_of_people < 1:
            return render(request, 'book_tour.html', {
                'tour': tour,
                'error': 'Number of people must be at least 1.'
            })

        if number_of_people > tour.available_slots:
            return render(request, 'book_tour.html', {
                'tour': tour,
                'error': (
                    f'Only {tour.available_slots} '
                    'slot(s) are available.'
                )
            })

        total_price = tour.price * number_of_people

        return render(request, 'booking.html', {
            'tour': tour,
            'number_of_people': number_of_people,
            'total_price': total_price
        })

    return render(request, 'book_tour.html', {
        'tour': tour
    })


# =========================
# CONFIRM BOOKING
# =========================

@login_required
def confirm_booking(request, tour_id):
    tour = get_object_or_404(TourPackage, id=tour_id)

    if request.method != 'POST':
        return redirect('book_tour', tour_id=tour.id)

    try:
        number_of_people = int(
            request.POST.get('number_of_people')
        )
    except (TypeError, ValueError):
        return redirect('book_tour', tour_id=tour.id)

    if number_of_people < 1:
        return redirect('book_tour', tour_id=tour.id)

    if number_of_people > tour.available_slots:
        return render(request, 'book_tour.html', {
            'tour': tour,
            'error': (
                f'Only {tour.available_slots} '
                'slot(s) are available.'
            )
        })

    booking = Booking.objects.create(
        user=request.user,
        tour=tour,
        number_of_people=number_of_people,
        status='Pending'
    )

    tour.available_slots -= number_of_people
    tour.save()

    return redirect('payment', booking_id=booking.id)


# =========================
# PAYMENT
# =========================

@login_required
def payment(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    total_price = (
        booking.tour.price * booking.number_of_people
    )

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method != 'GCash':
            return render(request, 'payment.html', {
                'booking': booking,
                'total_price': total_price,
                'error': 'Please select GCash.'
            })

        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                'payment_method': 'GCash',
                'amount': total_price,
                'payment_status': 'Pending'
            }
        )

        return redirect(
            'demo_payment',
            booking_id=booking.id
        )

    return render(request, 'payment.html', {
        'booking': booking,
        'total_price': total_price
    })


# =========================
# DEMO PAYMENT
# =========================

@login_required
def demo_payment(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    payment = get_object_or_404(
        Payment,
        booking=booking
    )

    if request.method == 'POST':
        payment.payment_status = 'Paid'
        payment.save()

        booking.status = 'Confirmed'
        booking.save()

        return redirect(
            'payment_success',
            booking_id=booking.id
        )

    return render(request, 'demo_payment.html', {
        'booking': booking,
        'payment': payment
    })


# =========================
# PAYMENT SUCCESS
# =========================

@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    payment = get_object_or_404(
        Payment,
        booking=booking
    )

    return render(request, 'payment_success.html', {
        'booking': booking,
        'payment': payment
    })


# =========================
# BOOKING SUCCESS
# =========================

@login_required
def booking_success(request):
    return render(request, 'booking_success.html')


# =========================
# MY BOOKINGS
# =========================

@login_required
def my_bookings(request):
    bookings = (
        Booking.objects
        .filter(user=request.user)
        .select_related('tour')
        .order_by('-booking_date')
    )

    return render(request, 'my_bookings.html', {
        'bookings': bookings
    })


# =========================
# CANCEL BOOKING
# =========================

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if request.method != 'POST':
        return redirect('my_bookings')

    if booking.status != 'Confirmed':
        messages.error(
            request,
            'Only confirmed bookings can be cancelled.'
        )
        return redirect('my_bookings')

    cancellation_deadline = (
        booking.booking_date + timedelta(hours=3)
    )

    if timezone.now() > cancellation_deadline:
        messages.error(
            request,
            'This booking can no longer be cancelled.'
        )
        return redirect('my_bookings')

    booking.status = 'Cancelled'
    booking.save()

    tour = booking.tour
    tour.available_slots += booking.number_of_people
    tour.save()

    try:
        payment = Payment.objects.get(booking=booking)
        payment.payment_status = 'Failed'
        payment.save()
    except Payment.DoesNotExist:
        pass

    messages.success(
        request,
        'Booking cancelled successfully.'
    )

    return redirect('my_bookings')