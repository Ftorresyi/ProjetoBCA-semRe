# Import the necessary libraries
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set the path to your chromedriver executable
driver_path_chrome = '/webdriver/chromedriver.exe'
driver_path_edge = '/webdriver/msedgedriver.exe'

# Set the URL of the webpage you want to scrape
url = 'http://boletim.servicos.ccarj.intraer/boletim/#/consultar-item'

# Set the text you want to enter in the field
text_to_enter = '6449700'

# Set the path to where you want to save the downloaded CSV file
csv_path = 'Dados_Baixados.csv'

# Start a new instance of the Web driver
driver = webdriver.Chrome(driver_path_chrome)
#driver = webdriver.Edge(driver_path_edge)

# Navigate to the webpage
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, 'button-id')))

# Find the text field you want to fill in and enter the text
#<input step="any" type="text" class="col q-input-target q-no-input-spinner">
#<button data-v-406700f8=""
#text_field = driver.find_element_by_id('text-field-id')
text_field = driver.find_element("col q-input-target q-no-input-spinner")
text_field.clear()
text_field.send_keys(text_to_enter)

# Find the button you want to click and click it
button = driver.find_element('data-v-406700f8=""')
button.click()

# Wait for the table to load
time.sleep(10)

# Find the table and extract its data

table = driver.find_element('//*[@id="estiloConsultar"]/div[1]/table/thead/tr/th[6]')
rows = table.find_element('th')

# Write the data to a CSV file
with open(csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for row in rows:
        data = [cell.text for cell in row.find_elements_by_tag_name('th')]
        writer.writerow(data)

# Quit the driver
driver.quit()