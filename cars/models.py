
# settings-დან ვიღებ django-ს პროექტის ძირითად პარამეტრებს
# ამ შემთხვევაში გვჭირდება AUTH_USER_MODEL, რათა მომხმარებლის მოდელთან
# კავშირი პირდაპირ User კლასის მითითების გარეშე დამყარდეს
from django.conf import settings


from django.db import models


# ============================================================
# ავტომობილის მოდელი
# ============================================================

class Car(models.Model):

    # ავტომობილის მფლობელი
    # ForeignKey ქმნის კავშირს მომხმარებელსა და ავტომობილს შორის
    # ერთი მომხმარებელი შეიძლება ფლობდეს რამდენიმე ავტომობილს,
    # მაგრამ თითოეულ ავტომობილს მხოლოდ ერთი მფლობელი ჰყავს

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        # თუ მომხმარებელი წაიშლება, მასთან დაკავშირებული
        # ავტომობილებიც ავტომატურად წაიშლება მონაცემთა ბაზიდან
        on_delete=models.CASCADE,

        # მომხმარებლის ობიექტიდან მის ავტომობილებზე წვდომა
        # შესაძლებელია owner.cars.all() ფორმით
        related_name="cars",
    )

    # ავტომობილის მარკა. მაგსლითად: BMW, Merceds
    # CharField გამოიყენება ტექსტური მონაცემების შესანახად
    # max_length განსაზღვრავს ტექსტის მაქსიმალურ სიგრძეს
    brand = models.CharField(max_length=100)

    # ავტომობილის მოდელი. მაგალითდ: C-Class, Prius
    model = models.CharField(max_length=100)

    # გამოშვების წელი.
    # PositiveIntegerField ინახავს მხოლოდ არაუარყოფით მთელ რიცხვებს
    year = models.PositiveIntegerField()

    # ავტომობილის გაქირავების ფასი
    # DecimalField გამოიყენება ათწილადი რიცხვების ზუსტად შესანახად
    # max_digits=10 ნიშნავს, რომ რიცხვში მაქსიმუმ 10 ციფრი შეიძლება იყოს
    # decimal_places=2 ნიშნავს, რომ მძიმის შემდეგ 2 ციფრი ინახება
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # ავტომობილში მგზავრების მაქსიმალური რაოდენობა
    capacity = models.PositiveIntegerField()

    # გადაცემათა კოლოფის ტიპი
    transmission = models.CharField(max_length=50)

    # ქალაქი, სადაც ავტომობილი მდებარეობს
    city = models.CharField(max_length=100)

    # საწვავის ავზის მოცულობა
    fuel_capacity = models.PositiveIntegerField()

    # ავტომობილის მფლობელის საკონტაქტო ტელეფონის ნომერი
    # CharField გამოიყენება და არა IntegerField, რადგან
    # ტელეფონის ნომერი შეიძლება შეიცავდეს + ნიშანს
    phone_number = models.CharField(max_length=30)

    # ავტომობილის პირველი ფოტო
    # ImageField გამოიყენება სურათების ასატვირთად და შესანახად
    # upload_to="cars/" ნიშნავს, რომ ფაილი მედია ფაილების
    # შესაბამის cars/ საქაღალდეში შეინახება
    # blank=True ნიშნავს, რომ ველი შეიძლება ცარიელი დარჩეს ფორმაში
    # null=True ნიშნავს, რომ მონაცემთა ბაზაში შეიძლება NULL მნიშვნელობა ჰქონდეს
    image1 = models.ImageField(
        upload_to="cars/", blank=True, null=True
    )

    # ავტომობილის მეორე ფოტო
    # ფოტოს ატვირთვა სავალდებულო არ არის
    image2 = models.ImageField(
        upload_to="cars/", blank=True, null=True
    )

    # ავტომობილის მესამე ფოტო
    # ასევე არასავალდებულო ველი
    image3 = models.ImageField(
        upload_to="cars/", blank=True, null=True
    )

    # განსაზღვრავს, აქტიურია თუ არა ავტომობილის განცხადება
    # BooleanField ინახავს მხოლოდ ორ მნიშვნელობას: True ან False
    # default=True ნიშნავს, რომ ახალი ავტომობილი აქტიური იქნება,
    # თუ სხვა მნიშვნელობა სპეციალურად არ მიეთითა
    is_active = models.BooleanField(default=True)

    # ავტომობილის განცხადების შექმნის თარიღი და დრო
    # auto_now_add=True ნიშნავს, რომ ეს მნიშვნელობა ავტომატურად
    # განისაზღვრება ობიექტის პირველად შექმნის მომენტში
    created_at = models.DateTimeField(auto_now_add=True)

    # __str__ არის სპეციალური მეთოდი, რომელიც განსაზღვრავს,
    # როგორ გამოჩნდება ავტომობილის ობიექტი ტექსტური ფორმით
    # მაგალითად,
    # BMW X5 (2022), ნაცვლად უბრალოდ Car object (1)-ისა
    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


