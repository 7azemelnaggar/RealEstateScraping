from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

url = "https://www.amakkn.com/search-map/3/all/24.696238181952285/46.51110142939455/default/11/1"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

try:
    # Find all property ad links on the page
    ad_links = driver.find_elements(By.CSS_SELECTOR, "h6.property-name")
    
    # If the above doesn't work, try alternative selectors
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "#tabs_1 > div > div:nth-child(1)")
    
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