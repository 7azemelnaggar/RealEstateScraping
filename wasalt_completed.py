from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

url = "https://wasalt.sa/sale/search?propertyFor=sale&countryId=1&cityId=&type=residential"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

data = []


try:
    # Find all property ad links on the page
    # Try various selectors for Wasalt sale page
    ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/sale/property/']")
    
    # If the above doesn't work, try alternative selectors
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/property/']")
    
    # Another fallback selector for property cards
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, ".property-card a, .listing-item a, .card a")
    
    # More generic selectors for property links
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='property']")
    
    # Try to find any links that might be property ads
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='sale']")
    
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
            time.sleep(3)
# =======================================================================

            try:
                title =  driver.find_element(By.CSS_SELECTOR, ".stylenewPDP_TitleApartmentHeading__wjLoX  ").text
            except:
                title = "N/A"
# =======================================================================
            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, ".style_price__XdLHZ span")
                # Get the text nodes only (ignore child elements like <i> and <div>)
                price = price_elem.get_attribute("innerText").strip()
                # Remove any currency symbols or extra text if needed
                price = price.replace('\n', '').replace('\r', '').strip()
            except:
                price = "N/A"
# =======================================================================
            try:
                price_per_m_elem = driver.find_element(By.CSS_SELECTOR, ".style_monthlyPaymentPriceBox__KrIxm span")
                # Get the text nodes only (ignore child elements like <i> and <div>)
                price_per_m = price_per_m_elem.get_attribute("innerText").strip()
                # Remove any currency symbols or extra text if needed
                price_per_m = price_per_m.replace('\n', '').replace('\r', '').strip()
            except:
                price_per_m = "N/A"
# =======================================================================
            try:
                area = driver.find_element(By.CSS_SELECTOR, "div.style_propInfodetailfigure__LaYkG span")
                area = area.text
            except:
                area = "N/A"
# =======================================================================
            try:
                # Find all info rows inside the info section container
                info_rows = driver.find_elements(By.CSS_SELECTOR, ".style_infoSectionContainer_Lq3Ti .style_infoSectionInnerContainer_SmfLl")
                # Initialize all fields as N/A
                type_of = "N/A"
                age = "N/A"
                front = "N/A"
                street_width = "N/A"
                street_name = "N/A"
                ad_source = "N/A"
                plan_number = "N/A"
                land_number = "N/A"
                other_commitments = "N/A"
                postal_code = "N/A"
                ad_issue_date = "N/A"
                additional_number = "N/A"
                building_number = "N/A"
                electricity = "N/A"
                water = "N/A"
                sub_type_of = "N/A"
                available_in = "N/A"
                # Map Arabic labels to variable names
                label_map = {
                    "استخدام العقار": "type_of",
                    "العمر": "age",
                    "الواجهة": "front",
                    "عرض الشارع": "street_width",
                    "الشارع": "street_name",
                    "مصدر الإعلان": "ad_source",
                    "رقم المخطط": "plan_number",
                    "رقم الأرض": "land_number",
                    "إلتزامات أخرى على العقار": "other_commitments",
                    "الرقم البريدي": "postal_code",
                    "تاريخ اصدار الاعلان": "ad_issue_date",
                    "رقم إضافي": "additional_number",
                    "رقم المبنى": "building_number",
                    "كهرباء": "electricity",
                    "مياه": "water",
                    "نوع العقار الفرعي": "sub_type_of",
                    "متوفر في": "available_in",
                }
                for row in info_rows:
                    try:
                        label = row.find_element(By.CSS_SELECTOR, ".style_infoLable__40uxD").text.strip()
                        value_elem = row.find_elements(By.CSS_SELECTOR, ".style_name__ODkp6")
                        value = value_elem[0].text.strip() if value_elem else ""
                        if label in label_map:
                            var_name = label_map[label]
                            locals()[var_name] = value
                    except Exception:
                        continue
            except Exception:
                type_of = age = front = street_width = street_name = ad_source = plan_number = land_number = other_commitments = postal_code = ad_issue_date = additional_number = building_number = electricity = water = sub_type_of = available_in = "N/A"
# =======================================================================
            # Extract property details from the info list
            try:
                details = driver.find_elements(By.CSS_SELECTOR, "ul.style_propInfodetails_iK9pf > li.style_propInfodetailscell_PValh")
                num_bedrooms = num_bathrooms = living_room = majlis = area = None
                for li in details:
                    caption = li.find_element(By.CSS_SELECTOR, ".style_propInfodetailcaption__cDHsK").text.strip()
                    value = li.find_element(By.CSS_SELECTOR, ".style_propInfodetailfigure__LaYkG span").text.strip()
                    if "غرف نوم" in caption:
                        num_bedrooms = value
                    elif "دورات مياه" in caption:
                        num_bathrooms = value
                    elif "مساحة الأرض" in caption:
                        area = value
                    elif "مسطحات البناء" in caption:
                        building_surfaces = value
                    elif "صالات" in caption:
                        living_room = value
                    elif "مجلس" in caption:
                        majlis = value
                if num_bedrooms is None:
                    num_bedrooms = "N/A"
                if num_bathrooms is None:
                    num_bathrooms = "N/A"
                if area is None:
                    area = "N/A"
                if building_surfaces is None:
                    building_surfaces = "N/A"
                if living_room is None:
                    living_room = "N/A"
                if majlis is None:
                    majlis = "N/A"
            except Exception as e:
                num_bedrooms = num_bathrooms = building_surfaces = area = living_room = majlis = "N/A"

# =======================================================================
            data.append({
                        "Title": title,
                        "Price": price,
                        "Price per Month": price_per_m,
                        # "Type": type_,
                        "Area": area,
                        "Front": front,
                        "age": age,
                        "Street_Width": street_width,
                        "Street_Name": street_name,
                        "Ad_Source": ad_source,
                        "Plan_Number": plan_number,
                        "Num_Bedrooms": num_bedrooms,
                        "Num_Bathrooms": num_bathrooms,
                        "Living_Room": living_room,
                        "Majlis": majlis,
                        "Building_surfaces": building_surfaces,
                        
                        # "Region": Region,
                        # "City": City,
                        # "District": District,
                        # "Fal_License": fal_license,
                        # "Ad_License": ad_license,
                        # "Issue_Date": issue_date,
                        # "Expiry_Date": expiry_date,
                        # "Location": location,
                        # "Description": description,
                        "URL": url
                    })
            print(f"Scraped ad {i+1}:{title} | {area} | {price} | {price_per_m} |{type_of} | {front} | {available_in} | {sub_type_of}")

# =======================================================================
            # Close the current tab
            driver.close()
            
            # Switch back to the main window
            driver.switch_to.window(main_window)
            
            print(f"Closed ad {i+1}")
            
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
df.to_csv("wasalt_properties.csv", index=False, encoding="utf-8-sig")
print("Data saved to wasalt_properties.csv")