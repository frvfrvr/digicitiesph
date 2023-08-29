from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from chromedriver_py import binary_path
import streamlit as st
import pandas as pd
import logging
import zipfile
import io
import time
import requests

logging.basicConfig(level=logging.INFO)

def use_driver():
	## Setup chrome options
	chrome_options = Options()
	chrome_options.add_argument("--headless=new") # Ensure GUI is off
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--ignore-ssl-errors=yes')
	chrome_options.add_argument('--ignore-certificate-errors')
	
	driver = webdriver.Chrome(service=ChromeService(executable_path=binary_path), options=chrome_options) 
	
	return driver

def scrape_each_city(city_name: str, driver, mode: str, dfs: list, columns: list, skip_error: bool):
	"""_summary_

	Args:
		city_name_URL (str): city name in URL format (lowercase, spaces replaced with %20)
		driver (_type_): WebDriver
		mode (str): "simple" or "advanced"
		dfs (list): DataFrame list, in correct order: talent, infra, business, digital
	"""
	
	print(city_name, " is being scraped")
	logging.info(f"{city_name} is being scraped")
	start_time = time.time()
	selected_mode = mode.lower()
	talent_df = dfs[0]
	infra_df = dfs[1]
	business_df = dfs[2]
	digital_df = dfs[3]
	talent_columns = columns[0]
	infra_columns = columns[1]
	business_columns = columns[2]
	digital_columns = columns[3]
 
	city_name_URL = city_name.split()
	city_name_URL = [word.lower() for word in city_name_URL]
	city_name_URL = '%20'.join(city_name_URL)
	driver.get(f'http://www.digitalcitiesph.com/location-profiles/cities/{city_name_URL}/')
	driver.implicitly_wait(10)
	time.sleep(10)
	try:
		w = WebDriverWait(driver, 30)
		w.until(EC.title_contains(f"{city_name}"))
		# w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".filter-nav > li:nth-child(1)")))
		logging.info(f"{city_name} Page load happened")
	except TimeoutException:
		if skip_error:
			logging.info(f"{city_name} skipped! Timeout happened no page load ({driver.title}) ({driver.current_url})")
			return talent_df, infra_df, business_df, digital_df
		else:
			logging.info(f"{city_name} error! Timeout happened no page load ({driver.title}) ({driver.current_url})")
	assert city_name in driver.title, f"Expected {city_name} in {driver.title}"
	logging.info(f"Driver redirected to: (Title: {driver.title}) http://www.digitalcitiesph.com/location-profiles/cities/{city_name_URL}/")
	#  obtain population by XPATH
	logging.info(f"Obtaining population data for {city_name}")
	#  Add population
	city_population = driver.find_elements(By.CLASS_NAME, 'score')[0].text.replace(',', '')
	time.sleep(1)
	talent_df.loc[talent_df["City"] == city_name, "Population"] = city_population
	infra_df.loc[infra_df["City"] == city_name, "Population"] = city_population
	business_df.loc[business_df["City"] == city_name, "Population"] = city_population
	digital_df.loc[digital_df["City"] == city_name, "Population"] = city_population
	
	#  imitate clicking of navbar to set menu active and show info according to menu
	extract_vars = {}
 
	#  Talent table
	logging.info(f"Obtaining Talent data for {city_name}")
	if selected_mode == "simple":
		WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".filter-nav > li:nth-child(1)")))
		driver.find_element(By.CSS_SELECTOR, ".filter-nav > li:nth-child(1)").click()
		extract_vars["Total Graduates"] = driver.find_element(By.CSS_SELECTOR, "div:nth-child(1) > .details-overall > .score").text.replace(',', '')
		extract_vars["Higher Education Graduates"] = driver.find_element(By.CSS_SELECTOR, "#talentAccordion1 > .card > .card-link > span").text.replace(',', '')
		extract_vars["Technical Vocational Graduates"] = driver.find_element(By.CSS_SELECTOR, "#talentAccordion2 .collapsed > span").text.replace(',', '')
		extract_vars["Senior High Graduates"] = driver.find_element(By.CSS_SELECTOR, "#talentAccordion3 > .card > .collapsed > span").text.replace(',', '')
		extract_vars["Number of Center of Excellence"] = driver.find_element(By.CSS_SELECTOR, "#talentAccordion4 span").text.replace(',', '')
		extract_vars["Number of Center of Development"] = driver.find_element(By.CSS_SELECTOR, "#talentAccordion5 span").text.replace(',', '')
		extract_vars["Number of Higher Education Institutions"] = driver.find_element(By.CSS_SELECTOR, "#talentAccordion6 span").text.replace(',', '')
		extract_vars["Number of Technical Vocational Institutions"] = driver.find_element(By.CSS_SELECTOR, "#talentAccordion7 span").text.replace(',', '')
		extract_vars["Number of Schools offering Senior High"] = driver.find_element(By.CSS_SELECTOR, "#talentAccordion8 span").text.replace(',', '')
	elif selected_mode == "advanced":
		# Graduates of courses and other disciplines
		pass

	#  Infrastructure table
	logging.info(f"Obtaining Infrastructure data for {city_name}")
	WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".filter-nav > li:nth-child(2)")))
	driver.find_element(By.CSS_SELECTOR, ".filter-nav > li:nth-child(2)").click()
	extract_vars["Office Real Estate"] = driver.find_element(By.CSS_SELECTOR, "#infraAccordion9 .card-link > span").text
	extract_vars["Telco Infrastructure"] = driver.find_element(By.CSS_SELECTOR, "#infraAccordion10 span").text
	extract_vars["Internet Bandwidth"] = driver.find_element(By.CSS_SELECTOR, "#infraAccordion11 .collapsed > span").text
	extract_vars["Power Supply"] = driver.find_element(By.CSS_SELECTOR, "#infraAccordion12 .collapsed > span").text
	extract_vars["Transportation Access"] = driver.find_element(By.XPATH, "//div[@id=\'infraAccordion13\']/div/a/span").text
	extract_vars["Hotel Availability"] = driver.find_element(By.XPATH, "(//div[@id=\'infraAccordion11\']/div/a/span)[2]").text
	extract_vars["Hospital Beds"] = driver.find_element(By.XPATH, "(//div[@id=\'infraAccordion12\']/div/a/span)[2]").text
	extract_vars["Recreational and Tourist Attractions"] = driver.find_element(By.XPATH, "(//div[@id=\'infraAccordion13\']/div/a/span)[2]").text

	#  Business Environment table
	logging.info(f"Obtaining Business Environment data for {city_name}")
	WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".filter-nav > li:nth-child(3)")))
	driver.find_element(By.CSS_SELECTOR, ".filter-nav > li:nth-child(3)").click()
	extract_vars["(Cost) Minimum Wage Nonagri"] = driver.find_element(By.CSS_SELECTOR, "li:nth-child(1) > span").text.replace(',', '')
	extract_vars["(Cost) Monthly Office Space Rental per sqm"] = driver.find_element(By.CSS_SELECTOR, "li:nth-child(2) > span").text
	extract_vars["(Cost) Grade A"] = driver.find_element(By.CSS_SELECTOR, "li:nth-child(3) > span").text
	extract_vars["(Cost) Grade B"] = driver.find_element(By.CSS_SELECTOR, "li:nth-child(4) > span").text
	extract_vars["(Cost) Grade C"] = driver.find_element(By.CSS_SELECTOR, "li:nth-child(5) > span").text
	extract_vars["(Cost) Monthly Power Rates"] = driver.find_element(By.CSS_SELECTOR, "li:nth-child(6) > span").text
	extract_vars["PEZA IT Parks/Centers"] = driver.find_element(By.CSS_SELECTOR, ".collapsed > span").text
	extract_vars["Disaster Preparedness Plan"] = driver.find_element(By.CSS_SELECTOR, "#businessAccordion11 span").text
	extract_vars["Average Crime Solution Efficiency"] = driver.find_element(By.CSS_SELECTOR, "#businessAccordion12 span").text

	#  Digital Parameters table
	logging.info(f"Obtaining Digital Parameters data for {city_name}")
	WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".filter-nav > li:nth-child(4)")))
	driver.find_element(By.CSS_SELECTOR, ".filter-nav > li:nth-child(4)").click()
	extract_vars["Open Innovation Ecosystem"] = driver.find_element(By.CSS_SELECTOR, "#digitalAccordion11 span").text
	extract_vars["Number of Startups"] = driver.find_element(By.CSS_SELECTOR, "#digitalAccordion13 span").text
	extract_vars["Innovation Policy and Incentives"] = driver.find_element(By.CSS_SELECTOR, "#digitalAccordion14 span").text
	extract_vars["Number of Unicorns"] = driver.find_element(By.CSS_SELECTOR, "#digitalAccordion15 span").text

	#  Add scraped data to dataframe using a loop of columns' keys and values
	for i in talent_columns:
		talent_df.loc[talent_df["City"] == city_name, i] = extract_vars[i]
	for i in infra_columns:
		infra_df.loc[infra_df["City"] == city_name, i] = extract_vars[i]
	for i in business_columns:
		business_df.loc[business_df["City"] == city_name, i] = extract_vars[i]
	for i in digital_columns:
		digital_df.loc[digital_df["City"] == city_name, i] = extract_vars[i]

	end_time = time.time()
	print(f"{city_name} took {end_time - start_time} seconds to scrape")
	logging.info(f"{city_name} took {end_time - start_time} seconds to scrape")

	return talent_df, infra_df, business_df, digital_df

