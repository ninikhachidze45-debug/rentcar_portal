
import random
from datetime import date
from decimal import Decimal, InvalidOperation

# django-ს შეტყობინებების სისტემა
from django.contrib import messages

# მომხმარებლის ავტორიზაციისა და ანგარიშების მართვის ფუნქციები
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

# უზრუნველყოფს რამდენიმე მონაცემთა ბაზის ოპერაციის
# შესრულებას ერთიან ტრანზაქციად.
from django.db import transaction

#მონაცემების რაოდენობის დასათვლელად
from django.db.models import Count

# get_object_or_404 ობიექტს ეძებს მონაცემთა ბაზაში,
# თუ ობიექტი არ არსებობს, ავტომატურად აბრუნებს 404 შეცდომას.
# redirect მომხმარებელს სხვა გვერდზე გადაიყვანს
# render HTML აბრუნებს შაბლონს მონაცემებთან ერთად ბრაუზერში გამოსაჩენად
from django.shortcuts import get_object_or_404, redirect, render

#თარიღისა და დროის სწორად შესანახად
from django.utils import timezone

# require_POST უზრუნველყოფს, რომ ფუნქცია მხოლოდ POST მოთხოვნით იქნას გამოიძახებული
from django.views.decorators.http import require_POST

# მონაცემთა ბაზის მოდელები.
from .models import Car, Favorite, RentalRequest, Payment


# get_user_model() აბრუნებს პროექტში გამოყენებულ მომხმარებლის მოდელს.
User = get_user_model()

#=============================
# CITIES — ქალაქების სია
#=============================



CITIES = [
    {'slug': 'tbilisi', 'ka': 'თბილისი', 'en': 'Tbilisi'},
    {'slug': 'batumi', 'ka': 'ბათუმი', 'en': 'Batumi'},
    {'slug': 'kutaisi', 'ka': 'ქუთაისი', 'en': 'Kutaisi'},
    {'slug': 'rustavi', 'ka': 'რუსთავი', 'en': 'Rustavi'},
    {'slug': 'gori', 'ka': 'გორი', 'en': 'Gori'},
    {'slug': 'zugdidi', 'ka': 'ზუგდიდი', 'en': 'Zugdidi'},
    {'slug': 'poti', 'ka': 'ფოთი', 'en': 'Poti'},
    {'slug': 'telavi', 'ka': 'თელავი', 'en': 'Telavi'},
    {'slug': 'akhaltsikhe', 'ka': 'ახალციხე', 'en': 'Akhaltsikhe'},
    {'slug': 'mtskheta', 'ka': 'მცხეთა', 'en': 'Mtskheta'},
    {'slug': 'ozurgeti', 'ka': 'ოზურგეთი', 'en': 'Ozurgeti'},
    {'slug': 'ambrolauri', 'ka': 'ამბროლაური', 'en': 'Ambrolauri'},
    {'slug': 'akhalkalaki', 'ka': 'ახალქალაქი', 'en': 'Akhalkalaki'},
    {'slug': 'senaki', 'ka': 'სენაკი', 'en': 'Senaki'},
    {'slug': 'samtredia', 'ka': 'სამტრედია', 'en': 'Samtredia'},
    {'slug': 'borjomi', 'ka': 'ბორჯომი', 'en': 'Borjomi'},
]


# თითოეული ქალაქისთვის შექმნილია შესაძლო დასახელებების სიას.
# მაგალითად, თბილისი შეიძლება შეგვხვდეს შემდეგი ფორმებით:
# "tbilisi", "Tbilisi" ან "თბილისი".
#
# casefold() ტექსტს გარდაქმნის ისე, რომ შედარებისას
# დიდი და პატარა ასოები განსხვავებულად არ ჩაითვალოს.


CITY_ALIASES = {
    city['slug']: [
        city['slug'],
        city['en'].casefold(),
        city['ka'].casefold()
    ]
    for city in CITIES
}


def normalize_city(city_name):
    """
    ქალაქის დასახელება მოჰყავს ერთიან ფორმატში
    თუ მიღებული დასახელება არც ერთ ქალაქს არ ემთხვევა,
    ფუნქცია აბრუნებს None-ს
    """

    city_name = str(city_name or '').strip().casefold()

  
    for city, aliases in CITY_ALIASES.items():
        if city_name in aliases:
            return city

    return None

#===========================================
# HELPER FUNCTIONS — დამხმარე ფუნქციები
#===========================================



def get_user_data(user):
    """
    მომხმარებლის ინფორმაციას ლექსიკონის სახით აბრუნებს.

    """

    return {
        'firstName': user.first_name,
        'lastName': user.last_name,
        'phoneNumber': user.username,
        'email': user.email,
        'role': 'User',
    }


def car_to_dict(car):
    """
    ავტომობილის მოდელის ობიექტს გარდაქმნის ლექსიკონად

    ასე ავტომობილის მონაცემები
    HTML შაბლონს უფრო მარტივად გადაეცემა

    ასევე მუშავდება სურათების მისამართები
    """

   
    image1 = car.image1.url if car.image1 else ''
    image2 = car.image2.url if car.image2 else ''
    image3 = car.image3.url if car.image3 else ''

    return {
        'id': car.id,
        'brand': car.brand,
        'model': car.model,
        'year': car.year,
        'price': car.price,
        'capacity': car.capacity,
        'transmission': car.transmission,
        'city': car.city,
        'fuelCapacity': car.fuel_capacity,
        'phoneNumber': car.phone_number,
        'email': car.owner.email,

        # სურათების მისამართები.
        'imageUrl1': image1,
        'imageUrl2': image2,
        'imageUrl3': image3,

        # იგივე მისამართები ალტერნატიული სახელებით
        'image1': image1,
        'image2': image2,
        'image3': image3,

        # ავტომობილის მფლობელის მომხმარებლის სახელი
        'createdBy': car.owner.username,
    }


