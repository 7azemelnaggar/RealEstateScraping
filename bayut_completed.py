from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

url = "https://www.bayut.sa/en/for-sale/properties/ksa/"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 5)

data = []

try:
    # Find all property ad links on the page
    ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/en/property/']")

    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/property/']")

    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, ".property-card a, .listing-item a")

    print(f"Found {len(ad_links)} ad links on the page")

    unique_urls = set()
    for link in ad_links:
        href = link.get_attribute("href")
        if href:
            unique_urls.add(href)

    print(f"Found {len(unique_urls)} unique ads to visit")

    main_window = driver.current_window_handle

    for i, ad_url in enumerate(unique_urls):
        try:
            print(f"Opening ad {i+1}/{len(unique_urls)}")

            driver.execute_script("window.open(arguments[0], '_blank');", ad_url)
            driver.switch_to.window(driver.window_handles[-1])
                
            time.sleep(5)  # let page load

            try:
                more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'More')]")))
                more_btn.click()
                time.sleep(2)
            except:
                pass  # مفيش زر "المزيد"

            # ------------------ SCRAP DATA ------------------
            try:
                title = driver.find_element(By.CSS_SELECTOR, "h1").text
            except:
                title = "N/A"

            try:
                price = driver.find_element(By.CSS_SELECTOR, "span[aria-label='Price'], .9a7b7a70, ._price_X51mi").text
            except:
                price = "N/A"

            try:
                type_ = driver.find_element(By.CSS_SELECTOR, "span[aria-label='Type'], ._249434d2").text
            except:
                type_ = "N/A"

            try:
                area_elements = driver.find_elements(By.CSS_SELECTOR, "span._3458a9d4")
                area = area_elements[2].text if len(area_elements) >= 3 else "N/A"
            except:
                area = "N/A"

            try:
                num_bedrooms = driver.find_element(By.XPATH, "(//span[@class='_3458a9d4'])[1]").text
            except:
                num_bedrooms = "N/A"

            try:
                num_bathrooms = driver.find_element(By.XPATH, "(//span[@class='_3458a9d4'])[2]").text
            except:
                num_bathrooms = "N/A"


# =====================================================================================================================================
            try:
                # Locate the <a> tag with "tel:"
                phone_elem = driver.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
                
                # Option 1: Get number from href
                number = phone_elem.get_attribute("href").replace("tel:", "").strip()
                
                # Option 2: Get visible text (sometimes formatted differently)
                if not number:
                    number = phone_elem.text.strip()
                if not number:
                    number = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Listing phone number'] , ._202f0b9e").text.strip()
            except Exception:
                number = "N/A"
            # ---------------- Location Info ----------------
            Region, City, District = "N/A", "N/A", "N/A"
            try:
                ul = driver.find_element(By.CSS_SELECTOR, "ul.f1a238ef")
                li_items = ul.find_elements(By.TAG_NAME, "li")
                for li in li_items:
                    spans = li.find_elements(By.TAG_NAME, "span")
                    if len(spans) >= 2:
                        label = spans[0].text.strip()
                        value = spans[1].text.strip()
                        if label == "Region":
                            Region = value
                        elif label == "City":
                            City = value
                        elif label == "District":
                            District = value
            except:
                pass

            # ---------------- License Info ----------------
            fal_license, ad_license, issue_date, expiry_date = "N/A", "N/A", "N/A", "N/A"
            try:
                fal_license = driver.find_element(By.CSS_SELECTOR, "span[aria-label='Permit number']").text.strip()
                ad_license = driver.find_element(By.CSS_SELECTOR, "span[aria-label='Permit Number']").text.strip()
                issue_date = driver.find_element(By.CSS_SELECTOR, "span[aria-label='License Issue Date']").text.strip()
                expiry_date = driver.find_element(By.CSS_SELECTOR, "span[aria-label='License Expiry Date']").text.strip()
            except:
                pass

            # ---------------- Others ----------------
            try:
                location = driver.find_element(By.CSS_SELECTOR, "._832b01c7").text
            except:
                location = "N/A"

            try:
                description = driver.find_element(By.CSS_SELECTOR, "._4bbafa79").text
            except:
                description = "N/A"

            # ---------------- Save Data ----------------
            data.append({
                "Title": title,
                "Price": price,
                "Phone_Number": number,
                "Type": type_,
                "Area": area,
                "Num_Bedrooms": num_bedrooms,
                "Num_Bathrooms": num_bathrooms,
                "Region": Region,
                "City": City,
                "District": District,
                "Fal_License": fal_license,
                "Ad_License": ad_license,
                "Issue_Date": issue_date,
                "Expiry_Date": expiry_date,
                "Location": location,
                "Description": description,
                "URL": ad_url
            })

            print(f"Scraped: {title} | {price} | {area} | {num_bedrooms} | {num_bathrooms} | {type_} | {Region} | {City} | {District} | {fal_license} | {number} ")

            # ------------------------------------------------
            driver.close()
            driver.switch_to.window(main_window)

        except Exception as e:
            print(f"Error processing ad {i+1}: {str(e)}")
            try:
                driver.switch_to.window(main_window)
            except:
                pass
            continue

    print("Finished processing all ads")

except Exception as e:
    print(f"Error: {str(e)}")

finally:
    driver.quit()

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("bayut_properties.csv", index=False, encoding="utf-8-sig")
print("Data saved to bayut_properties.csv")