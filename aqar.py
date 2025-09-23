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

try:
    # Find ad anchors inside the list container
    ad_links = driver.find_elements(By.CSS_SELECTOR, "div._list__Ka30R a[href]")

    # If the above doesn't work, try alternative selectors within cards
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "div._listingCard__PoR_B a[href], div._content__W4gas a[href]")

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
            time.sleep(3)
            
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