@st.cache_data()
def preview(selected_province, mode, skip_error: bool):
	logging.info(f"Preview started {'(Skipping errors)' if skip_error else ''}")
	driver = use_driver()

	# province_name for URL use
	province_name = selected_province.split()
	province_name = [word.lower() for word in province_name]
	province_name = '%20'.join(province_name)

	url = f'http://www.digitalcitiesph.com/location-profiles/provinces/{province_name}/'

	driver.get(url)
	driver.implicitly_wait(10) 
	time.sleep(10)
	logging.info(f"Driver redirected to: {url}")
	logging.info(f"Page title: {driver.title}")
	
	try:
		w = WebDriverWait(driver, 8)
		w.until(EC.title_contains(f"{selected_province}"))
		# w.until(EC.presence_of_element_located((By.CLASS_NAME, 'municipality')))
		logging.info("Page load happened")
	except TimeoutException:
		logging.info("Timeout happened no page load")
	
	assert selected_province in driver.title, f"Expected {selected_province} in {driver.title}"
	# print(driver.title.split()[2:])
	preview_test = driver.title
	preview_test += "\n"

	elements = driver.find_elements(By.CLASS_NAME, 'municipality') 
	# make a dataframe with province name and city names
	# df = pd.DataFrame(columns=['province', 'city'])
 
	# TALENT TABLE
	talent_df = pd.DataFrame([], columns=['Province', 'City', 'Population'])
	# INFRASTRUCTURE TABLE
	infra_df = pd.DataFrame([], columns=['Province', 'City', 'Population'])
	# BUSINESS ENVIRONMENT TABLE
	business_df = pd.DataFrame([], columns=['Province', 'City', 'Population'])
	# DIGITAL PARAMETERS TABLE
	digital_df = pd.DataFrame([], columns=['Province', 'City', 'Population'])
	
 
	if mode == "simple":
		logging.info("Columns for simple mode")
		# COLUMNS
		talent_columns = ['Total Graduates', 'Higher Education Graduates', 'Technical Vocational Graduates', 'Senior High Graduates', 'Number of Center of Excellence', 'Number of Center of Development', 'Number of Higher Education Institutions', 'Number of Technical Vocational Institutions']
		infra_columns = ['Office Real Estate', 'Telco Infrastructure', 'Internet Bandwidth', 'Power Supply', 'Transportation Access', 'Hotel Availability', 'Hospital Beds', 'Recreational and Tourist Attractions']
		business_columns = ['(Cost) Minimum Wage Nonagri', '(Cost) Monthly Office Space Rental per sqm', '(Cost) Grade A', '(Cost) Grade B', '(Cost) Grade C', '(Cost) Monthly Power Rates', 'PEZA IT Parks/Centers', 'Disaster Preparedness Plan', 'Average Crime Solution Efficiency']
		digital_columns = ['Open Innovation Ecosystem', 'Number of Startups', 'Innovation Policy and Incentives', 'Number of Unicorns']

		for i in talent_columns:
			talent_df[i] = None
		for i in infra_columns:
			infra_df[i] = None
		for i in business_columns:
			business_df[i] = None
		for i in digital_columns:
			digital_df[i] = None
  
		logging.info("Columns for simple mode finished")
  		# add rows to dataframe
		# URL is currently at: 'http://www.digitalcitiesph.com/location-profiles/provinces/{province_name}/'
		logging.info(f"URL is currently at: 'http://www.digitalcitiesph.com/location-profiles/provinces/{province_name}/'")
  		# Loop through each city
		for element in elements:
			# Each heading is named after the city
			city_name = element.find_element(By.TAG_NAME, 'h6').text
			new_row = pd.DataFrame({'Province': selected_province, 'City': city_name}, index=[0])
			talent_df = pd.concat([talent_df, new_row], ignore_index=True)
			infra_df = pd.concat([infra_df, new_row], ignore_index=True)
			business_df = pd.concat([business_df, new_row], ignore_index=True)
			digital_df = pd.concat([digital_df, new_row], ignore_index=True)
			
		# Create a list of all the cities from df
		cities = talent_df['City'].tolist()
		for n, city_name in enumerate(cities):
			logging.info(f"{n + 1}/{len(cities)} iteration: {city_name}")
			talent_df, infra_df, business_df, digital_df = scrape_each_city(city_name, driver, mode, [talent_df, infra_df, business_df, digital_df], [talent_columns, infra_columns, business_columns, digital_columns], skip_error=skip_error)

		talent_table = talent_df
		infra_table = infra_df
		business_table = business_df
		digital_table = digital_df
		logging.info(f"Finished extracting {selected_province}")
	elif mode == "advanced":
		# TODO: Additional table for Talent category
		pass

	driver.quit()

	return talent_table, infra_table, business_table, digital_table


