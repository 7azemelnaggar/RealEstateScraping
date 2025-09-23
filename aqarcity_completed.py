from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

url = "https://www.aqarcity.net/2"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

data = []

try:
    # Find all property ad links on the page
    ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/en/property/']")
    
    # If the above doesn't work, try alternative selectors
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/property/']")
    
    # Another fallback selector
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, ".property-card a, .listing-item a")
    
    print(f"Found {len(ad_links)} ad links on the page")
    
    # Extract unique URLs to avoid opening the same ad multiple times
    unique_urls = set()
    for link in ad_links:
        href = link.get_attribute('href')
        if href:
            unique_urls.add(href)
    
    print(f"Found {len(unique_urls)} unique ads to visit")
    
    # Store the main window handle
    main_window = driver.current_window_handle
    
    # Loop through each unique URL
    for i, url in enumerate(unique_urls):
        try:
            print(f"Opening ad {i+1}/{len(unique_urls)}")
            
            # Open link in new tab
            driver.execute_script("window.open(arguments[0], '_blank');", url)
            
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            
            # Wait for the page to load
            time.sleep(2)
            
            # Wait 3 seconds as requested
            print(f"Viewing ad for 3 seconds...")
            # =================================================================================================
            try:
                title =  driver.find_element(By.CSS_SELECTOR, "h1").text
            except:
                title = "N/A"
            try:
                price =  driver.find_element(By.CSS_SELECTOR, ".btnPriceHead").text
            except:
                price = "N/A"
            try:
                Advertiser =  driver.find_element(By.CSS_SELECTOR, ".button a").text
            except:
                Advertiser = "N/A"
            try:
                advertiser_elem = driver.find_element(By.CSS_SELECTOR, "h2.button.full-width a")
                Advertiser = advertiser_elem.text.strip()
            except:
                Advertiser = "N/A"
            try:
                date_of_advertising = driver.find_element(By.CSS_SELECTOR, ".job-property h5").text
            except:
                date_of_advertising = "N/A"
            # =================================================================================================
            # Extract property details by matching the label text
            area = "N/A"
            miter_price = "N/A"
            num_of_rooms = "N/A"
            type_of = "N/A"
            age_of = "N/A"
            date_of_license = "N/A"
            facade_of = "N/A"
            try:
                items = driver.find_elements(By.CSS_SELECTOR, ".property_infos_card_item")
                for item in items:
                    try:
                        label_elem = item.find_element(By.CSS_SELECTOR, ".property_infos_card_item_value_name")
                        value_elems = item.find_elements(By.CSS_SELECTOR, ".property_infos_card_item_value > div")
                        label = label_elem.text.strip()
                        value = value_elems[-1].text.strip() if value_elems else ""
                        if "مساحة العقار" in label:
                            area = value
                        elif "سعر الوحدة" in label or "سعر المتر" in label:
                            miter_price = value
                        elif "عدد الغرف" in label:
                            num_of_rooms = value
                        elif "نوع العقار" in label:
                            type_of = value
                        elif "عمر العقار" in label:
                            age_of = value
                        elif "واجهة العقار" in label:
                            facade_of = value
                        elif "تاريخ إنشاء ترخيص الإعلان" in label:
                            date_of_license = value
                    except Exception:
                        continue
            except Exception:
                pass
            # =================================================================================================
            
            time.sleep(3)
            
            # Close the current tab
            driver.close()
            
            # Switch back to the main window
            driver.switch_to.window(main_window)
            
            print(f"Closed ad {i+1} | Title: {title} | Price: {price} | Area: {area} | Meter Price: {miter_price} | Rooms: {num_of_rooms} | {date_of_advertising}")
            



            data.append({
                "title": title,
                "price": price,
                "area": area,
                "meter_price": miter_price,
                "num_of_rooms": num_of_rooms,
                "type_of": type_of,
                "age_of": age_of,
                "date_of_license": date_of_license,
                "facade_of": facade_of,
                "Advertiser": Advertiser,
                "date_of_advertising": date_of_advertising,
                "url": url
            })
        except Exception as e:
            print(f"Error processing ad {i+1}: {str(e)}")
            # Make sure we're back on the main window
            try:
                driver.switch_to.window(main_window)
            except:
                pass
            continue
    
    print("Finished processing all ads")
    
except Exception as e:
    print(f"Error: {str(e)} ")
    
finally:
    # Keep the browser open for a moment to see the results
    time.sleep(5)
    driver.quit()
    
df = pd.DataFrame(data)
df.to_csv("aqarcitypg2.csv", index=False, encoding="utf-8-sig")
print("Data saved to aqarcity.csv")