import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == '__main__':
    chrome_options = uc.ChromeOptions()
    chrome = uc.Chrome(options=chrome_options)
    file = open("url.txt", "r")
    urls = file.readlines()
    collection = []
    for url in urls[0:300]:
        try:
            chrome.get(url)
            myElem = WebDriverWait(chrome, 30).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main-content"]/div/section/div/div[3]/div/div/h1')))
            
            brand = chrome.find_element('xpath', '//*[@id="main-content"]/div/section/div/div[3]/div/div/h1').text.split(" ")[0]
            if brand == 'New':
                brand = "New Balance"
            category = chrome.find_element('xpath',
                                        '//*[@id="main-content"]/div/section/div/div[3]/div/div/h1').text.replace("\n", " ")

            chrome.find_element('xpath', '//*[@id="menu-button-pdp-size-selector"]').click()
            time.sleep(2)
            item = []
            if 'US M' in chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[2]/div/span[1]/span').text or 'US W' in chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[2]/div/span[1]/span').text or 'US' in chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[2]/div/span[1]/span').text or 'EU' in chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[2]/div/span[1]/span').text:
                for i in range(1, 7):
                    if 'UK' in chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[2]/div/span[' + str(i) + ']/span').text:
                        try:
                            chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[2]/div/span[' + str(i) + ']').click()
                            time.sleep(2)
                            # print('0000000000000')
                            for i in range(1, 31):
                                try:
                                    subitem = {}
                                    subitem['size'] = chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[3]/div/button[' + str(i) + ']/span[2]/div/dl/dt').text.split(" ")[1]
                                    print('size', subitem['size'])
                                    subitem['price'] = chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[3]/div/button[' + str(i) + ']/span[2]/div/dl/dd').text.replace("$", "")
                                    print('price', subitem['price'])
                                    item.append(subitem)
                                except:
                                    # print('11111111')
                                    break
                        except:
                            # print('2222222222222')
                            for i in range(1, 31):
                                try:
                                    subitem = {}
                                    subitem['size'] = chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[3]/div/button[' + str(i) + ']/span[2]/div/dl/dt').text
                                    subitem['price'] = chrome.find_element('xpath','//*[@class="css-r6z5ec"]/div/div[3]/div/button[' + str(i) + ']/span[2]/div/dl/dd').text.replace("$", "")
                                    item.append(subitem)
                                except:
                                    # print('3333333333333333')
                                    break
                            pass       
            try:
                chrome.find_element('xpath','//*[@id="main-content"]/div/section[3]/div/div/div/div[2]/button').click()
                time.sleep(1)
                style = chrome.find_element('xpath','//*[@id="main-content"]/div/section[3]/div/div[2]/div/div/div/div/div/div/p').text
                colorway = chrome.find_element('xpath','//*[@id="main-content"]/div/section[3]/div/div[2]/div/div/div/div/div/div[2]/p').text
                try:
                    release_date = chrome.find_element('xpath','//*[@id="main-content"]/div/section[3]/div/div[2]/div/div/div/div/div/div[4]/p').text
                    print('release_date', release_date)
                except:
                    release_date = ""
                try:
                    retail_price = chrome.find_element('xpath','//*[@id="main-content"]/div/section[3]/div/div[2]/div/div/div/div/div/div[3]/p').text.replace("$", "")
                except:
                    retail_price = ""
            except:
                style = chrome.find_element('xpath','//*[@id="main-content"]/div/section[3]/div/div[2]/div/div/div/div/p').text
                colorway = chrome.find_element('xpath', '//*[@id="main-content"]/div/section[3]/div/div[2]/div/div/div/div[2]/p').text
                try:
                    release_date = chrome.find_element('xpath', '//*[@id="main-content"]/div/section[3]/div/div[2]/div/div/div/div[4]/p').text
                except:
                    release_date = ""
                try:
                    retail_price = chrome.find_element('xpath', '//*[@id="main-content"]/div/section[3]/div/div[2]/div/div/div/div[3]/p').text.replace("$", "")
                except:
                    retail_price = ""
            document = {
                'brand': brand,
                'category': category,
                'style': style,
                'release_date': release_date,
                'colorway': colorway,
                'retail_price': retail_price,
                'sizes': item
            }
            # if len(item) == 0:
            #     print(url)
            # else:
            #     collection.append(document)
            collection.append(document)
        except Exception as e:
            print(url)
            print(e)
    print(collection)
    try:
        with open("data.json", "r") as file:
            current_arr = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        current_arr = []
    file.close()
    collection = collection + current_arr

    try:
        with open("data.json", "w") as file:
            json.dump(collection, file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
    file.close()
    print("Data saved to 'data.json'.")