def get_car_photos(car):
    """
    აბრუნებს კონკრეტული ავტომობილის არსებული ფოტოების სიას

    """

    photos = []


    for image in [car.image1, car.image2, car.image3]:

        if image:
            photos.append(image.url)

    return photos


def get_car_queryset():
    """
    აბრუნებს აქტიური ავტომობილების QuerySet-ს

    filter(is_active=True) — აჩვენებს მხოლოდ აქტიურ განცხადებებს
    select_related('owner') — ავტომობილის მფლობელის მონაცემებს
    იმავე მონაცემთა ბაზის მოთხოვნაში იღებს

    """

    return (
        Car.objects
        .filter(is_active=True)
        .select_related('owner')
    )


# ===========================================
# HOME PAGE — მთავარი გვერდი
# ===========================================

def home(request):
    """
    1. აქტიური ავტომობილების მიღება
    2. ავტომობილების ფილტრაცია
    3. პოპულარული ავტომობილების შერჩევა
    4. შემთხვევითი ავტომობილების შერჩევა
    5. მომხმარებლის რჩეული ავტომობილების მიღება
    6. მონაცემების home.html შაბლონში გადაცემა
    """

    # მონაცემთა ბაზაში ყველა აქტიური ავტომობილის სიად გარდაქმნა
    
    all_cars = list(get_car_queryset())

    # სიის დამოუკიდებელი ასლის შექმნა, რომ ფილტრაციამ all_cars სიას არ შეცვალოს
    cars = all_cars.copy()

    # GET მეთოდით ვიღებთ მონაცემებს  URL-ის პარამეტრებიდან
    city = request.GET.get('city', '')
    year_from = request.GET.get('year_from', '')
    year_to = request.GET.get('year_to', '')
    capacity = request.GET.get('capacity', '')

    # ერთი კონკრეტული წლის ფილტრაციის ალტერნატიული პარამეტრი
    single_year = request.GET.get('year', '')


    if single_year:
        year_from = single_year
        year_to = single_year

    # ------------------------------
    # ქალაქის მიხედვით ფილტრაცია
    # ------------------------------

    if city:
        normalized_filter_city = normalize_city(city)

        if normalized_filter_city:
            cars = [
                car for car in cars
                if normalize_city(car.city) == normalized_filter_city
            ]
        else:
           
            cars = []

    # ------------------------------
    # მინიმალური წლის ფილტრაცია
    # ------------------------------

    try:
        if year_from:
            cars = [
                car for car in cars
                if car.year >= int(year_from)
            ]

    except (ValueError, TypeError):
        year_from = ''

    # ------------------------------
    # მაქსიმალური წლის ფილტრაცია
    # ------------------------------

    try:
        if year_to:
            cars = [
                car for car in cars
                if car.year <= int(year_to)
            ]

    except (ValueError, TypeError):
        year_to = ''

    # ------------------------------
    # ადგილების რაოდენობის ფილტრაცია
    # ------------------------------

    try:
        if capacity:
            cars = [
                car for car in cars
                if car.capacity == int(capacity)
            ]

    except (ValueError, TypeError):
        capacity = ''

    # ფილტრაციის პირობები ერთმანეთისგან დამოუკიდებლად სრულდება.

    # ------------------------------
    # პოპულარული ავტომობილები
    # ------------------------------

    popular_cars = (
        Car.objects
        .filter(is_active=True)

        # მფლობელის მონაცემები წინასწარ იტვირთება
        .select_related('owner')

        # rental_requests საშუალებით ვითვლით,
        # რამდენი გაქირავების მოთხოვნა აქვს ავტომობილს
        .annotate(rental_count=Count('rental_requests'))

        # პირველ რიგში მეტი გაქირავების მქონე ავტომობილები გამოჩნდება,
        # თუ რაოდენობა ერთნაირია, უფრო ახალი განცხადება იქნება პირველი
        .order_by('-rental_count', '-created_at')[:4]
    )

    # ------------------------------
    # შემთხვევითი ავტომობილები
    # ------------------------------

    # ვქმნით აქტიური ავტომობილების სიის ასლს
    random_cars = all_cars.copy()

    random.shuffle(random_cars)

    # ------------------------------
    # რჩეული ავტომობილები
    # ------------------------------

    # set ინახავს ავტომობილების id-ების 
    # თუ მომხმარებელი ავტორიზებული არაა, სეტი ცარიელია
    favorite_ids = set()

    if request.user.is_authenticated:

        # values_list() აბრუნებს მხოლოდ car_id ველების მნიშვნელობებს
        # flat=True შედეგს მარტივ სიად გარდაქმნის
        favorite_ids = set(
            Favorite.objects.filter(
                user=request.user
            ).values_list('car_id', flat=True)
        )

    # ------------------------------
    # მონაცემების გადაცემა HTML შაბლონში
    # ------------------------------

    return render(request, 'cars/home.html', {

        # პოპულარული ავტომობილების პირველი ოთხი ჩანაწერი
        'popular_cars': [
            car_to_dict(car) for car in popular_cars
        ],

        # შემთხვევით შერჩეული მაქსიმუმ ოთხი ავტომობილი
        'random_cars': [
            car_to_dict(car) for car in random_cars[:4]
        ],

        # მომხმარებლის მიერ არჩეული ფილტრების შესაბამისი ავტომობილები
        'cars': [
            car_to_dict(car) for car in cars
        ],

        'favorite_ids': favorite_ids,

        # ფილტრაციისთვის საჭირო ჩამონათვალები.
        'cities': CITIES,
        'years': range(2026, 1989, -1),
        'capacities': range(2, 10),

        # შენახული ფილტრების მნიშვნელობები
        'selected_city': city,
        'selected_year_from': year_from,
        'selected_year_to': year_to,
        'selected_capacity': capacity,

        # True ნიშნავს, რომ მომხმარებელმა მინიმუმ ერთი ფილტრი მაინც გამოიყენა
        'is_filtered': bool(
            city or year_from or year_to or capacity
        ),
    })


