from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    SUBJECT_CHOICES = [
        ("feature_request", "Feature Request"),
        ("account_support", "Account Support"),
        ("partnership_inquiry", "Partnership Inquiry"),
        ("data_accuracy_issue", "Data Accuracy Issue"),
        ("user_experience_feedback", "User Experience Feedback"),
        ("others", "Others"),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.TextField()
    price = models.TextField()
    ratings = models.TextField()
    no_of_ratings = models.TextField()
    link = models.URLField(max_length=2000)
    image = models.ImageField(upload_to="set_images/", max_length=1000)
    brand = models.CharField(max_length=255, blank=True, null=True)
    budget = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    source = models.TextField(default="NULL")

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.TextField()
    price = models.TextField()
    ratings = models.TextField()
    no_of_ratings = models.TextField()
    link = models.URLField(max_length=2000)
    image = models.ImageField(upload_to="product_images/", max_length=1000)
    brand = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        null=True,
        blank=True,
        default="profile_photos/profile_photo.png",
    )


class RecentSearch(models.Model):
    productName = models.TextField()
