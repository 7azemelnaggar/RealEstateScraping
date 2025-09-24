from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

url = "https://dealapp.sa/ar/"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

"""Dismiss intro/instruction overlays by interacting with the viewport center and common overlays."""
try:
    # Ensure DOM is ready
    WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")

    # 1) JS-dispatch full click sequence at viewport center (4 times)
    for _ in range(4):
        driver.execute_script(
            """
            const cx = Math.floor(window.innerWidth / 2);
            const cy = Math.floor(window.innerHeight / 2);
            const el = document.elementFromPoint(cx, cy) || document.body;
            const evOpts = {bubbles: true, cancelable: true, composed: true, clientX: cx, clientY: cy, pointerId: 1, isPrimary: true, button: 0};
            try { el.dispatchEvent(new PointerEvent('pointerdown', evOpts)); } catch(e) {}
            try { el.dispatchEvent(new MouseEvent('mousedown', evOpts)); } catch(e) {}
            try { el.dispatchEvent(new PointerEvent('pointerup', evOpts)); } catch(e) {}
            try { el.dispatchEvent(new MouseEvent('mouseup', evOpts)); } catch(e) {}
            try { el.dispatchEvent(new MouseEvent('click', evOpts)); } catch(e) {}
            """
        )
        time.sleep(1)

    # 2) ActionChains backup click at center
    try:
        inner_w, inner_h = driver.execute_script("return [window.innerWidth, window.innerHeight];")
        body = driver.find_element(By.TAG_NAME, "body")
        ActionChains(driver).move_to_element_with_offset(body, inner_w // 2, inner_h // 2).click().perform()
        time.sleep(1)
    except Exception:
        pass

    # 3) Send ESC four times as additional dismiss signals
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(4):
            body.send_keys(Keys.ESCAPE)
            time.sleep(1)
    except Exception:
        pass

    # 4) Force-hide common overlay/backdrop selectors if still present
    driver.execute_script(
        """
        const selectors = [
          '.introjs-overlay', '.introjs-helperLayer', '.introjs-tooltip',
          '.modal-backdrop', '.swal2-container', '.swal2-shown',
          '.cookie', '.cookies', '.cookie-consent',
          '.overlay', '.backdrop', '.ReactModal__Overlay',
          '.location-modal', '.location-backdrop', '.fixed.top-0.left-0.right-0.bottom-0.z-modal'
        ];
        for (const sel of selectors) {
          document.querySelectorAll(sel).forEach(n => { try { n.style.setProperty('display','none','important'); n.style.setProperty('visibility','hidden','important'); n.style.setProperty('pointer-events','none','important'); } catch(e) {} });
        }
        """
    )
    time.sleep(0.2)
except Exception:
    pass

# Accept location/modal if present
try:
    accept_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.location-modal-btn.typographyTextBaseLd4Normal"))
    )
    accept_btn.click()
    time.sleep(2)
except Exception:
    pass

try:
    # Find all property ad links on the page
    ad_links = driver.find_elements(By.CSS_SELECTOR, "div.ad-card-content-wrapper")
    
    # If the above doesn't work, try alternative selectors
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "div.ad-card-main-container ad-card-promoted")
    
    # Another fallback selector
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a.ad-card-content-wrapper")
    
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