# ========================
# CAR DETAILS 
# ========================

def car_detail(request, car_id):
    """
    კონკრეტული ავტომობილის დეტალური ინფორმაციის გვერდი

    ფუნქცია ასევე ამოწმებს რჩეულ სტატუსს და ითვლის გაქირავების ფასს
    """

    # ვეძებთ აქტიურ ავტომობილს მისი id-ის მიხედვით
    car = get_object_or_404(
        get_car_queryset(),
        id=car_id
    )

    # საწყისად ავტომობილი რჩეულებში არ არის
    is_favorite = False

    if request.user.is_authenticated:

        is_favorite = Favorite.objects.filter(
            user=request.user,
            car=car
        ).exists()

    rental_estimate = None

    
    rental_start_date = ''
    rental_end_date = ''

    # ფასის გამოთვლა სრულდება მხოლოდ მაშინ,
    # როდესაც მომხმარებელი POST მოთხოვნას აგზავნის
    # და მოქმედების ტიპია calculate_price
    if (
        request.method == 'POST'
        and request.POST.get('action') == 'calculate_price'
    ):

        # ვიღებთ გაქირავების დაწყებისა და დასრულების თარიღებს
        rental_start_date = request.POST.get('start_date', '')
        rental_end_date = request.POST.get('end_date', '')

        try:
            # fromisoformat() ტექსტურ თარიღს date ობიექტად გარდაქმნის
            start_date = date.fromisoformat(rental_start_date)
            end_date = date.fromisoformat(rental_end_date)

            # ვანგარიშობთ გაქირავების დღეების რაოდენობას
            total_days = (end_date - start_date).days

           
            daily_price = Decimal(str(car.price))

            # მოწმდება:
            # დაწყების თარიღი წარსულში არ იყოს;
            # გაქირავების ხანგრძლივობა მინიმუმ ერთი დღე იყოს;
            if (
                start_date < date.today()
                or total_days < 1
                or daily_price <= 0
            ):
                messages.error(
                    request,
                    'Please choose valid rental dates.'
                )

            else:
                # იქმნება გამოთვლის შედეგის ლექსიკონი
                # იგი გამოიყენება გვერდზე დღეებისა და საერთო ფასის საჩვენებლად
                rental_estimate = {
                    'days': total_days,
                    'total': daily_price * total_days,
                }

        except (ValueError, TypeError, InvalidOperation):
            messages.error(
                request,
                'Please enter valid rental dates.'
            )

    # HTML შაბლონს გადაეცემა ავტომობილის ინფორმაციას,
    # ფოტოებს, მომხმარებლის რჩეულ სტატუსს და ფასის გამოთვლის შედეგს
    return render(request, 'cars/car_detail.html', {
        'car': car_to_dict(car),
        'photos': get_car_photos(car),
        'today': date.today(),
        'is_favorite': is_favorite,
        'rental_estimate': rental_estimate,
        'rental_start_date': rental_start_date,
        'rental_end_date': rental_end_date,
    })


# ==================================================
# FAVORITES — რჩეულებში დამატება და წაშლა
# ==================================================

@login_required
@require_POST
def toggle_favorite(request, car_id):
    """
    ერთი და იგივე ღილაკი ორივე მოქმედებას ასრულებს
    თუ ავტომობილი უკვე რჩეულებშია, წაიშლება,
    წინააღმდეგ შემთხვევაში, დაემატება
    """

    # ვიღებ მხოლოდ აქტიურ ავტომობილს
    car = get_object_or_404(
        get_car_queryset(),
        id=car_id
    )

    # ვეძებ მიმდინარე მომხმარებლისა და ავტომობილის შესაბამის ჩანაწერს
    favorite = Favorite.objects.filter(
        user=request.user,
        car=car
    )

    if favorite.exists():

        # თუ ჩანაწერი არსებობს, ვშლი რჩეულებიდან
        favorite.delete()

        messages.info(request, 'Car removed from your favorites.')

    else:

        # თუ ჩანაწერი არ არსებობს, ვქმნი ახალ ჩანაწერს
        Favorite.objects.create(
            user=request.user,
            car=car
        )

        messages.success(request, 'Car added to your favorites.')

    # მომხმარებელი ბრუნდება კონკრეტული ავტომობილის დეტალურ გვერდზე
    return redirect('car_detail', car_id=car_id)


# ==================================================
# RENT A CAR — ავტომობილის გაქირავება
# ==================================================

