
from django.contrib import admin
from .models import Car, Favorite, RentalRequest, Payment


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'brand',
        'model',
        'year',
        'price',
        'city',
        'owner',
        'is_active',
        'created_at',
    )

    list_filter = (
        'city',
        'year',
        'transmission',
        'is_active',
    )

    search_fields = (
        'brand',
        'model',
        'owner__username',
        'owner__email',
        'phone_number',
    )

    date_hierarchy = 'created_at'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'car',
    )

    list_filter = (
        'user',
    )

    search_fields = (
        'user__username',
        'car__brand',
        'car__model',
    )


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = (
        'renter',
        'car',
        'start_date',
        'end_date',
        'total_price',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'start_date',
        'created_at',
    )

    search_fields = (
        'renter__username',
        'renter__email',
        'car__brand',
        'car__model',
        'car__owner__username',
    )

    list_editable = ('status',)

    date_hierarchy = 'created_at'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'rental',
        'amount',
        'status',
        'refund_amount',
        'cancellation_fee',
        'refund_status',
        'created_at',
    )

    list_filter = (
        'status',
        'refund_status',
        'created_at',
    )

    search_fields = (
        'rental__renter__username',
        'rental__car__brand',
        'rental__car__model',
    )

    date_hierarchy = 'created_at'
