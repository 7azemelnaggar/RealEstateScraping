from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

url = "https://sa.aqar.fm/"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)
data = []

try:
    # Find ad anchors inside the list container
    ad_links = driver.find_elements(By.CSS_SELECTOR, "div.list_Ka30R a[href]")

    # If the above doesn't work, try alternative selectors within cards
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "div.listingCardPoR_B a[href], div._content_W4gas a[href]")

    print(f"Found {len(ad_links)} ad links on the page")

    # Normalize hrefs (preserve order, no deduplication)
    base_url = "https://sa.aqar.fm"
    hrefs = []
    for el in ad_links:
        href = el.get_attribute('href')
        if href:
            if href.startswith('/'):
                href = base_url + href
            hrefs.append(href)
    
    print(f"Found {len(hrefs)} ads to visit")
    
    # Store the main window handle
    main_window = driver.current_window_handle
    
    # Loop through each ad href sequentially
    for i, url in enumerate(hrefs):
        try:
            print(f"Opening ad {i+1}/{len(hrefs)}")
            
            # Open link in new tab
            driver.execute_script("window.open(arguments[0], '_blank');", url)
            
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            
            # Wait for the page to load
            time.sleep(2)
            
            # Wait 3 seconds as requested
            print(f"Viewing ad for 3 seconds...")
# ============================================================================================================================
            try:
                title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div/div[2]/div/div[2]/div[2]/div[1]/h1'))).text
            except:
                title = "N/A"
            try:
                price = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div/div[2]/div/div[2]/div[2]/div[3]/div[1]/div[2]/h2/span'))).text
            except:
                price = "N/A"
             
            try:
                number = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.phone_1-3fK"))).text
            except:
                number = "N/A"
            try:
                advertiser = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.name_W6hBp"))).text
            except:
                advertiser = "N/A"
# ============================================================================================================================
            try:
                # Find all property detail items inside the new spec card
                detail_items = driver.find_elements(By.CSS_SELECTOR, 'div.newSpecCardhWWBI > div._item__4Sv8')
                # Initialize all fields as N/A
                extracted = {
                    "area": "N/A",
                    "property_age": "N/A",
                    "street_width": "N/A",
                    "bathrooms": "N/A",
                    "living_rooms": "N/A",
                    "apartments_count": "N/A",
                    "bedrooms": "N/A",
                    "facade": "N/A",
                    "purpose": "N/A"
                }
                # Map Arabic labels to variable names
                label_map = {
                    "المساحة": "area",
                    "عمر العقار": "property_age",
                    "عرض الشارع": "street_width",
                    "دورات المياه": "bathrooms",
                    "الصالات": "living_rooms",
                    "عدد الشقق": "apartments_count",
                    "غرف النوم": "bedrooms",
                    "الواجهة": "facade",
                    "الغرض": "purpose"
                }
                for item in detail_items:
                    try:
                        label = item.find_element(By.CSS_SELECTOR, 'div.label__qjLO').text.strip()
                        value = item.find_element(By.CSS_SELECTOR, 'div.value_yF2Fx').text.strip()
                        if label in label_map:
                            var_name = label_map[label]
                            extracted[var_name] = value
                    except Exception as e:
                        print(f"Error extracting detail item: {e}")
                area = extracted["area"]
                property_age = extracted["property_age"]
                street_width = extracted["street_width"]
                bathrooms = extracted["bathrooms"]
                living_rooms = extracted["living_rooms"]
                apartments_count = extracted["apartments_count"]
                bedrooms = extracted["bedrooms"]
                facade = extracted["facade"]
                purpose = extracted["purpose"]
            except Exception as e:
                print(f"Error extracting details: {e}")
                area = property_age = street_width = bathrooms = living_rooms = apartments_count = bedrooms = facade = purpose = "N/A"
# ============================================================================================================================
            # Switch back to the main window
            driver.switch_to.window(main_window)

            data.append({
                "title": title,
                "price": price,
                "number": number,
                "area": area,
                "property_age": property_age,
                "street_width": street_width,
                "bathrooms": bathrooms,
                "living_rooms": living_rooms,
                "apartments_count": apartments_count,
                "bedrooms": bedrooms,
                "facade": facade,
                "purpose": purpose,
                "advertiser": advertiser
            })

            print(f"Closed ad {i+1} : title: {title}, price: {price}, number: {number}, area: {area}, property_age: {property_age}, street_width: {street_width}, bathrooms: {bathrooms}, living_rooms: {living_rooms}, apartments_count: {apartments_count}, bedrooms: {bedrooms}, facade: {facade}, purpose: {purpose} , advertiser: {advertiser}")

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
    print(f"Error: {str(e)}")
    
finally:
    # Keep the browser open for a moment to see the results
    time.sleep(5)
    driver.quit()
    
df = pd.DataFrame(data)
df.to_csv("aqar.csv", index=False, encoding="utf-8-sig")
print("Data saved to aqar.csv")