# ============================================
# რჩეული ავტომობილების მოდელი
# ============================================

class Favorite(models.Model):

    # მომხმარებელი, რომელმაც ავტომობილი რჩეულებში დაამატა
    # ერთი მომხმარებელი შეიძლება რამდენიმე ავტომობილს ამატებდეს რჩეულებში
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        # მომხმარებლის წაშლის შემთხვევაში მისი რჩეულების ჩანაწერებიც იშლება
        on_delete=models.CASCADE,

        # მომხმარებლის რჩეულებზე წვდომა შესაძლებელია:
        # user.favorites.all() ფორმით
        related_name="favorites",
    )

    # ავტომობილი, რომელიც მომხმარებელმა რჩეულებში დაამატა
    # ერთი ავტომობილი შეიძლება რამდენიმე სხვადასხვა მომხმარებლის
    # რჩეულებში იყოს დამატებული
    car = models.ForeignKey(
        Car,

        # თუ ავტომობილი წაიშლება, მასთან დაკავშირებული
        # რჩეულების ჩანაწერებიც ავტომატურად წაიშლება
        on_delete=models.CASCADE,

        # ავტომობილის ყველა მომხმარებლის პოვნა შესაძლებელია:
        # car.favorited_by.all() ფორმით
        related_name="favorited_by",
    )

    # Meta კლასი გამოიყენება მოდელის დამატებითი პარამეტრების განსაზღვრისთვის
    class Meta:

        # UniqueConstraint ქმნის უნიკალურობის შეზღუდვას
        # ერთი და იგივე მომხმარებელი ერთსა და იმავე ავტომობილს
        # რჩეულებში მხოლოდ ერთხელ დაამატებს
        # ამით თავიდან ვიცილებთ მონაცემთა ბაზაში დუბლირებულ ჩანაწერებს
        constraints = [
            models.UniqueConstraint(
                fields=["user", "car"],
                name="unique_user_car_favorite",
            )
        ]

    # რჩეულის ჩანაწერის ტექსტური წარმოდგენა
    # მაგალითად: user@example.com - BMW X5 (2022)
    def __str__(self):
        return f"{self.user} - {self.car}"


# ============================================================
# RENTAL REQUEST MODEL
# ავტომობილის დაქირავების მოთხოვნის მოდელი
# ============================================================

class RentalRequest(models.Model):

    # დაქირავების მოთხოვნის შესაძლო სტატუსები
    # პირველი მნიშვნელობა ინახება მონაცემთა ბაზაში,
    # ხოლო მეორე მნიშვნელობა გამოიყენება მომხმარებლისთვის საჩვენებლად
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    # მომხმარებელი, რომელიც ავტომობილის დაქირავებას ითხოვს
    # ერთი მომხმარებელი შეიძლება რამდენიმე დაქირავების მოთხოვნას ქმნიდეს
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        # მომხმარებლის წაშლის შემთხვევაში მისი დაქირავების
        # მოთხოვნებიც წაიშლება
        on_delete=models.CASCADE,

        # მომხმარებლის ყველა დაქირავების მოთხოვნაზე წვდომა:
        # user.rental_requests.all()
        related_name="rental_requests",
    )

    # ავტომობილი, რომლის დაქირავებაც მომხმარებელს სურს
    # ერთ ავტომობილზე შეიძლება რამდენიმე მოთხოვნა არსებობდეს
    car = models.ForeignKey(
        Car,

        # ავტომობილის წაშლის შემთხვევაში მასთან დაკავშირებული
        # დაქირავების მოთხოვნებიც წაიშლება
        on_delete=models.CASCADE,

        # კონკრეტული ავტომობილის დაქირავების მოთხოვნები:
        # car.rental_requests.all()
        related_name="rental_requests",
    )

    # ქირაობის დაწყების თარიღი.
    # DateField ინახავს მხოლოდ თარიღს და არა საათსა და წუთს
    start_date = models.DateField()

    # ქირაობის დასრულების თარიღი
    end_date = models.DateField()

    # ქირაობის საერთო ხანგრძლივობა დღეებში
    # PositiveIntegerField ინახავს არაუარყოფით მთელ რიცხვს
    total_days = models.PositiveIntegerField()

    # ქირაობის სრული ღირებულება
    # გამოიყენება ათწილადი რიცხვების შესანახად,
    # ორი ციფრით მძიმის შემდეგ
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    # დაქირავების მოთხოვნის მიმდინარე სტატუსი.
    status = models.CharField(
        # სტატუსის ტექსტის მაქსიმალური სიგრძე
        max_length=20,

        # choices ზღუდავს ველის შესაძლო მნიშვნელობებს
        # ზემოთ განსაზღვრული STATUS_CHOICES სიით
        choices=STATUS_CHOICES,

       
        default="pending",
    )

    # მოთხოვნის შექმნის თარიღი და დრო
    # მნიშვნელობა ავტომატურად ენიჭება ჩანაწერის შექმნისას
    created_at = models.DateTimeField(auto_now_add=True)

    # მოთხოვნის გაუქმების თარიღი და დრო
    # null=True ნიშნავს, რომ მონაცემთა ბაზაში შეიძლება NULL იყოს
    # blank=True ნიშნავს, რომ ფორმაში შევსება სავალდებულო არ არის
    # ეს ველი ივსება მხოლოდ მაშინ, როდესაც მოთხოვნა უქმდება
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # დაქირავების მოთხოვნის ტექსტური წარმოდგენა
    # მაგალითად: user@example.com - BMW X5 (2022) (pending).
    def __str__(self):
        return f"{self.renter} - {self.car} ({self.status})"


