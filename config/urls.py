
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from cars import views


urlpatterns = [
    # Django ადმინისტრაცია
    path('admin/', admin.site.urls),

    # მომხმარებლის აუთენტიკაცია
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # მთავარი გვერდი
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),

    # ავტომობილენი
    path('add-car/', views.add_car_view, name='add_car'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),

    # რჩეულები
    path(
        'car/<int:car_id>/favorite/',
        views.toggle_favorite,
        name='toggle_favorite'
    ),

    # სიმულირებული გადახდა
    path(
        'car/<int:car_id>/rent/',
        views.rent_car,
        name='rent_car'
    ),

    # ჯავშვნის გაუქმება და თანხის დაბრუნების სიმულაცია
    path(
        'rental/<int:rental_id>/cancel/',
        views.cancel_paid_rental,
        name='cancel_paid_rental'
    ),

    # მანქანის მენეჯმენტი
    path(
        'car/<int:car_id>/edit/',
        views.edit_car,
        name='edit_car'
    ),
    path(
        'car/<int:car_id>/delete/',
        views.delete_car,
        name='delete_car'
    ),

    # ენის შეცვლა
    path('i18n/', include('django.conf.urls.i18n')),
]


# სურათები
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
