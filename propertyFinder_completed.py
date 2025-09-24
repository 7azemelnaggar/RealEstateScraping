from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

url = "https://www.propertyfinder.sa/ar/search?c=1&fu=0&ob=mr"
driver = webdriver.Chrome()
driver.get(url)
data = []
# Wait for the page to load
wait = WebDriverWait(driver, 10)

try:
    # Find all property ad links on the page
    ad_links = driver.find_elements(By.CSS_SELECTOR, "a[role='link'][href*='/property/']")
    

    # ad_links = driver.find_elements(By.CSS_SELECTOR, "a.styles-module_property-card_link_iDk-2")
    
    # If the above doesn't work, try alternative selectors
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a.styles-module_property-card_link_r--GK")
    
    # Another fallback selector
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "div[role='link'] a")
    
    print(f"Found {len(ad_links)} ad links on the page")
    
    # Extract unique URLs to avoid opening the same ad multiple times
    # unique_urls = set()
    # for link in ad_links:
    #     href = link.get_attribute('href')
    #     if href:
    #         unique_urls.add(href)
    
    # print(f"Found {len(unique_urls)} unique ads to visit")
    
    # Store the main window handle
    main_window = driver.current_window_handle
    
    # Loop through each unique URL
    for i, url in enumerate(ad_links):
        try:
            print(f"Opening ad {i+1}/{len(ad_links)}")
            
            # Open link in new tab
            driver.execute_script("window.open(arguments[0], '_blank');", url)
            
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            
            # Wait for the page to load
            time.sleep(2)
            
            # Wait 3 seconds as requested
            print(f"Viewing ad for 3 seconds...")
            time.sleep(3)
# ==============================================================================================================================================
            try:
                title = driver.find_element(By.CSS_SELECTOR, "h1").text
            except:
                title = "N/A"   
# ==============================================================================================================================================
            try:
                price = driver.find_element(By.CSS_SELECTOR, ".styles_desktop_price_value_JLKWF").text
            except:
                title = "N/A"   
# ==============================================================================================================================================
            try:
                call_btn = WebDriverWait(driver, 10).until(
                    # EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="call-number-button"]'))
                    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="call-number-button"]')))

                )
                button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="call-number-button"]')))
                call_btn.click()
                print("✅ Clicked phone button")

                # Wait for a link starting with tel:
                phone_link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="tel:"]'))
                )
                phone_number = phone_link.text.strip()
                if not phone_number:  # Sometimes the <span> has the number
                    phone_number = phone_link.get_attribute("href").replace("tel:", "")

                print("📞 Phone number found:", phone_number)

            except Exception as e:
                phone_number = "N/A"
                print("❌ Could not retrieve phone number:", e)

# ==============================================================================================================================================
            try:
                description = driver.find_element(By.CSS_SELECTOR, ".styles_description__tKGaD").text
            except:
                description = "N/A"
# ==============================================================================================================================================
            try:
                # Initialize all fields as N/A
                type_of = area = num_of_rooms = bathrooms = street_width = street_direction = property_age = category = city = region = district = plot_number = land_number = available_from = "N/A"

                # Find all property detail items
                detail_items = driver.find_elements(By.CSS_SELECTOR, ".styles_desktop_list_item_lF_Fh")
                for item in detail_items:
                    try:
                        label_elem = item.find_element(By.CSS_SELECTOR, ".styles_desktop_list_label-text_0YJ8y")
                        value_elem = item.find_element(By.CSS_SELECTOR, ".styles_desktop_list_value_uIdMl")
                        label = label_elem.text.strip()
                        value = value_elem.text.strip()
                        if label == "نوع العقار":
                            type_of = value
                        elif label == "مساحة العقار":
                            area = value
                        elif label == "عدد غرف النوم":
                            num_of_rooms = value
                        elif label == "الحمامات":
                            bathrooms = value
                        elif label == "عرض الشارع":
                            street_width = value
                        elif label == "الواجهة":
                            street_direction = value
                        elif label == "عمر العقار":
                            property_age = value
                        elif label == "فئة":
                            category = value
                        elif label == "المدينة":
                            city = value
                        elif label == "منطقة":
                            region = value
                        elif label == "حي":
                            district = value
                        elif label == "رقم القطعة":
                            plot_number = value
                        elif label == "رقم المخطط":
                            land_number = value
                        elif label == "متاح من":
                            available_from = value
                    except Exception:
                        continue
            except Exception:
                type_of = area = num_of_rooms = bathrooms = street_width = street_direction = property_age = category = city = region = district = plot_number = land_number = available_from = "N/A"
# ==============================================================================================================================================
            
            # Close the current tab
            driver.close()
            
            # Switch back to the main window
            driver.switch_to.window(main_window)

            data.append({
                "Title": title,
                "Price": price,
                "Description": description,
                "Type": type_of,
                "Area": area,
                "Rooms": num_of_rooms,
                "Bathrooms": bathrooms,
                "Street Width": street_width,
                "Street Direction": street_direction,
                "Property Age": property_age,
                "Category": category,
                "City": city,
                "Region": region,
                "District": district,
                "Plot Number": plot_number,
                "Land Number": land_number,
                "Available From": available_from,
                "url": url
            })

            print(f"Closed ad {i+1} - Title: {title} - phone: {phone_number}")

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
    
    
    # Save to CSV
df = pd.DataFrame(data)
df.to_csv("property_finder.csv", index=False, encoding="utf-8-sig")
print("Data saved to property_finder.csv")