@st.cache_data()
def export(selected_province, mode: str, filetype: str, skip_error: bool):
	logging.info(f"{selected_province} {filetype} {mode} Export started")
	talent_df, infra_df, business_df, digital_df = preview(selected_province, mode, skip_error=skip_error)
	dfs = [talent_df, infra_df, business_df, digital_df]
	table_names = ["Talent", "Infrastructure", "Business Environment", "Digital Parameters"]

	#  filetype condition
	if filetype.lower() == "csv":
		zip_file = zipfile.ZipFile(f"{selected_province} - Digital Cities PH.zip", "w")
		buffer = io.BytesIO()

		for i, df in enumerate(dfs):
			df.to_csv(buffer, index=False, compression='gzip')
		csv_bytes = buffer.getvalue()
		for i, df in enumerate(dfs):
			zip_file.writestr(f"{table_names[i]}.csv", csv_bytes)
		zip_file.close()
		logging.info(f"{selected_province} {filetype} {mode} Export Ready")
		return zip_file
	elif filetype.lower() == "excel":
		buffer = io.BytesIO()
		writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
		for i, df in enumerate(dfs):
			#  rename sheet name to table_names[i]
			df.to_excel(writer, sheet_name=f"{table_names[i]}")

		writer.close()

		file_object = buffer.getvalue()
		logging.info(f"{selected_province} {filetype} {mode} Export Ready")
		return file_object

def multitest():
    # return multiple values. show each by multitest().test1, multitest().test2, etc.
    test1 = "test1"
    test2 = "test2"
	
    return test1, test2

