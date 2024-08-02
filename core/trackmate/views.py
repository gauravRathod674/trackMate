from django.shortcuts import render, redirect
from .models import *
import requests
import time
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .tasks import *
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import random
from concurrent.futures import ThreadPoolExecutor
import math
import threading
import concurrent.futures
import json
from datetime import datetime, timedelta


def scrape_flipkart_banner_info(container):
    base_url = "https://www.flipkart.com"

    # Find the 'a' tag within the 'div' and get the href attribute
    anchor_tag = container.find("a", class_="_3n8fnay4")
    if anchor_tag:
        href = anchor_tag.get("href", "")
        if not href.startswith("http"):
            href = base_url + href

        # Find the image tag and get the src or srcset attribute
        image_tag = anchor_tag.find("img", alt="Image")
        if image_tag:
            if "src" in image_tag.attrs:
                img_src = image_tag["src"]
            elif "srcset" in image_tag.attrs:
                img_src = image_tag["srcset"].split(",")[0].split()[0]
            else:
                img_src = "No src or srcset attribute found"

            return {
                "href": href,
                "img_src": img_src,
            }
    return None


def scrape_flipkart_banner():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    base_url = "https://www.flipkart.com"

    timeout = 5

    while True:
        try:
            response = requests.get(base_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException:
            time.sleep(0.1)  

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the containers
    containers = soup.find_all("div", class_="_8S67Ib")

    # List to store Flipkart product information
    flipkart_banner = []

    # Use multithreading to scrape product information concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(scrape_flipkart_banner_info, containers))

    # Append the results to the flipkart_banner list
    flipkart_banner.extend(result for result in results if result is not None)

    for i, info in enumerate(flipkart_banner, start=1):
        print(f"Item {i} - HREF: {info['href']}")
        print(f"Item {i} - Image Source: {info['img_src']}")
        print("\n-----------------\n")

    return flipkart_banner


def scrape_westside_banner_info(swiper_slide):
    base_url = "https://www.westside.com"

    # Find the 'a' tag within the 'div' and get the href attribute
    anchor_tag = swiper_slide.find("a")
    if anchor_tag:
        href = anchor_tag.get("href", "")
        # Ensure href is a valid URL
        if not href.startswith("http"):
            href = base_url + href

    # Find the 'img' tag within the 'div' and get the src attribute
    img_tag = swiper_slide.find("img", class_="banner__desktop")
    if img_tag:
        img_src_relative = img_tag.get("src", "")
        # Construct the absolute image source URL
        if not img_src_relative.startswith("http"):
            img_src = base_url + img_src_relative.split("www.westside.com")[-1]
        else:
            img_src = img_src_relative
    else:
        img_src = "Image source not found"

    return {
        "href": href,
        "img_src": img_src,
    }


def scrape_westside_banner():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    base_url = "https://www.westside.com"

    timeout = 5

    while True:
        try:
            response = requests.get(base_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException:
            time.sleep(0.1)  # Wait for 0.1 seconds before retrying

    soup = BeautifulSoup(response.text, "html.parser")

    # List to store Westside product information
    westside_banner = []

    # Find all div elements with class "swiper-slide"
    swiper_slides = soup.find_all("div", class_="swiper-slide")

    # Use multithreading to scrape product information concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(
            executor.map(
                lambda slide: scrape_westside_banner_info(slide),
                swiper_slides,
            )
        )

    # Append the results to the westside_banner list
    westside_banner.extend(results)

    for i, info in enumerate(westside_banner, start=1):
        print(f"Slide {i} - HREF: {info['href']}")
        print(f"Slide {i} - Image Source: {info['img_src']}")
        print("\n-----------------\n")

    return westside_banner


def scrape_skechers_banner_info(banner_div):
    base_url = "https://www.skechers.in"

    # Find the anchor tag inside each div
    anchor_tag = banner_div.find("a", class_="banner-event-tracking")

    if anchor_tag:
        # Extract href attribute
        href = anchor_tag.get("href", "")
        # Ensure href is a valid URL
        if not href.startswith("http"):
            href = base_url + href

        # Find the picture tag inside each anchor tag
        picture_tag = anchor_tag.find("picture")

        if picture_tag:
            # Find the source tag inside the picture tag
            source_tag = picture_tag.find("source")

            if source_tag:
                # Extract the srcset attribute
                srcset = source_tag.get("srcset", "")
                # Split the srcset attribute into different sources
                sources = srcset.split(", ")
                # Extract the first image link from sources
                first_image_link = (
                    sources[0].split(" ")[0]
                    if len(sources) > 0
                    else "Image source not found"
                )

                return {"href": href, "img_src": first_image_link}

    return None


def scrape_skechers_banner():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    url = "https://www.skechers.in/"

    timeout = 5

    while True:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException:
            time.sleep(0.1)  # Wait for 0.1 seconds before retrying

    soup = BeautifulSoup(response.text, "html.parser")

    banner_info = []

    # Find all div elements with class "experience-component experience-commerce_assets-imageBanner"
    banner_divs = soup.find_all(
        "div", class_="experience-component experience-commerce_assets-imageBanner"
    )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(scrape_skechers_banner_info, banner_divs))

    banner_info = [result for result in results if result is not None]

    for idx, info in enumerate(banner_info, start=1):
        print(f"Banner {idx}:")
        print("Href:", info["href"])
        print("Image Source:", info["img_src"])
        print("---")

    return banner_info


