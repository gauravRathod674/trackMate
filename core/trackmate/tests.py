from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail

from .views import *
from .models import Product
from bs4 import BeautifulSoup
import time
import requests
