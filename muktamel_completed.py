import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

url = "https://www.muktamel.com/%D8%B9%D9%82%D8%A7%D8%B1%D8%A7%D8%AA-%D9%84%D9%84%D8%A8%D9%8A%D8%B9/%D8%A7%D9%84%D8%B3%D8%B9%D9%88%D8%AF%D9%8A%D8%A9/"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

data = []

try:
    # Find all property ad links on the page
    ad_links = driver.find_elements(By.CSS_SELECTOR, "a.item-link")
    
    # If the above doesn't work, try alternative selectors
    if not ad_links:
        ad_links = driver.find_elements(By.XPATH, '//*[@id="listContainer"]/div/div/div[3]/div[1]/div[1]/a')
    
    # Another fallback selector
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "h2.price text-red d-flex align-items-end order-0")

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
# ==========================================================================================================================================================
            try:
                title = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/section/div/div[1]/div[1]/h1').text
            except:
                title = "N/A"
# ==========================================================================================================================================================
            try:
                price = driver.find_element(By.CSS_SELECTOR, 'h2.number-text').text
            except:
                price = "N/A"
# ==========================================================================================================================================================
            try:
                # Find all property detail blocks inside the main row
                detail_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.row[style*="justify-content: space-evenly"] > div.text-center')
                # Initialize all fields as N/A
                extracted = {
                    "area": "N/A",
                    "type_of": "N/A",
                    "available_in": "N/A",
                    "sub_type_of": "N/A"
                }
                # Map Arabic labels to variable names
                label_map = {
                    "مساحة العقار": "area",
                    "تشطيب العقار": "sub_type_of",
                    "نوع العقار": "type_of",
                    "عمر العقار": "available_in",
                }
                for block in detail_blocks:
                    try:
                        label = block.find_element(By.CSS_SELECTOR, 'h6.text-black').text.strip()
                        # Try to get value from h4 or h5
                        value = ""
                        if label == "مساحة العقار":
                            # Area is in h4
                            value = block.find_element(By.CSS_SELECTOR, 'h4.number-text').text.strip()
                        elif label == "سعر العقار":
                            continue  # skip price, already extracted
                        else:
                            h5s = block.find_elements(By.CSS_SELECTOR, 'h5.text-red, h5.font-size-20px')
                            if h5s:
                                value = h5s[0].text.strip()
                        if label in label_map:
                            var_name = label_map[label]
                            extracted[var_name] = value
                    except Exception as e:
                        print(f"Error extracting detail block: {e}")
                area = extracted["area"]
                type_of = extracted["type_of"]
                available_in = extracted["available_in"]
                sub_type_of = extracted["sub_type_of"]
            except Exception as e:
                print(f"Error extracting details: {e}")
                area = type_of = available_in = sub_type_of = "N/A"
                
# ==========================================================================================================================================================
            try:
                details = driver.find_elements(By.CSS_SELECTOR, "div.inner-conts > div.inner-cont")
                # Initialize all fields as N/A
                num_of_rooms = "N/A"
                num_of_halls = "N/A"
                num_of_bathrooms = "N/A"
                # Map Arabic labels to variable names
                label_map = {
                    "الغرف": "num_of_rooms",
                    "الصالات": "num_of_halls",
                    "الحمامات": "num_of_bathrooms",
                }
                # Use a dict to store extracted values
                extracted = {
                    "num_of_rooms": "N/A",
                    "num_of_halls": "N/A",
                    "num_of_bathrooms": "N/A"
                }
                for row in details:
                    try:
                        label = row.find_element(By.TAG_NAME, "label").text.strip()
                        value = row.find_element(By.CSS_SELECTOR, "span.number-text").text.strip()
                        if label in label_map:
                            var_name = label_map[label]
                            extracted[var_name] = value
                    except Exception:
                        continue
                num_of_rooms = extracted["num_of_rooms"]
                num_of_halls = extracted["num_of_halls"]
                num_of_bathrooms = extracted["num_of_bathrooms"]
            except Exception:
                num_of_rooms = num_of_halls = num_of_bathrooms = "N/A"
# ==========================================================================================================================================================
            try:
                advertiser = driver.find_element(By.CSS_SELECTOR, 'div.title').text
            except:
                advertiser = "N/A"
# ==========================================================================================================================================================
            try:
                location = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div/div[1]/div[2]/div[9]/div/div/div/div[2]/div[1]/p/span').text
            except:
                location = "N/A"
# ==========================================================================================================================================================
            try:
                # Click the "اتصل بنا" button to open the modal
                contact_btn = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div/div[1]/div[2]/div[11]/ul[2]/li[1]/a')
                contact_btn.click()
                # Wait for the modal to appear and the phone number to be visible
                modal_number = WebDriverWait(driver, 5).until(
                    # EC.visibility_of_element_located((By.XPATH, '//*[@id="formModalCallOffice"]/div/div/div/div/div/div/div/div[2]/h5[2]/span[2]'))
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="formModalCallOffice"]/div/div/div/div/div/div/div/div[2]/h5[2]'))
                )
                number = modal_number.text.strip()
            except Exception:
                number = "N/A"
# ==========================================================================================================================================================
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
                "available_in": available_in,
                "sub_type_of": sub_type_of,
                "num_of_rooms": num_of_rooms,
                "num_of_halls": num_of_halls,
                "num_of_bathrooms": num_of_bathrooms,
                "advertiser": advertiser,
                "url": url
            })

            print(f"Closed ad {i+1} : title: {title} ,Location: {location} , number: {number} ")

        except Exception as e:
            print(f"Error processing ad {i+1}: {str(e)} ")
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
df.to_csv("muktamel.csv", index=False, encoding="utf-8-sig")
print("Data saved to muktamel.csv")