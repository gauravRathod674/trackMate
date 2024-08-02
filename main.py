import concurrent.futures
import requests
from bs4 import BeautifulSoup
import math
import time
import random
from concurrent.futures import ThreadPoolExecutor


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

    timeout = 5
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    product_containers = soup.find_all("div", class_="s-result-item")

    amazon_products = []

    # Use ThreadPoolExecutor for multithreading inside the function
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for product in product_containers:
            # Submit each product scraping as a separate thread
            future = executor.submit(scrape_amazon_product, product)
            futures.append(future)

        # Retrieve results when the threads complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    amazon_products.append(result)
            except Exception as e:
                print(f"Error processing Amazon product: {e}")

    return amazon_products


def scrape_flipkart_product(product):
    # Individual product scraping logic for Flipkart
    name_element = product.find("div", class_="_4rR01T")
    name = name_element.getText().strip() if name_element else "No Name"

    price_element = product.find("div", class_="_30jeq3 _1_WHN1")
    price = price_element.getText().strip() if price_element else "No Price"

    ratings_element = product.find("div", class_="_3LWZlK")
    rating_text = ratings_element.getText().strip() if ratings_element else "No Ratings"

    numerical_rating = None
    if rating_text != "No Ratings":
        try:
            numerical_rating = math.ceil(float(rating_text.split()[0]))
        except ValueError:
            print(f"Error converting rating to float: {rating_text}")
            numerical_rating = None

    no_of_ratings_span = product.find("span", class_="_2_R_DZ")

    # Extract the text inside the span
    if no_of_ratings_span:
        no_of_ratings_text = no_of_ratings_span.get_text(strip=True)

        # Split the text to get only the Ratings part
        no_of_ratings = no_of_ratings_text.split("&")[0].strip()
    else:
        no_of_ratings = "No Number of Ratings"

    image_element = product.find("img", class_="_396cs4")
    image = image_element["src"] if image_element else "No Image"

    link_element = product.find("a", class_="_1fQZEK")
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


def scrape_flipkart(product_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en",
    }

    formatted_product_name = "+".join(product_name.split())
    url = f"https://www.flipkart.com/search?q={formatted_product_name}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

    timeout = 5
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    product_containers = soup.find_all("div", class_="_1AtVbE")

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


def scrape_all_platforms_static():
    with ThreadPoolExecutor() as executor:
        # Create a list of futures for concurrent execution
        futures = [
            # executor.submit(scrape_amazon, "mobiles"),
            # executor.submit(scrape_amazon, "refrigerator"),
            executor.submit(scrape_flipkart, "camera"),
            executor.submit(scrape_flipkart, "iphone 15"),
            executor.submit(scrape_hm, "tshirt"),
            executor.submit(scrape_hm, "jacket"),
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


print(scrape_all_platforms_static())