def scrape_all_platforms_banner():
    with ThreadPoolExecutor() as executor:
        # Create a list of futures for concurrent execution
        futures = [
            executor.submit(scrape_flipkart_banner),
            executor.submit(scrape_westside_banner),
            executor.submit(scrape_skechers_banner),
        ]

        # Wait for all futures to complete
        results = [future.result() for future in futures]

    # Combine the results from all platforms
    all_banners = sum(results, [])
    random.shuffle(all_banners)

    return all_banners


def banner(request):
    banners = scrape_all_platforms_banner()
    return render(request, "banner.html", {"banners": banners})


CACHE_EXPIRATION_DAYS = 1


def load_cache(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(cache_file, data):
    with open(cache_file, "w") as file:
        json.dump(data, file, indent=2)


def is_cache_valid(cache_timestamp, expiration_days):
    now = datetime.now()
    expiration_time = datetime.fromtimestamp(cache_timestamp) + timedelta(
        days=expiration_days
    )
    return now < expiration_time


def scrape_all_platforms_static():
    with ThreadPoolExecutor() as executor:
        # Create a list of futures for concurrent execution
        futures = [
            executor.submit(scrape_amazon, "mobiles"),
            executor.submit(scrape_amazon, "refrigerator"),
            executor.submit(scrape_flipkart, "camera"),
            executor.submit(scrape_flipkart, "iphone 15"),
            # executor.submit(scrape_hm, "tshirt"),
            # executor.submit(scrape_hm, "jacket"),
            executor.submit(scrape_westside, "jacket"),
            executor.submit(scrape_westside, "shirt"),
            executor.submit(scrape_skechers, "shoes"),
        ]

        # Wait for all futures to complete
        results = [future.result() for future in futures]

    # Combine the results from all platforms
    all_products = sum(results, [])
    random.shuffle(all_products)

    return all_products


def get_home_products_with_subcategories(
    request, subcategories, scrape_function, cache_file_prefix
):
    cached_data = load_cache(f"{cache_file_prefix}.json")

    if request.method == "POST":
        selected_sites = request.POST.getlist("site")
        if selected_sites:
            # Determine the cache file based on the selected site
            selected_site = selected_sites[0].lower()
            cache_file = f"{cache_file_prefix}_{selected_site}.json"
            cached_data = load_cache(cache_file)

            if "timestamp" in cached_data and is_cache_valid(
                cached_data["timestamp"], CACHE_EXPIRATION_DAYS
            ):
                products = cached_data["data"]
            else:
                # Fetch new data from selected site using the getCheckedSiteProducts function
                products = []
                for subcategory in subcategories:
                    products.extend(
                        getCheckedSiteProducts(f"{subcategory}", selected_sites)
                    )
                # Update cache with new data
                save_cache(
                    cache_file, {"timestamp": int(time.time()), "data": products}
                )
        else:
            # No specific site selected, use the default cache file
            products = []
            for subcategory in subcategories:
                products.extend(
                    getCheckedSiteProducts(f"{subcategory}", selected_sites)
                )
            # Update cache with new data
            save_cache(
                f"{cache_file_prefix}.json",
                {"timestamp": int(time.time()), "data": products},
            )
    else:
        if "timestamp" in cached_data and is_cache_valid(
            cached_data["timestamp"], CACHE_EXPIRATION_DAYS
        ):
            products = cached_data["data"]
        else:
            # Fetch new data from the scrape_function
            products = scrape_function()
            # Update cache with new data
            save_cache(
                f"{cache_file_prefix}.json",
                {"timestamp": int(time.time()), "data": products},
            )

    return products


def homepage(request):
    banners = scrape_all_platforms_banner()

    subcategories = [
        "Mobiles",
        "Refrigerator",
        "Camera",
        "iphone 15",
        "Jacket",
        "Shirt",
        "Shoes",
    ]
    return render(
        request,
        "homepage.html",
        {
            "products": get_home_products_with_subcategories(
                request, subcategories, scrape_all_platforms_static, "home"
            ), "banners": banners
        },
    )


def getCheckedSiteProducts(product_name, selected_sites):
    products = []
    threads = []

    def scrape_and_extend(scrape_function):
        site_products = scrape_function(product_name)
        products.extend(site_products)

    if "amazon" in selected_sites:
        thread = threading.Thread(target=scrape_and_extend, args=(scrape_amazon,))
        threads.append(thread)

    if "flipkart" in selected_sites:
        thread = threading.Thread(target=scrape_and_extend, args=(scrape_flipkart,))
        threads.append(thread)

    # if "H&M" in selected_sites:
    #     thread = threading.Thread(target=scrape_and_extend, args=(scrape_hm,))
    #     threads.append(thread)

    if "westside" in selected_sites:
        thread = threading.Thread(target=scrape_and_extend, args=(scrape_westside,))
        threads.append(thread)

    if "skechers" in selected_sites:
        thread = threading.Thread(target=scrape_and_extend, args=(scrape_skechers,))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    random.shuffle(products)

    return products


def get_products(request, category, scrape_function, cache_file_prefix):
    cached_data = load_cache(f"{cache_file_prefix}.json")

    if request.method == "POST":
        selected_sites = request.POST.getlist("site")
        if selected_sites:
            # Determine the cache file based on the selected site
            cache_file = f"{cache_file_prefix}_{selected_sites[0].lower()}.json"
            cached_data = load_cache(cache_file)

            if "timestamp" in cached_data and is_cache_valid(
                cached_data["timestamp"], CACHE_EXPIRATION_DAYS
            ):
                products = cached_data["data"]
            else:
                # Fetch new data from selected site using the getCheckedSiteProducts function
                products = getCheckedSiteProducts(category, selected_sites)
                # Update cache with new data
                save_cache(
                    cache_file, {"timestamp": int(time.time()), "data": products}
                )
        else:
            # No specific site selected, use the default cache file
            products = getCheckedSiteProducts(category, selected_sites)
            # Update cache with new data
            save_cache(
                f"{cache_file_prefix}.json",
                {"timestamp": int(time.time()), "data": products},
            )
    else:
        if "timestamp" in cached_data and is_cache_valid(
            cached_data["timestamp"], CACHE_EXPIRATION_DAYS
        ):
            products = cached_data["data"]
        else:
            # Fetch new data from Amazon using the provided scrape function
            products = scrape_function(category)
            # Update default cache with new data
            save_cache(
                f"{cache_file_prefix}.json",
                {"timestamp": int(time.time()), "data": products},
            )

    return products


def get_products_with_subcategories(
    request, category, subcategories, scrape_function, cache_file_prefix
):
    cached_data = load_cache(f"{cache_file_prefix}.json")

    if request.method == "POST":
        selected_sites = request.POST.getlist("site")
        if selected_sites:
            # Determine the cache file based on the selected site
            selected_site = selected_sites[0].lower()
            cache_file = f"{cache_file_prefix}_{selected_site}.json"
            cached_data = load_cache(cache_file)

            if "timestamp" in cached_data and is_cache_valid(
                cached_data["timestamp"], CACHE_EXPIRATION_DAYS
            ):
                products = cached_data["data"]
            else:
                # Fetch new data from selected site using the getCheckedSiteProducts function
                products = []
                for subcategory in subcategories:
                    products.extend(
                        getCheckedSiteProducts(
                            f"{category} {subcategory}", selected_sites
                        )
                    )
                # Update cache with new data
                save_cache(
                    cache_file, {"timestamp": int(time.time()), "data": products}
                )
        else:
            # No specific site selected, use the default cache file
            products = []
            for subcategory in subcategories:
                products.extend(
                    getCheckedSiteProducts(f"{category} {subcategory}", selected_sites)
                )
            # Update cache with new data
            save_cache(
                f"{cache_file_prefix}.json",
                {"timestamp": int(time.time()), "data": products},
            )
    else:
        if "timestamp" in cached_data and is_cache_valid(
            cached_data["timestamp"], CACHE_EXPIRATION_DAYS
        ):
            products = cached_data["data"]
        else:
            # Fetch new data from Amazon using the provided scrape function
            products = []
            for subcategory in subcategories:
                products.extend(scrape_function(f"{category} {subcategory}"))
            # Update default cache with new data
            save_cache(
                f"{cache_file_prefix}.json",
                {"timestamp": int(time.time()), "data": products},
            )

    return products


def mobile(request):
    return render(
        request,
        "mobile.html",
        {
            "products": get_products(
                request, "mobiles", scrape_amazon_flipkart, "mobile"
            )
        },
    )


def laptop(request):
    return render(
        request,
        "laptop.html",
        {
            "products": get_products(
                request, "laptop", scrape_amazon_flipkart_hm_skechers, "laptop"
            )
        },
    )


def scrape_audio(category):
    subcategories = ["Headphones", "Earphones", "Ear buds", "Neck band"]
    with ThreadPoolExecutor() as executor:
        # Create a list of futures for concurrent execution
        futures = [
            executor.submit(scrape_amazon, f"{category} {sub}") for sub in subcategories
        ]

        # Wait for all futures to complete
        results = [future.result() for future in futures]

    # Combine the results from all platforms
    all_products = sum(results, [])
    random.shuffle(all_products)

    return all_products


def audio(request):
    subcategories = ["Headphones", "Earphones", "Ear buds", "Neck band"]

    return render(
        request,
        "audio.html",
        {
            "products": get_products_with_subcategories(
                request, "Audio", subcategories, scrape_audio, "audio"
            )
        },
    )


def books(request):
    return render(
        request,
        "books.html",
        {"products": get_products(request, "Books", scrape_amazon, "books")},
    )


def petFood(request):
    return render(
        request,
        "dog_food.html",
        {
            "products": get_products(
                request, "Dog food", scrape_amazon_flipkart, "petFood"
            )
        },
    )


def scrape_watches(category):
    subcategories = [
        "Smart Watch",
        "Apple Watch",
        "Noise Watch",
        "Fireboltt Watch",
        "Boat Watch",
    ]
    with ThreadPoolExecutor() as executor:
        # Create a list of futures for concurrent execution
        futures = [
            executor.submit(scrape_amazon, f"{category} {sub}") for sub in subcategories
        ]

        # Wait for all futures to complete
        results = [future.result() for future in futures]

    # Combine the results from all platforms
    all_products = sum(results, [])
    random.shuffle(all_products)

    return all_products


def watches(request):
    subcategories = [
        "Smart Watch",
        "Apple Watch",
        "Noise Watch",
        "Fireboltt Watch",
        "Boat Watch",
    ]

    return render(
        request,
        "watches.html",
        {
            "products": get_products_with_subcategories(
                request, "Watches", subcategories, scrape_watches, "watches"
            )
        },
    )


def scrape_clothes(category):
    subcategories = ["Jeans", "T-shirt", "Shirt", "Jacket"]
    with ThreadPoolExecutor() as executor:
        # Create a list of futures for concurrent execution
        futures = [
            executor.submit(scrape_hm_westside_skechers, f"{category} {sub}")
            for sub in subcategories
        ]

        # Wait for all futures to complete
        results = [future.result() for future in futures]

    # Combine the results from all platforms
    all_products = sum(results, [])
    random.shuffle(all_products)

    return all_products


def clothes(request):
    subcategories = ["Jeans", "T-shirt", "Shirt", "Jacket"]
    return render(
        request,
        "clothes.html",
        {
            "products": get_products_with_subcategories(
                request, "Clothes", subcategories, scrape_clothes, "clothes"
            )
        },
    )


def camera(request):
    return render(
        request,
        "camera.html",
        {"products": get_products(request, "Camera", scrape_amazon_flipkart, "camera")},
    )


def footwear(request):
    return render(
        request,
        "footwear.html",
        {
            "products": get_products(
                request, "Shoes", scrape_hm_westside_skechers, "footwear"
            )
        },
    )


def contact(request):
    if request.method == "POST":
        data = request.POST
        subject = data.get("subject")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        message = data.get("message")

        Contact.objects.create(
            subject=subject,
            first_name=first_name,
            last_name=last_name,
            email=email,
            message=message,
        )

        plain_message = f"Subject: {subject}\nName: {first_name} {last_name}\nEmail: {email}\nMessage: {message}"

        send_mail(
            'New Contact Form Submission',
            plain_message,
           "trackmate.official@gmail.com",
            [email],
            fail_silently=False,
        )

        return redirect("/contact")

    return render(request, "contactUs.html")


def aboutUs(request):
    return render(request, "aboutUs.html")


def loginPage(request):
    if request.method == "POST":
        username = request.POST.get("loginUsername")
        password = request.POST.get("loginPassword")

        if not User.objects.filter(username=username).exists():
            messages.error(request, "Username doesn't exists!")
            return redirect("/login/")

        user = authenticate(username=username, password=password)

        if user is None:
            messages.info(
                request,
                "Incorrect password. Please double-check your password and try again.!",
            )
            return redirect("/login/")

        else:
            login(request, user)
            return redirect("/homepage/")

    return render(request, "login_signup.html")


def is_valid_email(email):
    # Define the regex pattern for email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)


def is_valid_password(password):
    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return False

    # Check if the password contains at least one lowercase letter, one uppercase letter, and one digit
    if (
        not re.search(r"[a-z]", password)
        or not re.search(r"[A-Z]", password)
        or not re.search(r"\d", password)
    ):
        return False

    # Check if the password contains at least one special character (you can customize the set of special characters)
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True


def registerPage(request):
    if request.method == "POST":
        username = request.POST.get("registerUsername")
        password = request.POST.get("registerPassword")
        email = request.POST.get("registerEmail")

        user = User.objects.filter(username=username)

        if user.exists():
            messages.error(request, "Username already exists!")
            return redirect("/login/")

        if not re.match(r"^\w+$", username):
            messages.error(
                request, "Username can only contain letters, numbers, and underscores"
            )
            return redirect("/login/")

        # Check if the username is between 5 and 20 characters long
        if not (5 <= len(username) <= 20):
            messages.error(request, "Username must be between 5 and 20 characters long")
            return redirect("/login/")

        if not is_valid_email(email):
            messages.error(request, "Please enter a valid email address!")
            return redirect("/login/")

        if not is_valid_password(password):
            messages.info(
                request,
                "Please enter a valid password! The password must be at least 8 characters long and include at least one lowercase letter, one uppercase letter, one digit, and one special character.",
            )
            return redirect("/login/")

        user = User.objects.create(
            username=username,
            email=email,
        )

        # user.set_password(password) to encrypt password
        user.set_password(password)
        user.save()
        messages.success(request, "Account created successfully🎉")

        return redirect("/login/")
    return render(request, "login_signup.html")


def scrape_amazon_product(product):
    # Individual product scraping logic for Amazon
    brand_name = product.find("span", class_="a-size-medium a-color-base")
    brand = brand_name.getText().strip() if brand_name else "N/A"

    name_element = product.find(
        "span", class_="a-size-medium a-color-base a-text-normal"
    )
    name = name_element.getText().strip() if name_element else "No Name"

    price_element = product.find("span", class_="a-offscreen")
    price = price_element.getText().strip() if price_element else "No Price"

    ratings_element = product.find("span", class_="a-icon-alt")
    rating_text = (
        ratings_element.get_text(strip=True) if ratings_element else "No Ratings"
    )

    numerical_rating = None
    if rating_text != "No Ratings":
        try:
            numerical_rating = math.ceil(float(rating_text.split()[0]))
        except ValueError:
            print(f"Error converting rating to float: {rating_text}")
            numerical_rating = None

    no_of_ratings_element = product.find("span", class_="a-size-base s-underline-text")
    no_of_ratings = (
        no_of_ratings_element.getText().strip()
        if no_of_ratings_element
        else "No Number of Ratings"
    )

    image_element = product.find("img", class_="s-image")
    image = image_element["src"] if image_element else "No Image"

    link_element = product.find("a", class_="a-link-normal")
    link = link_element["href"] if link_element else "#"

    if (
        name != "No Name"
        and price != "No Price"
        and rating_text != "No Ratings"
        and no_of_ratings != "No Number of Ratings"
        and image != "No Image"
    ):
        return {
            "brand": brand,
            "name": name,
            "price": price,
            "ratings": rating_text,
            "numerical_rating": numerical_rating,
            "no_of_ratings": no_of_ratings,
            "image": image,
            "source": "AMAZON",
            "link": f"https://www.amazon.in{link}",
        }
    else:
        return None


def scrape_amazon(product_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    formatted_product_name = "+".join(product_name.split())
    url = f"https://www.amazon.in/s?k={formatted_product_name.replace(' ', '+')}&ref=nb_sb_noss_2"

    timeout = 10
    max_retries = 100
    retry_delay = 0.0000000000001  # seconds

    for retry_count in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            break  # Exit the loop if the request is successful
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Amazon: {e}")
            if retry_count < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Exiting.")
                return []

    soup = BeautifulSoup(response.text, "lxml")
    product_containers = soup.find_all("div", class_="s-result-item")

    amazon_products = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for product in product_containers:
            future = executor.submit(scrape_amazon_product, product)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    amazon_products.append(result)
            except Exception as e:
                print(f"Error processing Amazon product: {e}")

    return amazon_products


def scrape_flipkart_product(product):
    try:
        # Extracting the name
        name_element = product.find("div", class_="KzDlHZ")
        name = name_element.getText().strip() if name_element else "No Name"

        # Extracting the price
        price_element = product.find("div", class_="Nx9bqj _4b5DiR")
        price = price_element.getText().strip() if price_element else "No Price"

        # Extracting ratings
        ratings_element = product.find("span", class_="Y1HWO0")
        rating_text = (
            ratings_element.getText().strip() if ratings_element else "No Ratings"
        )

        # Converting ratings to numerical
        numerical_rating = None
        if rating_text != "No Ratings":
            try:
                numerical_rating = math.ceil(float(rating_text.split()[0]))
            except ValueError:
                print(f"Error converting rating to float: {rating_text}")
                numerical_rating = None

        # Extracting number of ratings
        no_of_ratings_span = product.find("span", class_="Wphh3N")
        if no_of_ratings_span:
            no_of_ratings_text = no_of_ratings_span.get_text(strip=True)
            numeric_part = re.sub(
                r"[^\d,]", "", no_of_ratings_text.split("&")[0].strip()
            )
            no_of_ratings = numeric_part if numeric_part else "No Number of Ratings"
        else:
            no_of_ratings = "No Number of Ratings"

        # Extracting image URL
        image_element = product.find("img", class_="DByuf4")
        image = image_element["src"] if image_element else "No Image"

        # Extracting product link
        link_element = product.find("a", class_="CGtC98")
        link = link_element["href"] if link_element else "#"

        if (
            name != "No Name"
            and price != "No Price"
            and rating_text != "No Ratings"
            and image != "No Image"
        ):
            return {
                "name": name,
                "price": price,
                "ratings": rating_text,
                "numerical_rating": numerical_rating,
                "no_of_ratings": no_of_ratings,
                "image": image,
                "source": "FLIPKART",
                "link": f"https://www.flipkart.com{link}",
            }
        else:
            return None
    except Exception as e:
        print(f"Error processing Flipkart product: {e}")
        return None


def scrape_flipkart(product_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    formatted_product_name = "+".join(product_name.split())
    url = f"https://www.flipkart.com/search?q={formatted_product_name}"

    timeout = 10
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Find all div elements with class "cPHDOP"
    product_containers = soup.find_all("div", class_="cPHDOP")

    flipkart_products = []

    # Use ThreadPoolExecutor for multithreading inside the function
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for product in product_containers:
            # Submit each product scraping as a separate thread
            future = executor.submit(scrape_flipkart_product, product)
            futures.append(future)

        # Retrieve results when the threads complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    flipkart_products.append(result)
            except Exception as e:
                print(f"Error processing Flipkart product: {e}")

    return flipkart_products


def scrape_hm_product(product):
    try:
        # Individual product scraping logic for H&M
        name_element = product.find("a", class_="link")
        name = name_element.getText().strip() if name_element else "No Name"

        price_element = product.find("span", class_="price regular")
        price = price_element.getText().strip() if price_element else "No Price"

        image_element = product.find("img", class_="item-image")
        image = image_element.get("src", "No Image")

        link_element = product.find("a", class_="link")
        link = link_element.get("href", "#")

        # Check if the product has all the required information
        if name != "No Name" and price != "No Price" and image != "No Image":
            return {
                "brand": "H&M",
                "name": name,
                "price": price,
                "image": image,
                "source": "H&M",
                "link": f"https://www2.hm.com{link}",
            }
        else:
            return None
    except Exception as e:
        print(f"Error processing H&M product: {e}")
        return None


def scrape_hm(product_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    formatted_product_name = "-".join(product_name.split())
    url = f"https://www2.hm.com/en_in/search-results.html?q={formatted_product_name}"

    timeout = 10
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    product_containers = soup.find_all("li", class_="product-item")

    hm_products = []

    # Use ThreadPoolExecutor for multithreading inside the function
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for product in product_containers:
            # Submit each product scraping as a separate thread
            future = executor.submit(scrape_hm_product, product)
            futures.append(future)

        # Retrieve results when the threads complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    hm_products.append(result)
            except Exception as e:
                print(f"Error processing H&M product: {e}")

    return hm_products


def scrape_westside_product(product):
    try:
        # Individual product scraping logic for Westside
        name_element = product.find("a", class_="full-unstyled-link")
        name = name_element.getText().strip() if name_element else "No Name"

        price_element = product.find(
            "span", class_="price-item price-item--sale price-item--last"
        )
        price = price_element.getText().strip() if price_element else "No Price"

        image_element = product.find("img", class_="motion-reduce")
        image = image_element.get("src", "No Image")

        link_element = product.find("a", class_="hover_slider_active")
        link = link_element.get("href", "#")

        # Check if the product has all the required information
        if name != "No Name" and price != "No Price" and image != "No Image":
            return {
                "brand": "WESTSIDE",
                "name": name,
                "price": price,
                "image": image,
                "source": "WESTSIDE",
                "link": f"https://www.westside.com{link}",
            }
        else:
            return None
    except Exception as e:
        print(f"Error processing Westside product: {e}")
        return None


def scrape_westside(product_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    formatted_product_name = "-".join(product_name.split())
    url = f"https://www.westside.com/search?q={formatted_product_name}"

    timeout = 10
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    product_containers = soup.find_all("div", class_="card card--standard card--media")

    westside_products = []

    # Use ThreadPoolExecutor for multithreading inside the function
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for product in product_containers:
            # Submit each product scraping as a separate thread
            future = executor.submit(scrape_westside_product, product)
            futures.append(future)

        # Retrieve results when the threads complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    westside_products.append(result)
            except Exception as e:
                print(f"Error processing Westside product: {e}")

    return westside_products


def scrape_skechers_product(product):
    try:
        # Individual product scraping logic for Skechers
        name_element = product.find("a", title=True)
        name = name_element["title"].strip() if name_element else "No Name"

        price_element = product.find(
            "span",
            class_="value p-heading mobile-view-global product-list-price-mobile list-price",
        )
        price = price_element.getText().strip() if price_element else "No Price"

        image_element = product.find("img", class_="tile-image")
        image = image_element["data-src"] if image_element else "No Image"

        link_element = product.find("a", href=True)
        link = link_element["href"] if link_element else "#"

        # Check if the product has all the required information
        if name != "No Name" and price != "No Price" and image != "No Image":
            return {
                "brand": "SKECHERS",
                "name": name,
                "price": price,
                "image": image,
                "source": "SKECHERS",
                "link": link,
            }
        else:
            return None
    except Exception as e:
        print(f"Error processing Skechers product: {e}")
        return None


def scrape_skechers(product_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    formatted_product_name = "-".join(product_name.split())
    url = f"https://www.skechers.in/search/?q={formatted_product_name}"

    timeout = 10
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    product_containers = soup.find_all("div", class_="product-tile")

    skechers_products = []

    # Use ThreadPoolExecutor for multithreading inside the function
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for product in product_containers:
            # Submit each product scraping as a separate thread
            future = executor.submit(scrape_skechers_product, product)
            futures.append(future)

        # Retrieve results when the threads complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    skechers_products.append(result)
            except Exception as e:
                print(f"Error processing Skechers product: {e}")

    return skechers_products


def scrape_products(product_name):
    product_name = product_name.title()

    if product_name == "Mobile":
        all_products = scrape_amazon_flipkart(product_name)

    elif product_name == "Laptop":
        all_products = scrape_amazon_flipkart_hm_skechers(product_name)

    elif product_name == "Headphones":
        all_products = scrape_amazon(product_name)

    elif product_name == "Neck Band":
        all_products = scrape_amazon(product_name)

    elif product_name == "Ear phones":
        all_products = scrape_amazon(product_name)

    elif product_name == "Ear buds":
        all_products = scrape_amazon(product_name)

    elif product_name == "Books":
        all_products = scrape_amazon(product_name)

    elif product_name == "Clothes":
        all_products = scrape_clothes()

    elif product_name == "Watch":
        all_products = scrape_watches()

    else:
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Concurrently execute scraping functions
            amazon_future = executor.submit(scrape_amazon, product_name)
            flipkart_future = executor.submit(scrape_flipkart, product_name)
            # hm_future = executor.submit(scrape_hm, product_name)
            ws_future = executor.submit(scrape_westside, product_name)
            sk_future = executor.submit(scrape_skechers, product_name)

        # Retrieve results from the futures
        amazon_products = amazon_future.result()
        flipkart_products = flipkart_future.result()
        # hm_products = hm_future.result()
        ws_products = ws_future.result()
        sk_products = sk_future.result()

        # Combine and return the list of products
        all_products = (
            amazon_products
            + flipkart_products
            # + hm_products
            + ws_products
            + sk_products
        )
        # Shuffle products so that they don't return in sequence based on the site
        random.shuffle(all_products)
    return all_products


def scrape_hm_westside_skechers(product_name):
    with ThreadPoolExecutor(max_workers=8) as executor:
        # hm_future = executor.submit(scrape_hm, product_name)
        ws_future = executor.submit(scrape_westside, product_name)
        sk_future = executor.submit(scrape_skechers, product_name)

    # Retrieve results from the futures
    # hm_products = hm_future.result()
    ws_products = ws_future.result()
    sk_products = sk_future.result()

    # Combine and return the list of products
    # all_products = hm_products + ws_products + sk_products
    all_products =  ws_products + sk_products
    # Shuffle products so that they don't return in sequence based on the site
    random.shuffle(all_products)
    return all_products


def scrape_amazon_flipkart_hm_skechers(product_name):
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Concurrently execute scraping functions
        amazon_future = executor.submit(scrape_amazon, product_name)
        flipkart_future = executor.submit(scrape_flipkart, product_name)
        # hm_future = executor.submit(scrape_hm, product_name)
        sk_future = executor.submit(scrape_skechers, product_name)

    # Retrieve results from the futures
    amazon_products = amazon_future.result()
    flipkart_products = flipkart_future.result()
    # hm_products = hm_future.result()
    sk_products = sk_future.result()

    # Combine and return the list of products
    # all_products = amazon_products + flipkart_products + hm_products + sk_products
    all_products = amazon_products + flipkart_products  + sk_products
    # Shuffle products so that they don't return in sequence based on the site
    random.shuffle(all_products)
    return all_products


def scrape_amazon_flipkart(product_name):
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Concurrently execute scraping functions
        amazon_future = executor.submit(scrape_amazon, product_name)
        flipkart_future = executor.submit(scrape_flipkart, product_name)

    # Retrieve results from the futures
    amazon_products = amazon_future.result()
    flipkart_products = flipkart_future.result()

    # Combine and return the list of products
    all_products = amazon_products + flipkart_products
    # Shuffle products so that they don't return in sequence based on the site
    random.shuffle(all_products)
    return all_products


def check_authentication(request):
    authenticated = request.user.is_authenticated
    print(authenticated)
    return JsonResponse({"authenticated": authenticated})


def alertlist(request):
    if request.method == "POST":
        brand = request.POST.get("product_brand")
        name = request.POST.get("product_name")
        price = request.POST.get("product_price")
        ratings = request.POST.get("product_rating")
        no_of_ratings = request.POST.get("product_no_of_ratings")
        link = request.POST.get("product_link")
        image = request.POST.get("product_image")
        budget = request.POST.get("product_budget")
        source = request.POST.get("product_source")

        print("ID :", id)
        print("Name :", name)
        print("price :", price)
        print("ratings :", ratings)
        print("no_of_ratings :", no_of_ratings)
        print("link :", link)
        print("brand :", brand)
        print("image :", image)
        print("budget :", budget)
        print("source :", source)

        Product.objects.create(
            name=name,
            price=price,
            ratings=ratings,
            no_of_ratings=no_of_ratings,
            link=link,
            image=image,
            brand=brand,
            budget=budget,
            source=source,
        )

        check_prices_and_notify.apply_async(countdown=60)

        # redirect_url = request.META.get("HTTP_REFERER", "/default-url/")
        # return redirect(redirect_url)
        return redirect("/search/")
    queryset = Product.objects.all().order_by("-id")

    return render(request, "alertlist.html", {"alertlist": queryset})


def search(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name", "")

        selected_sites = request.POST.getlist(
            "site", []
        )  # Default to an empty list if "site" is not provided

        # If product_name is empty, get the latest recent search's product_name
        if not product_name:
            latest_search = RecentSearch.objects.order_by("-id").first()
            if latest_search:
                product_name = latest_search.productName

        # Create RecentSearch entry
        RecentSearch.objects.create(productName=product_name)

        # If selected_sites is empty, scrape products
        if not selected_sites:
            products = scrape_products(product_name)
        else:
            # Retrieve products based on selected sites
            products = getCheckedSiteProducts(product_name, selected_sites)

        return render(
            request,
            "searchPage.html",
            {"products": products},
        )

    # If the request method is not POST, return an empty list of products
    return render(request, "searchPage.html", {"products": []})


@login_required  # Use the login_required decorator to check authentication
def wishlist(request):
    if request.method == "POST":
        name = request.POST.get("product_name")
        price = request.POST.get("product_price")
        ratings = request.POST.get("product_rating")
        image = request.POST.get("product_image")
        no_of_ratings = request.POST.get("product_no_of_ratings")
        link = request.POST.get("product_link")
        brand = request.POST.get("product_brand")
        source = request.POST.get("product_source")

        print("Name :", name)
        print("price :", price)
        print("ratings :", ratings)
        print("no_of_ratings :", no_of_ratings)
        print("link :", link)
        print("brand :", brand)
        print("source :", source)

        # product = scrape(link)
        print("image :", image)

        wishlist = Wishlist.objects.create(
            name=name,
            link=link,
            brand=brand,
            source=source,
            price=price,
            ratings=ratings,
            no_of_ratings=no_of_ratings,
            image=image,
        )

        # Return a JsonResponse indicating success and authentication
        return JsonResponse(
            {"authenticated": True, "message": "Product added to wishlist successfully"}
        )

    queryset = Wishlist.objects.all().order_by("-id")

    return render(request, "wishlist.html", {"wishlist": queryset})


def removeItemFromWishlist(request):
    if request.method == "POST":
        # Get the product_id from the form submission
        product_id = request.POST.get("product_id")

        wishlist_item = Wishlist.objects.get(id=product_id)

        # Remove the item from the wishlist
        wishlist_item.delete()

        # Retrieve the updated wishlist
        wishlist = Wishlist.objects.filter(user=request.user)

        return redirect("/wishlist/")
    return render(request, "wishlist.html", {"wishlist": wishlist})


def removeItemFromAlert(request):
    if request.method == "POST":
        # Get the product_id from the form submission
        product_id = request.POST.get("product_id")

        alert_item = Product.objects.get(id=product_id)

        # Remove the item from the wishlist
        alert_item.delete()

        # Retrieve the updated wishlist
        alertlist = Product.objects.filter(user=request.user)

        return redirect("/alertlist/")
    return render(request, "alertlist.html", {"alertlist": alertlist})


def logoutView(request):
    logout(request)
    return redirect("/homepage")


@login_required
def userProfileSetting(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # If the profile doesn't exist, create a new one
        profile = UserProfile(user=request.user)

    if request.method == "POST":
        if "deactivate_account" in request.POST:
            # Delete the user account and redirect to the homepage
            request.user.delete()
            # messages.success(request, "Your account has been deactivated.")
            return redirect("/homepage")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if the provided passwords match
        if password != confirm_password:
            messages.error(request, "Passwords did not match!")
            return redirect(
                "userProfileSetting"
            )  # Redirect back to the profile settings page

        user = User.objects.get(username=request.user.username)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username

        # Check if a new password is provided before updating it
        if password:
            user.set_password(password)

        user.save()
        messages.success(request, "Account updated successfully!🎉")

        # Handle profile photo update
        profile_photo = request.FILES.get("profile_photo")
        if profile_photo:
            profile.profile_photo = profile_photo
            profile.save()
            messages.success(request, "Profile photo updated successfully!🎉")

    # Retrieve the updated user information after saving
    user = User.objects.get(username=request.user.username)

    context = {
        "user": user,  # Pass the updated user object to the template
        "profile": profile,
    }

    return render(request, "userProfileSetting.html", context)


@login_required
def deactivate_account(request):
    if request.method == "POST":
        # Add your account deactivation logic here
        request.user.delete()  # This is just an example; customize it based on your requirements
        # messages.success(request, "Your account has been deactivated.")
        return redirect("/homepage/")

    return render(request, "userProfileSetting.html")


def recentSearch(request):
    recentSearch = RecentSearch.objects.all().order_by("-id")
    return render(request, "recentSearch.html", {"recentSearch": recentSearch})


def deleteRecentSearchProduct(request, id):
    queryset = RecentSearch.objects.get(id=id)
    queryset.delete()
    return redirect("/recentSearch")


def Search(request, productName):
    products = scrape_products(productName)

    return render(
        request,
        "searchPage.html",
        {"products": products},
    )


def clearHistory(request):
    queryset = RecentSearch.objects.all()
    queryset.delete()
    return redirect("/recentSearch")
