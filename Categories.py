import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from urllib.parse import urlparse, urlunparse


def update_urls(url):
    parsed_url = urlparse(url)

    # Check if the URL has query parameters
    if parsed_url.query:
        # Remove existing query parameters
        updated_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    else:
        # If there are no query parameters, keep the original URL
        updated_url = url

    # Append '?page=' to the updated URL
    updated_url += '?page='

    return updated_url


def display_categories(url):
    options = Options()
    options.headless = False  # Set to True if you want the browser to run in headless mode

    # Use webdriver_manager to automatically download the GeckoDriver
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
    browser.minimize_window()

    categories_data = {}

    try:
        browser.get(url)

        # Wait for the menu to load
        menu_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div/div/div/div/div/ul'))
        )

        categories = menu_element.find_elements(By.XPATH, 'li')

        print("List of Categories:")
        for category_number, category in enumerate(categories, start=1):
            category_name = category.find_element(By.XPATH, 'a/span[2]').text
            print(f"{category_number}. {category_name}")

            # Dynamically adjust the subcategories XPath based on the index of the parent category
            subcategories_xpath = f'/html/body/div[1]/div/div/div[2]/div/div/div/div/div/div/div/ul/ul[{category_number}]/li'

            subcategory_items = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, subcategories_xpath))
            )

            subcategories_data = {}

            for index, subcategory_item in enumerate(subcategory_items, start=1):
                subcategory_name = subcategory_item.find_element(By.XPATH, 'a/span').text
                subcategory_url = subcategory_item.find_element(By.XPATH, 'a').get_attribute('href')

                # Update the subcategory URLs
                updated_subcategory_url = update_urls(subcategory_url)
                subcategories_data[f"subCategory_{index}_name"] = subcategory_name
                subcategories_data[f"subCategory_{index}_updated_url"] = updated_subcategory_url

                print(
                    f"  Subcategory {index}: {subcategory_name} - Updated URL: {updated_subcategory_url}")

            # Add the data to the categories dictionary
            categories_data[category_name] = subcategories_data

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        browser.quit()

        with open('categories_data.json', 'w') as json_file:
            json.dump(categories_data, json_file, indent=4)


if __name__ == "__main__":
    daraz_url = "https://www.daraz.pk"
    display_categories(daraz_url)