# ============================================================
# გადახდის მოდელი
# ============================================================

class Payment(models.Model):

    # გადახდის შესაძლო სტატუსები
    STATUS_CHOICES = [
        ("pending", "Pending"),

        # გადახდა წარმატებით განხორციელდა
        ("successful", "Successful"),

        # გადახდა წარუმატებლად დასრულდა
        ("failed", "Failed"),
    ]

    # თანხის დაბრუნების შესაძლო სტატუსები
    REFUND_STATUS_CHOICES = [
        # თანხის დაბრუნება არ გამოიყენება
        ("not_applicable", "Not applicable"),

        # თანხის დაბრუნების პროცესი დასრულებულია
        ("processed", "Processed"),
    ]

    # გადახდა დაკავშირებულია კონკრეტულ დაქირავების მოთხოვნასთან
    # OneToOneField ქმნის ერთ-ერთთან კავშირს:
    # ერთ დაქირავების მოთხოვნას შეიძლება ჰქონდეს მხოლოდ ერთი გადახდის ჩანაწერი,
    # ხოლო ერთი გადახდის ჩანაწერი მხოლოდ ერთ მოთხოვნას ეკუთვნის
    rental = models.OneToOneField(
        RentalRequest,

        # თუ დაქირავების მოთხოვნა წაიშლება,
        # მასთან დაკავშირებული გადახდის ჩანაწერიც წაიშლება
        on_delete=models.CASCADE,

        # დაქირავების მოთხოვნიდან გადახდის ჩანაწერზე წვდომა:
        # rental.payment
        related_name="payment",
    )

    # გადასახდელი თანხა.
    # DecimalField უზრუნველყოფს ფულადი მნიშვნელობების ზუსტ შენახვას
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # გადახდის მიმდინარე სტატუსი
    status = models.CharField(
        max_length=20,

        # შესაძლო მნიშვნელობები შეზღუდულია STATUS_CHOICES სიით
        choices=STATUS_CHOICES,

        # ახალი გადახდის ჩანაწერის საწყისი სტატუსია pending
        default="pending",
    )

    # მომხმარებლისთვის დასაბრუნებელი თანხის ოდენობა
    # default=0 ნიშნავს, რომ თუ თანხის დაბრუნება არ მომხდარა,
    # საწყისი მნიშვნელობა ნულია
    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    # გაუქმების შემთხვევაში დაკისრებული საკომისიო ან ჯარიმა
    # საწყისი მნიშვნელობა ნულია
    cancellation_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    # თანხის დაბრუნების სტატუსი
    refund_status = models.CharField(
        max_length=20,

        # დასაშვები მნიშვნელობები განსაზღვრულია REFUND_STATUS_CHOICES-ში
        choices=REFUND_STATUS_CHOICES,

        # საწყისად თანხის დაბრუნება არ გამოიყენება
        default="not_applicable",
    )

    # გადახდის ჩანაწერის შექმნის თარიღი და დრო
    created_at = models.DateTimeField(auto_now_add=True)

    # წარმატებული გადახდის განხორციელების თარიღი და დრო
    # თავდაპირველად შეიძლება ცარიელი იყოს
    paid_at = models.DateTimeField(null=True, blank=True)

    # თანხის დაბრუნების დასრულების თარიღი და დრო
    # ივსება თანხის დაბრუნების პროცესის დასრულების შემდეგ
    refunded_at = models.DateTimeField(null=True, blank=True)

    # გადახდის ჩანაწერის ტექსტური წარმოდგენა
    # rental_id არის დაკავშირებული დაქირავების მოთხოვნის მონაცემთა ბაზის id
    def __str__(self):
        return f"Payment for rental #{self.rental_id}"