@login_required
@require_POST
def rent_car(request, car_id):
    """
    ავტომობილის დაჯავშნა და სიმულირებული გადახდის შექმნა

    რეალურ საბანკო გადახდას არ სრულდება
    """

    # ------------------------------
    # თარიღების მიღება და შემოწმება
    # ------------------------------

    try:
        start_date = date.fromisoformat(
            request.POST.get('start_date', '')
        )

        end_date = date.fromisoformat(
            request.POST.get('end_date', '')
        )

    except (ValueError, TypeError):

        # თუ თარიღის ფორმატი არასწორია, მომხმარებელი უკან ბრუნდება
        messages.error(request, 'Please enter valid rental dates.')

        return redirect('car_detail', car_id=car_id)

    # ვანგარიშობ გაქირავების ხანგრძლივობას
    total_days = (end_date - start_date).days

    # დაწყების თარიღი არ უნდა იყოს წარსულში,
    # ხოლო დასრულების თარიღი დაწყების თარიღზე გვიან უნდა იყოს
    if start_date < date.today() or total_days < 1:
        messages.error(
            request,
            'Choose a valid start date and an end date after the start date.'
        )

        return redirect('car_detail', car_id=car_id)

    # ------------------------------
    # მონაცემთა ბაზის ტრანზაქცია
    # ------------------------------

    # atomic() უზრუნველყოფს ოპერაციების ერთიან შესრულებას
    # თუ ტრანზაქციის რომელიმე ოპერაცია შეცდომით დასრულდება,
    # მონაცემთა ბაზაში ცვლილებები გაუქმდება
    with transaction.atomic():

        car = get_object_or_404(
            Car.objects.select_for_update().select_related('owner'),
            id=car_id,
            is_active=True
        )

        # მომხმარებელს არ შეუძლია საკუთარი ავტომობილის დაჯავშნა
        if car.owner == request.user:
            messages.error(request, 'You cannot rent your own car.')
            return redirect('car_detail', car_id=car_id)

        # ავტომობილის დღიური ფასის Decimal ფორმატში მიღება
        daily_price = Decimal(str(car.price))

        if daily_price <= 0:
            messages.error(request, 'This car has an invalid rental price.')
            return redirect('car_detail', car_id=car_id)

        # ------------------------------
        # თარიღების გადაკვეთის შემოწმება
        # ------------------------------

        # მომწდება არსებობს თუ არა იმავე ავტომობილზე
        # უკვე გადახდილი ჯავშანი, რომლის თარიღებიც
        # მომხმარებლის მიერ არჩეულ პერიოდს ემთხვევა
        #
        # start_date__lt=end_date ნიშნავს, რომ არსებული
        # ჯავშნის დაწყების თარიღი ახალი ჯავშნის დასრულებამდეა
        #
        # end_date__gt=start_date ნიშნავს, რომ არსებული
        # ჯავშნის დასრულების თარიღი ახალი ჯავშნის დაწყების შემდეგაა
        #
        # ორივე პირობის შესრულება ნიშნავს, რომ პერიოდები იკვეთება
        overlapping_rental = RentalRequest.objects.filter(
            car=car,
            status='paid',
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists()

        if overlapping_rental:
            messages.error(
                request,
                'This car is already booked for some of these dates.'
            )

            return redirect('car_detail', car_id=car_id)

        # ------------------------------
        # საბოლოო ფასის გამოთვლა
        # ------------------------------

        total_price = daily_price * total_days

        # ვქმნით გაქირავების ჩანაწერს
        # სტატუსი paid ნიშნავს, რომ დაჯავშნა დადასტურებულია
        rental = RentalRequest.objects.create(
            renter=request.user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            total_price=total_price,
            status='paid',
        )

        # ------------------------------
        # სიმულირებული გადახდა
        # ------------------------------

        # რეალური საბანკო სისტემის ნაცვლად ავტომატურად
        # იქმნება წარმატებული გადახდის ჩანაწერი
        #
        # timezone.now() აბრუნებს მიმდინარე თარიღსა და დროს
        Payment.objects.create(
            rental=rental,
            amount=total_price,
            status='successful',
            paid_at=timezone.now(),
        )

    # ტრანზაქციის წარმატებით დასრულების შემდეგ მომხმარებელს
    # ვაჩვენებთ დადასტურების შეტყობინებას.
    messages.success(
        request,
        (
            f'Booking confirmed! Simulated payment of '
            f'{total_price:.2f} was successful.'
        )
    )

    # მომხმარებელი გადადის პროფილზე, სადაც შეუძლია ჯავშნის ნახვა.
    return redirect('profile')


# ==================================================
# CANCEL PAID RENTAL — ჯავშნის გაუქმება და თანხის დაბრუნება
# ==================================================

@login_required
@require_POST
def cancel_paid_rental(request, rental_id):
    """

    დაბრუნებული თანხა დამოკიდებულია იმაზე,
    რამდენი დღე დარჩა გაქირავების დაწყებამდე

    თანხის დაბრუნება სიმულირებულია
    """

    # უზრუნველყოფს ჯავშნისა და გადახდის
    # სტატუსების თანმიმდევრულ განახლებას
    with transaction.atomic():

        # იძებნება გადახდილი ჯავშანი და იკეტება მისი ჩანაწერი
        rental = get_object_or_404(
            RentalRequest.objects.select_for_update().select_related(
                'car',
                'car__owner'
            ),
            id=rental_id,
            renter=request.user,
            status='paid'
        )

        #ჯავშნის წარმატებულ გადახდას
        payment = get_object_or_404(
            Payment.objects.select_for_update(),
            rental=rental,
            status='successful'
        )

        # მიმდინარე კალენდარული თარიღი
        today = date.today()

        # დასრულებული ჯავშნის გაუქმება შეუძლებელია
        if rental.end_date < today:
            messages.error(
                request,
                'This rental has already ended and cannot be cancelled.'
            )
            return redirect('profile')

        # უკვე დაწყებული ჯავშნის გაუქმება შეუძლებელია
        if rental.start_date < today:
            messages.error(
                request,
                'This rental has already started and cannot be cancelled.'
            )
            return redirect('profile')

        # ვანგარიშობ, რამდენი კალენდარული დღეა დარჩენილი
        # გაქირავების დაწყებამდე
        days_before_start = (rental.start_date - today).days

        # ------------------------------
        # თანხის დაბრუნების პროცენტის განსაზღვრა
        # ------------------------------

        # 7 ან მეტი დღით ადრე გაუქმებისას ბრუნდება 100%
        if days_before_start >= 7:
            refund_percentage = Decimal('100')

        # 3-დან 6 დღემდე ადრე გაუქმებისას ბრუნდება 80%
        elif days_before_start >= 3:
            refund_percentage = Decimal('80')

        # 1-დან 2 დღემდე ადრე გაუქმებისას ბრუნდება 50%
        elif days_before_start >= 1:
            refund_percentage = Decimal('50')

        # დაწყების დღეს თანხა არ ბრუნდება
        else:
            refund_percentage = Decimal('0')

        # ------------------------------
        # დასაბრუნებელი თანხის გამოთვლა
        # ------------------------------

        # დასაბრუნებელი თანხა = გადახდილი თანხა × პროცენტი / 100
        #
        # quantize(Decimal('0.01')) ამრგვალებს თანხას
        refund_amount = (
            payment.amount * refund_percentage / Decimal('100')
        ).quantize(Decimal('0.01'))

        # გაუქმების საკომისიო არის თანხა,
        # რომელიც მომხმარებელს უკან არ უბრუნდება
        cancellation_fee = payment.amount - refund_amount

        # ვინახავთ თანხის დაბრუნების მონაცემებს
        payment.refund_amount = refund_amount
        payment.cancellation_fee = cancellation_fee

        # თუ თანხა ბრუნდება, ვნიშნავთ დაბრუნებას დამუშავებულად
        if refund_amount > 0:
            payment.refund_status = 'processed'
            payment.refunded_at = timezone.now()

        else:
            # თუ დასაბრუნებელი თანხა ნულის ტოლია,
            # თანხის დაბრუნება საჭირო არ არის
            payment.refund_status = 'not_applicable'
            payment.refunded_at = None

        # ვაახლებთ მხოლოდ შეცვლილ ველებს.
        # update_fields ამცირებს მონაცემთა ბაზაში შესანახი
        # ზედმეტი ცვლილებების რაოდენობას.
        payment.save(update_fields=[
            'refund_amount',
            'cancellation_fee',
            'refund_status',
            'refunded_at',
        ])

        # ჯავშნის სტატუსს ვცვლით cancelled მნიშვნელობით
        rental.status = 'cancelled'
        rental.cancelled_at = timezone.now()

        rental.save(update_fields=[
            'status',
            'cancelled_at',
        ])

    # ოპერაციის დასრულების შემდეგ ვაჩვენებთ დაბრუნებულ თანხასა
    # და გაუქმების საკომისიოს
    messages.success(
        request,
        (
            f'Booking cancelled. Simulated refund: '
            f'{refund_amount:.2f}. '
            f'Cancellation fee: {cancellation_fee:.2f}.'
        )
    )

    return redirect('profile')


# ==================================================
# REGISTRATION — მომხმარებლის რეგისტრაცია
# ==================================================

def register(request):
    """
    ახალი მომხმარებლის ანგარიშის შექმნა

    ფუნქცია იღებს მომხმარებლის პირად ინფორმაციას,
    ამოწმებს შეყვანილ მონაცემებს და ქმნის ახალ ანგარიშს
    """

    # რეგისტრაციის მონაცემებს ვამუშავებთ მხოლოდ POST მოთხოვნისას
    if request.method == 'POST':

        # ტელეფონის ნომერი გამოიყენება მომხმარებლის username-ად
        # ვამოწმებთ ორივე შესაძლო ველის სახელს,
        # რათა ფორმის სხვადასხვა ვერსიასთან თავსებადობა შენარჩუნდეს
        phone_number = request.POST.get(
            'phoneNumber',
            request.POST.get('username', '')
        ).strip()

        password = request.POST.get('password', '')
        email = request.POST.get('email', '').strip()

        # მომხმარებლის სახელი და გვარი
        first_name = request.POST.get(
            'firstName',
            request.POST.get('first_name', '')
        ).strip()

        last_name = request.POST.get(
            'lastName',
            request.POST.get('last_name', '')
        ).strip()

        # პაროლის დადასტურება
        confirm_password = request.POST.get(
            'confirmPassword',
            request.POST.get('confirm_password', '')
        )

        # მოწმდება აუცილებელ ველებს
        # all() აბრუნებს True-ს მხოლოდ მაშინ,
        # როდესაც ჩამონათვალის ყველა მნიშვნელობა შევსებულია
        if not all([
            phone_number,
            password,
            first_name,
            last_name
        ]):
            return render(request, 'cars/register.html', {
                'message': 'Please fill in all required fields.'
            })

        # თუ პაროლის დადასტურების ველი შევსებულია,
        # ვამოწმებთ ემთხვევა თუ არა პაროლები ერთმანეთს
        if confirm_password and password != confirm_password:
            return render(request, 'cars/register.html', {
                'message': 'Passwords do not match.'
            })

        # მოწმდება, ხომ არ არსებობს უკვე მომხმარებელი
        # იგივე ტელეფონის ნომრით
        if User.objects.filter(username=phone_number).exists():
            return render(request, 'cars/register.html', {
                'message': 'An account with this phone number already exists.'
            })

        # ელფოსტაც უნიკალური უნდა იყოს
        if email and User.objects.filter(email=email).exists():
            return render(request, 'cars/register.html', {
                'message': 'An account with this email already exists.'
            })

        # create_user() ქმნის ახალ მომხმარებელს
        # პაროლი ავტომატურად ინახება დაშიფრული ფორმით
        # ჩვეულებრივი create() მეთოდის გამოყენების შემთხვევაში
        # პაროლი უსაფრთხოდ არ დამუშავდებოდა
        User.objects.create_user(
            username=phone_number,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        # წარმატებული რეგისტრაციის შეტყობინება
        messages.success(
            request,
            'Registration successful. You can now log in.'
        )

        # რეგისტრაციის შემდეგ მომხმარებელი გადადის ავტორიზაციის გვერდზე
        return redirect('login')

    # GET მოთხოვნისას ვაჩვენებთ რეგისტრაციის ფორმას
    return render(request, 'cars/register.html')


# ==================================================
# LOGIN — მომხმარებლის ავტორიზაცია
# ==================================================

def login(request):
    """
    მომხმარებელი უთითებს ტელეფონის ნომერსა და პაროლს
    """

    # თუ მომხმარებელი უკვე ავტორიზებულია,
    # მას აღარ ვაჩვენებთ შესვლის ფორმას
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        # მომხმარებლის ტელეფონის ნომრის მიღება
        phone_number = request.POST.get(
            'phoneNumber',
            request.POST.get('username', '')
        ).strip()

        password = request.POST.get('password', '')

        # authenticate() ამოწმებს მომხმარებლის მონაცემებს
        # სწორი მონაცემების შემთხვევაში აბრუნებს User ობიექტს
        user = authenticate(
            request,
            username=phone_number,
            password=password
        )

        if user is not None:

            # auth_login() ქმნის ავტორიზებულ სესიას
            auth_login(request, user)

            # მომხმარებლის დამატებით ინფორმაციას ვინახავთ სესიაში.
            # სესია საშუალებას გვაძლევს მომხმარებლის მონაცემები
            # შევინარჩუნოთ გვერდებს შორის გადასვლისას
            request.session['user'] = get_user_data(user)

            return redirect('home')

        # არასწორი ტელეფონის ნომრის ან პაროლის შემთხვევაში
        # ვაჩვენებთ შესაბამის შეტყობინებას
        return render(request, 'cars/login.html', {
            'message': 'Invalid phone number or password.'
        })

    # GET მოთხოვნისას ვაჩვენებთ ავტორიზაციის ფორმას
    return render(request, 'cars/login.html')


# ==================================================
# LOGOUT — სისტემიდან გამოსვლა
# ==================================================

def logout(request):
    """
    auth_logout() ასრულებს django-ს ავტორიზებული სესიის გაუქმებას
    დამატებით იშლება შექმნილი user სესიის მონაცემს
    """

    # მომხმარებლის ავტორიზაციის დასრულება
    auth_logout(request)

    # სესიიდან მომხმარებლის დამატებითი მონაცემების წაშლა
    request.session.pop('user', None)

    # გამოსვლის შემდეგ მომხმარებელი მთავარ გვერდზე გადადის
    return redirect('home')


# ==================================================
# USER PROFILE — მომხმარებლის პროფილი
# ==================================================

@login_required
def profile(request):
    """
    პროფილში ნაჩვენებია:
    1. მომხმარებლის პირადი ინფორმაცი
    2. მის მიერ დამატებული ავტომობილები
    3. რჩეული ავტომობილები
    4. მომხმარებლის მიერ განხორციელებული გაქირავებები
    5. სხვა მომხმარებლების მიერ მის ავტომობილებზე შექმნილი ჯავშნები
    """

    # მომხმარებლის ძირითადი მონაცემები

    user_data = get_user_data(request.user)

    # ------------------------------
    # მომხმარებლის ავტომობილები
    # ------------------------------

    # ვიღებთ მხოლოდ მიმდინარე მომხმარებლის მიერ დამატებულ
    # აქტიურ ავტომობილებს
    user_cars = (
        Car.objects
        .filter(owner=request.user, is_active=True)
        .select_related('owner')

        # პირველ რიგში გამოჩნდება უახლესი განცხადებები
        .order_by('-created_at')
    )

    # ------------------------------
    # რჩეული ავტომობილები
    # ------------------------------

    # ვიღებთ მიმდინარე მომხმარებლის რჩეულ ავტომობილებს
    # წაშლილი ან არააქტიური განცხადებები არ გამოჩნდება
    favorite_objects = (
        Favorite.objects
        .filter(user=request.user, car__is_active=True)
        .select_related('car', 'car__owner')
    )

    # თითოეული რჩეული ჩანაწერიდან ვიღებთ ავტომობილსა
    # და შესაბამის Favorite ობიექტს
    favorites = [
        {'car': favorite.car, 'favorite': favorite}
        for favorite in favorite_objects
    ]

    # ------------------------------
    # მომხმარებლის მიერ გაკეთებული ჯავშნები
    # ------------------------------

    # ვიღებთ ყველა გაქირავების მოთხოვნას,
    # სადაც მიმდინარე მომხმარებელი არის დამქირავებელი
    rental_objects = (
        RentalRequest.objects
        .filter(renter=request.user)

        # წინასწარ ვიღებთ დაკავშირებულ ავტომობილს,
        # მის მფლობელსა და გადახდის ინფორმაციას
        .select_related('car', 'car__owner', 'payment')

        # უახლესი ჯავშნები პირველ რიგში
        .order_by('-created_at')
    )

    # თითოეული ჯავშნის ინფორმაციას ლექსიკონის სახით მზადდება
    rentals = [
        {
            'car': rental.car,
            'rental': rental,
            'start_date': rental.start_date,
            'end_date': rental.end_date,
            'total_days': rental.total_days,
            'total_price': rental.total_price,
            'status': rental.status,

            # getattr() ცდილობს მიიღოს დაკავშირებული Payment ობიექტი
            # თუ გადახდის ჩანაწერი არ არსებობს, აბრუნებს None
            'payment': getattr(rental, 'payment', None),
        }
        for rental in rental_objects
    ]

    # ------------------------------
    # შემომავალი ჯავშნები
    # ------------------------------

    # ვიღებ იმ ჯავშნებს, რომლებიც მომხმარებლის საკუთრებაში
    # არსებულ ავტომობილებზე სხვა მომხმარებლებმა გააკეთეს
    incoming_rental_objects = (
        RentalRequest.objects
        .filter(car__owner=request.user)

        # წინასწარ ვიღებ ავტომობილის, მფლობელისა და დამქირავებლის მონაცემებს
        .select_related('car', 'car__owner', 'renter')

        .order_by('-created_at')
    )

    # ვამზადებ შემომავალი ჯავშნების ინფორმაციას
    incoming_rentals = [
        {
            'car': rental.car,
            'rental': rental,

            # დამქირავებლის სრული სახელი
            'renter_name': rental.renter.get_full_name(),

            # დამქირავებლის ტელეფონის ნომერი
            'renter_phone': rental.renter.username,
        }
        for rental in incoming_rental_objects
    ]

    # ყველა მიღებული ინფორმაცია გადაეცემა პროფილის HTML შაბლონს
    return render(request, 'cars/profile.html', {
        'user': user_data,
        'cars': user_cars,
        'favorites': favorites,
        'rentals': rentals,
        'incoming_rentals': incoming_rentals,
    })


# ==================================================
# ADD CAR — ახალი ავტომობილის დამატება
# ==================================================

@login_required
def add_car_view(request):
    """

    მხოლოდ ავტორიზებულ მომხმარებელს შეუძლია ავტომობილის დამატება
    ფუნქცია ამოწმებს ტექსტურ მონაცემებს, რიცხვით მნიშვნელობებსა
    და ატვირთული ფოტოების ფორმატებს
    """

    if request.method == 'POST':

        # ატვირთული სურათები ინახება request.FILES-ში
        # request.POST გამოიყენება ჩვეულებრივი ფორმის მონაცემებისთვის,
        # ხოლო request.FILES — ფაილებისთვის
        image1 = request.FILES.get('Image1')
        image2 = request.FILES.get('Image2')
        image3 = request.FILES.get('Image3')

        # სამივე სურათს ერთ სიაში ვათავსებ,
        # რათა მათი შემოწმება ციკლით შევძლო
        images = [image1, image2, image3]

        # ------------------------------
        # ფოტოების ფორმატის შემოწმება
        # ------------------------------

        for image in images:

            # ვამოწმებ, რომ ატვირთული ფაილი იყოს PNG, JPG ან JPEG.
            # lower() ფაილის გაფართოებას პატარა ასოებად გარდაქმნის
            if image and not image.name.lower().endswith(
                ('.png', '.jpg', '.jpeg')
            ):
                messages.error(
                    request,
                    'Photos must be PNG, JPG or JPEG files.'
                )

                return redirect('add_car')

        # ------------------------------
        # ტექსტური მონაცემების მიღება
        # ------------------------------

        brand = request.POST.get('brand', '').strip()
        model = request.POST.get('model', '').strip()
        city = request.POST.get('city', '').strip()
        transmission = request.POST.get('transmission', '').strip()

        # ------------------------------
        # რიცხვითი მონაცემების მიღება და შემოწმება
        # ------------------------------

        try:
            year = int(request.POST.get('year'))

            # Decimal გამოიყენება ფასის ზუსტი გამოთვლებისთვის
            price = Decimal(request.POST.get('price'))

            capacity = int(request.POST.get('capacity'))
            fuel_capacity = int(request.POST.get('fuelCapacity'))

            # ავტომობილის გამოშვების წელი უნდა იყოს
            # 1900 წელსა და მიმდინარე წელს შორის
            if not 1900 <= year <= date.today().year:
                raise ValueError

            # ფასი, ადგილების რაოდენობა და საწვავის ავზის მოცულობა
            # დადებითი მნიშვნელობები უნდა იყოს
            if price <= 0 or capacity < 1 or fuel_capacity < 1:
                raise ValueError

        # თუ მონაცემების გარდაქმნა ან შემოწმება ვერ მოხერხდა,
        # მომხმარებელს ვუბრუნებთ შეცდომის შეტყობინებას
        except (TypeError, ValueError, InvalidOperation):
            messages.error(
                request,
                'Please check the year, price, seat count and fuel capacity.'
            )

            return redirect('add_car')

        # ვამოწმებთ, რომ აუცილებელი ტექსტური ველები შევსებული იყოს
        if not all([brand, model, city, transmission]):
            messages.error(
                request,
                'Please fill in all car details.'
            )

            return redirect('add_car')

        # ------------------------------
        # ავტომობილის მონაცემთა ბაზაში შენახვა
        # ------------------------------

        # Car.objects.create() ქმნის ახალ ავტომობილის ჩანაწერს
        # owner=request.user ავტომობილს აკავშირებს იმ მომხმარებელთან,
        # რომელიც ამ მომენტში სისტემაშია ავტორიზებული
        Car.objects.create(
            owner=request.user,
            brand=brand,
            model=model,
            year=year,
            price=price,
            capacity=capacity,
            transmission=transmission,
            city=city,
            fuel_capacity=fuel_capacity,

            # ტელეფონის ნომრად გამოიყენება მომხმარებლის username
            phone_number=request.user.username,

            # ავტომობილის ფოტოები ინახება შესაბამის ველებში
            image1=image1,
            image2=image2,
            image3=image3,
        )

        messages.success(request, 'Car added successfully.')

        # წარმატებული დამატების შემდეგ მომხმარებელი პროფილზე გადადის
        return redirect('profile')

    # GET მოთხოვნისას ვაჩვენებთ ავტომობილის დამატების ფორმას
    return render(request, 'cars/add_car.html')


# ==================================================
# EDIT CAR — ავტომობილის განცხადების რედაქტირება
# ==================================================

@login_required
def edit_car(request, car_id):
    """
    უკვე არსებული ავტომობილის განცხადების რედაქტირება

    მომხმარებელს შეუძლია მხოლოდ საკუთარი ავტომობილის შეცვლა
    სხვა მომხმარებლის ავტომობილის რედაქტირება დაუშვებელია
    """

    # ვეძებთ კონკრეტულ აქტიურ ავტომობილს
    #
    # owner=request.user უზრუნველყოფს საკუთრების შემოწმებას
    # თუ ავტომობილი სხვა მომხმარებელს ეკუთვნის ან არააქტიურია,
    car = get_object_or_404(
        Car,
        id=car_id,
        owner=request.user,
        is_active=True
    )

    if request.method == 'POST':

        # ვიღებთ ფორმიდან მიღებულ ტექსტურ მონაცემებს
        brand = request.POST.get('brand', '').strip()
        model = request.POST.get('model', '').strip()
        city = request.POST.get('city', '').strip()
        transmission = request.POST.get('transmission', '').strip()

        # ------------------------------
        # რიცხვითი მონაცემების შემოწმება
        # ------------------------------

        try:
            year = int(request.POST.get('year'))
            price = Decimal(request.POST.get('price'))
            capacity = int(request.POST.get('capacity'))
            fuel_capacity = int(request.POST.get('fuelCapacity'))

            # იგივე პირობები მოქმედებს, რაც ავტომობილის დამატებისას
            if not 1900 <= year <= date.today().year:
                raise ValueError

            if price <= 0 or capacity < 1 or fuel_capacity < 1:
                raise ValueError

        except (TypeError, ValueError, InvalidOperation):
            messages.error(request, 'Please check the car details.')

            return redirect('edit_car', car_id=car.id)

        # აუცილებელი ტექსტური ველების შემოწმება
        if not all([brand, model, city, transmission]):
            messages.error(request, 'Please fill in all required fields.')

            return redirect('edit_car', car_id=car.id)

        # ------------------------------
        # ახალი ფოტოების მიღება
        # ------------------------------

        # ლექსიკონი გამოიყენება მხოლოდ იმ ფოტოების შესანახად,
        # რომლებიც მომხმარებელმა ახლიდან ატვირთა
        uploaded_images = {}

        # ვამოწმებთ ავტომობილის სამივე ფოტოს ველს.
        for field_name in ['image1', 'image2', 'image3']:

            image = request.FILES.get(field_name)

            # თუ ახალი ფოტო არ არის ატვირთული,
            # ძველი ფოტო უცვლელი დარჩება
            if image:

                # ახალი ფოტოს გაფართოების შემოწმება
                if not image.name.lower().endswith(
                    ('.png', '.jpg', '.jpeg')
                ):
                    messages.error(
                        request,
                        'Photos must be PNG, JPG or JPEG files.'
                    )

                    return redirect('edit_car', car_id=car.id)

                # ვინახავთ ახალ ფოტოს შესაბამისი ველის სახელით
                uploaded_images[field_name] = image

        # ------------------------------
        # ავტომობილის მონაცემების განახლება
        # ------------------------------

        # Django მოდელის ობიექტის ატრიბუტებს ვანიჭებთ ახალ მნიშვნელობებს.
        car.brand = brand
        car.model = model
        car.year = year
        car.price = price
        car.capacity = capacity
        car.transmission = transmission
        car.city = city
        car.fuel_capacity = fuel_capacity

        # setattr() დინამიკურად ცვლის ობიექტის ატრიბუტს
        # მაგალითად:
        # setattr(car, 'image1', image)
        # იგივეა, რაც:
        # car.image1 = image
        #
        # ეს მაძლევს საშუალებას სამივე ფოტოს ველი
        # ერთი ციკლით განვაახლო
        for field_name, image in uploaded_images.items():
            setattr(car, field_name, image)

        # save() ინახავს ყველა ცვლილებას მონაცემთა ბაზაში.
        car.save()

        messages.success(request, 'Your car listing has been updated.')

        return redirect('profile')

    # GET მოთხოვნისას მომხმარებელს ვაჩვენებ რედაქტირების ფორმას
    # შაბლონს ასევე გადავცემ ქალაქების ჩამონათვალს
    return render(request, 'cars/edit_car.html', {
        'car': car,
        'cities': CITIES,
    })


# ==================================================
# DELETE CAR — ავტომობილის განცხადების წაშლა
# ==================================================

@login_required
@require_POST
def delete_car(request, car_id):
    """
    ავტომობილის განცხადების წაშლა Soft Delete მეთოდით

    ჩანაწერი მონაცემთა ბაზიდან
    ფიზიკურად არ იშლება

    ამის ნაცვლად is_active ველის მნიშვნელობა იცვლება False-ით.
    შედეგად განცხადება საიტზე აღარ ჩანს, მაგრამ მისი ისტორია ინახება
    """

    # ვიღებთ მხოლოდ იმ აქტიურ ავტომობილს,
    # რომელიც მიმდინარე მომხმარებელს ეკუთვნის
    car = get_object_or_404(
        Car,
        id=car_id,
        owner=request.user,
        is_active=True
    )

    # ------------------------------
    # აქტიური ჯავშნების შემოწმება
    # ------------------------------

    # ვამოწმებ, აქვს თუ არა ავტომობილს ისეთი გადახდილი ჯავშანი,
    # რომლის დასრულების თარიღიც დღევანდელი დღე ან მომავალია
    #
    # end_date__gte=date.today() ნიშნავს:
    # ჯავშანი ჯერ არ დასრულებულა.
    #
    # exists() აბრუნებს True-ს, თუ ასეთი ჯავშანი არსებობს.
    active_bookings = RentalRequest.objects.filter(
        car=car,
        status='paid',
        end_date__gte=date.today()
    ).exists()

    # თუ ავტომობილს აქვს მომავალი ან მიმდინარე ჯავშანი,
    # მისი განცხადების წაშლა დაუშვებელია.
    if active_bookings:
        messages.error(
            request,
            'This car cannot be removed because it has an upcoming or ongoing booking.'
        )

        return redirect('profile')

    # ------------------------------
    # Soft Delete — რბილი წაშლა
    # ------------------------------

    # ავტომობილს ვანიჭებ არააქტიურ სტატუსს
    # მონაცემთა ბაზის ჩანაწერი და მასთან დაკავშირებული ისტორია რჩება.
    car.is_active = False

    # ვინახავთ მხოლოდ is_active ველის ცვლილებას
    car.save(update_fields=['is_active'])

    messages.success(
        request,
        'Your car listing has been removed. Its rental history has been preserved.'
    )

    # მომხმარებელი ბრუნდება პროფილზე
    return redirect('profile')


