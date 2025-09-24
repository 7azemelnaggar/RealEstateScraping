from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

url = "https://auction.wasalt.sa/"
driver = webdriver.Chrome()
driver.get(url)
data = []

wait = WebDriverWait(driver, 10)

try:
    ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/auction/']")
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/property/']")
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='auction']")
    if not ad_links:
        ad_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='property']")

    print(f"Found {len(ad_links)} ad links on the page")

    unique_urls = {link.get_attribute('href') for link in ad_links if link.get_attribute('href')}
    print(f"Found {len(unique_urls)} unique ads to visit")

    main_window = driver.current_window_handle

    for i, url in enumerate(unique_urls):
        try:
            print(f"\nOpening ad {i+1}/{len(unique_urls)}")

            driver.execute_script("window.open(arguments[0], '_blank');", url)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)

            # ==================== Extract General Data ====================
            try:
                title = driver.find_element(By.CSS_SELECTOR, 'div.styles_proprtyTitle__pUu0y').text
            except:
                title = "N/A"

            try:
                num_of_assets = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/div[2]/div[1]/div[4]/div[1]/h2/span').text
            except:
                num_of_assets = "N/A"

            try:
                advertiser = driver.find_element(By.CSS_SELECTOR, 'h3.manageby_mngTitle___ZW5V').text
            except:
                advertiser = "N/A"

            try:
                time_for = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/div/div/span/div').text
            except:
                time_for = "N/A"

            # ==================== Extract Assets (Asset1, Asset2...) ====================
            asset_data = {}
            try:
                detail_blocks = driver.find_elements(By.CSS_SELECTOR, "div.propertyCard_gdpRevampCardWrapper__Lcpf2")

                for idx, block in enumerate(detail_blocks, start=1):
                    asset_prefix = f"Asset{idx}_"

                    try:
                        asset_data[asset_prefix + "title"] = block.find_element(By.CSS_SELECTOR, "div.propertyCard_cardTitle__fxBr4").text.strip()
                    except:
                        asset_data[asset_prefix + "title"] = "N/A"

                    try:
                        asset_data[asset_prefix + "city"] = block.find_element(By.CSS_SELECTOR, "div.propertyCard_address__Fo8yQ").text.strip()
                    except:
                        asset_data[asset_prefix + "city"] = "N/A"

                    try:
                        asset_data[asset_prefix + "deposit"] = block.find_element(By.CSS_SELECTOR, "span.propertyCard_depAmount__ooHJR span").text.strip()
                    except:
                        asset_data[asset_prefix + "deposit"] = "N/A"

                    try:
                        asset_data[asset_prefix + "start_price"] = block.find_element(By.CSS_SELECTOR, "span.propertyCard_startBidAmount__jZrxJ span").text.strip()
                    except:
                        asset_data[asset_prefix + "start_price"] = "N/A"

                    try:
                        asset_data[asset_prefix + "image"] = block.find_element(By.CSS_SELECTOR, "div.propertyCard_cardImageWrapper__yJKzA img").get_attribute("src")
                    except:
                        asset_data[asset_prefix + "image"] = "N/A"

                    try:
                        asset_data[asset_prefix + "status"] = block.find_element(By.CSS_SELECTOR, "span[data-testid='statusText']").text.strip()
                    except:
                        asset_data[asset_prefix + "status"] = "N/A"

                    try:
                        asset_data[asset_prefix + "asset_label"] = block.find_element(By.CSS_SELECTOR, "span.propertyCard_propertyAsset_tag__luy3H").text.strip()
                    except:
                        asset_data[asset_prefix + "asset_label"] = "N/A"
            except Exception as e:
                print(f"Error extracting assets: {e}")

            # ==================== Phone Number ====================
            try:
                contact_btn = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div/div[1]/div[2]/div[11]/ul[2]/li[1]/a')
                contact_btn.click()
                modal_number = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="formModalCallOffice"]/div/div/div/div/div/div/div/div[2]/h5[2]'))
                )
                number = modal_number.text.strip()
            except:
                number = "N/A"

            # ==================== Append Data ====================
            row = {
                "title": title,
                "num_of_assets": num_of_assets,
                "advertiser": advertiser,
                "time_for": time_for,
            }
            # Merge assets dynamically
            row.update(asset_data)

            data.append(row)

            print(f"Closed ad {i+1}: {row}")

            driver.close()
            driver.switch_to.window(main_window)

        except Exception as e:
            print(f"Error processing ad {i+1}: {e}")
            try:
                driver.switch_to.window(main_window)
            except:
                pass
            continue

finally:
    time.sleep(5)
    driver.quit()

df = pd.DataFrame(data)
df.to_csv("auctionWasalt.csv", index=False, encoding="utf-8-sig")
print("Data saved to auctionWasalt.csv")