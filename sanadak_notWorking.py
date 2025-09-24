from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

url = "https://sanadak.sa/"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

try:
    # Collect property ad links using robust XPaths and light scrolling
    unique_urls = set()

    def collect_links():
        elements = driver.find_elements(
            By.XPATH,
            "//a[contains(@href, '/property') or contains(@href, '/properties') or contains(@href, '/ad') or contains(@href, '/listing')]"
            + "[not(contains(@href,'#')) and not(starts-with(@href,'javascript')) and not(starts-with(@href,'tel')) and not(starts-with(@href,'mailto'))]"
        )
        for el in elements:
            href = el.get_attribute('href')
            if not href:
                continue
            # Only keep sanadak domain links
            if 'sanadak.sa' not in href:
                continue
            # Heuristic: avoid obvious non-ad pages
            if any(x in href for x in [
                '/contact', '/about', '/login', '/register', '/terms', '/privacy', '/blog'
            ]):
                continue
            unique_urls.add(href.split('?')[0])

    # Initial wait for any anchors
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
    except:
        pass

    collect_links()

    # Do a few scrolls to load lazy content
    last_height = driver.execute_script('return document.body.scrollHeight')
    for _ in range(4):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(1.5)
        collect_links()
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height

    print(f"Found {len(unique_urls)} unique ads to visit")
    
    # Store the main window handle
    main_window = driver.current_window_handle
    
    # Loop through each unique URL
    for i, url in enumerate(list(unique_urls)):
        try:
            print(f"Opening ad {i+1}/{len(unique_urls)}")

            # Open a guaranteed new tab (Selenium 4 API) and navigate
            driver.switch_to.new_window('tab')
            driver.get(url)

            # Give the ad page some time
            time.sleep(2)
            print(f"Viewing ad for 3 seconds...")
            time.sleep(3)

            # Close the ad tab
            driver.close()

            # Switch back to the main window (ensure it's still present)
            if main_window in driver.window_handles:
                driver.switch_to.window(main_window)
            else:
                # Fallback to the first available handle
                driver.switch_to.window(driver.window_handles[0])

            print(f"Closed ad {i+1}")

            # Small delay between tabs to reduce flakiness
            time.sleep(0.5)

        except Exception as e:
            print(f"Error processing ad {i+1}: {str(e)}")
            # Try to recover to a valid window
            try:
                if main_window in driver.window_handles:
                    driver.switch_to.window(main_window)
                elif driver.window_handles:
                    driver.switch_to.window(driver.window_handles[0])
            except Exception:
                pass
            continue
    
    print("Finished processing all ads")
    
except Exception as e:
    print(f"Error: {str(e)}")
    
finally:
    # Keep the browser open for a moment to see the results
    time.sleep(5)
    driver.quit()