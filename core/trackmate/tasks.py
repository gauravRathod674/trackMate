# tasks.py
from django.contrib.auth import get_user_model
from celery import shared_task
from core.celery import app
from .models import Product

from django.core.mail import send_mail
from bs4 import BeautifulSoup
import time
import requests
import re
import datetime
from celery.schedules import crontab


@shared_task
def scrape_amazon_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    # Set a reasonable timeout for the request
    timeout = 5  # You can adjust this based on your needs

    price = None

    # Keep trying to make the request until all information is successfully extracted or a timeout occurs
    while price is None:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Proceed with parsing the response
            soup = BeautifulSoup(response.text, "lxml")

            price_element = soup.find("span", class_="a-price-whole")
            if price_element:
                price = price_element.getText().strip()
                # print(f"Amazon Price found: {price}")

        except requests.exceptions.RequestException as e:
            time.sleep(0.000000000000000000000000000000000000001)

    return price


@shared_task
def scrape_flipkart_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    # Set a reasonable timeout for the request
    timeout = 5  # You can adjust this based on your needs

    price = None

    # Keep trying to make the request until all information is successfully extracted or a timeout occurs
    while price is None:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Proceed with parsing the response
            soup = BeautifulSoup(response.text, "lxml")

            price_element = soup.find("div", class_="_30jeq3 _16Jk6d")
            if price_element:
                price = price_element.getText().strip()
                # print(f"Flipkart Price found: {price}")

        except requests.exceptions.RequestException as e:
            time.sleep(0.000000000000000000000000000000000000001)

    return price


@shared_task
def scrape_skechers_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    # Set a reasonable timeout for the request
    timeout = 5  # You can adjust this based on your needs

    price = None

    # Keep trying to make the request until all information is successfully extracted or a timeout occurs
    while price is None:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Proceed with parsing the response
            soup = BeautifulSoup(response.text, "lxml")

            price_element = soup.find("span", class_="value p-heading hidden-lg-down")
            if price_element:
                price = price_element.getText().strip()
                # print(f"Skechers Price found: {price}")

        except requests.exceptions.RequestException as e:
            time.sleep(0.000000000000000000000000000000000000001)

    return price


@shared_task
def scrape_westside_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    # Set a reasonable timeout for the request
    timeout = 5  # You can adjust this based on your needs

    price = None

    # Keep trying to make the request until all information is successfully extracted or a timeout occurs
    while price is None:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Proceed with parsing the response
            soup = BeautifulSoup(response.text, "lxml")

            price_element = soup.find(
                "span", class_="price-item price-item--sale price-item--last"
            )
            if price_element:
                price = price_element.getText().strip()
                # print(f"Westside Price found: {price}")

        except requests.exceptions.RequestException as e:
            time.sleep(0.000000000000000000000000000000000000001)

    return price


@shared_task
def check_prices_and_notify():
    products = Product.objects.all()

    for product in products:
        # Use the corresponding scraping function based on the product's source
        if product.source == "AMAZON":
            current_price = scrape_amazon_price(product.link)
        elif product.source == "FLIPKART":
            current_price = scrape_flipkart_price(product.link)
        elif product.source == "WESTSIDE":
            current_price = scrape_westside_price(product.link)
        elif product.source == "SKECHERS":
            current_price = scrape_skechers_price(product.link)

        # Check if the scraping was successful
        if current_price:
            current_price_value = current_price

            # Convert the scraped price to a numeric value (you may need to adjust this based on your actual data)
            current_price_numeric = float(
                current_price_value.replace("₹", "").replace(",", "")
            )
            print(current_price_numeric)

            # Compare the current price with the stored budget
            if current_price_numeric <= product.budget:
                print("Inside If condition!")
                # Send email notification
                send_mail(
                    "Exciting News! The Price Drop You've Been Waiting For!",
                    f"""
Dear Customer,

We hope this message finds you well! We have some fantastic news to share with you - the price of the {product.name} has dropped, and it's now within your budget!

{product.name} : {current_price_numeric}
{product.link}

Now is the perfect time to make your purchase and take advantage of this amazing offer. Don't miss out on the opportunity to own {product.name} at an even more affordable price.

If you have any questions or need further assistance, feel free to reach out to our customer support team at [trackmate.official@gmai.com].

Thank you for choosing TrackMate! We appreciate your business and look forward to serving you.

Happy shopping!

Best regards,
TrackMate - Shope With Condidence
""",
                    "trackmate.official@gmail.com",
                    ["rathodgaurav753@gmail.com"],
                    fail_silently=False,
                )
    print("Done checking!")
