from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
from selenium.webdriver.common.by import By

url = "https://sa.sakan.co/ar/properties/sale"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)
data=[]
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
# ===================================================================================================================
            try:
                title = driver.find_element(By.CSS_SELECTOR, "h1.details__header-title").text
            except:
                title = "N/A"            
# ===================================================================================================================

            try:
                price = driver.find_element(By.CSS_SELECTOR, ".price span.fb").text
            except:
                price = "N/A"

# ===================================================================================================================
            try:
                advertiser = driver.find_element(By.CSS_SELECTOR, ".inner__info span").text
            except:
                advertiser = "N/A"

# ===================================================================================================================

# ===================================================================================================================
            # try:
            #     # Resolve phone number from visible text or onclick handlers (phone/WhatsApp)
            #     number = "N/A"

            #     # Primary: visible text inside span.tel-no
            #     try:
            #         tel_el = driver.find_element(By.CSS_SELECTOR, ".actions .tel-no")
            #         tel_text = (tel_el.text or "").strip()
            #         if tel_text:
            #             match = re.search(r"\+?\d[\d]{8,14}", tel_text)
            #             number = match.group(0) if match else tel_text
            #         # Fallback: onclick on the tel-no span
            #         if number == "N/A":
            #             onclick = tel_el.get_attribute("onclick") or ""
            #             match = re.search(r"\+?\d[\d]{8,14}", onclick)
            #             if match:
            #                 number = match.group(0)
            #     except Exception:
            #         pass

            #     # Fallback: WhatsApp button onclick
            #     if number == "N/A":
            #         try:
            #             wa_el = driver.find_element(By.CSS_SELECTOR, ".actions .tel-no")
            #             onclick = wa_el.get_attribute("onclick") or ""
            #             match = re.search(r"\+?\d[\d]{8,14}", onclick)
            #             if match:
            #                 number = match.group(0)
            #         except Exception:
            #             pass
            # except Exception:
            #     number = "N/A"
            
            # try:
            #     # Try to get the number from the visible text in span.tel-no
            #     tel_el = driver.find_element(By.CSS_SELECTOR, ".tel-no")
            #     number = tel_el.text.strip()
            #     # If text is empty, try to extract from the onclick attribute
            #     if not number:
            #         onclick = tel_el.get_attribute("onclick") or ""
            #         match = re.search(r"\+?\d[\d]{8,14}", onclick)
            #         number = match.group(0) if match else "N/A"
            # except:
            #     number = "N/A"


            try:
    # Locate the <a> element
                elem = driver.find_element(By.CSS_SELECTOR, "a.btn-call")

                # Get the onclick attribute
                onclick = elem.get_attribute("onclick")

                # Extract phone number using regex
                match = re.search(r"\+?\d{9,15}", onclick)
                number = match.group(0) if match else "N/A"
            except Exception:
                number = "N/A"
# ===================================================================================================================
            try:
                details = driver.find_elements(By.CSS_SELECTOR, ".inner .tr")
                # Initialize all fields as N/A
                area = "N/A"
                type_of = "N/A"
                num_of_rooms = "N/A"
                available_in = "N/A"
                sub_type_of = "N/A"
                # Map Arabic labels to variable names
                label_map = {
                    "المساحة": "area",
                    "غرف": "num_of_rooms",
                    "نوع العقار": "type_of",
                    "متوفر في": "available_in",
                    "نوع العقار الفرعي": "sub_type_of",
                }
                for row in details:
                    try:
                        label = row.find_element(By.CSS_SELECTOR, ".fn").text.strip()
                        value = row.find_elements(By.CSS_SELECTOR, ".fn.fn--b")
                        if value:
                            value = value[0].text.strip()
                        else:
                            value = ""
                        if label in label_map:
                            var_name = label_map[label]
                            locals()[var_name] = value
                    except Exception:
                        continue
            except Exception:
                 area = type_of = num_of_rooms = available_in = sub_type_of = "N/A"
                
# ===================================================================================================================
            
            time.sleep(3)
            
            # Close the current tab
            driver.close()
            
            # Switch back to the main window
            driver.switch_to.window(main_window)

            data.append({
                "title": title,
                "price": price,
                "area": area,
                "type_of": type_of,
                "num_of_rooms": num_of_rooms,
                "available_in": available_in,
                "sub_type_of": sub_type_of,
                "advertiser": advertiser,
                "number": number,
                "url": url
            })

            print(f"Closed ad {i+1} | Title: {title} | Price: {price} | Area: {area} | Type: {type_of} | Rooms: {num_of_rooms} | Available In: {available_in} | Sub Type: {sub_type_of} | Advertiser: {advertiser} | Number: {number}")

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
df.to_csv("sakan_ads.csv", index=False, encoding="utf-8-sig")
print("Data saved to sakan_ad.csv")