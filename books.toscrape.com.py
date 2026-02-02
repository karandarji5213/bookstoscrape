import os
import logging
import datetime
import requests
import pandas as pd
import mysql.connector
from bs4 import BeautifulSoup


class books_to_scrape:
    def __init__(self):
        # Creating log file to store logs
        logging.basicConfig(filename="books_toscrape log.log", level=logging.INFO)

        # Headers which will be used for taking response from the website
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'http://books.toscrape.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        }

        # Local system MYSQL connection details
        self.database_name = 'books_toscrape'
        self.table_name = 'books_table'
        host = 'localhost'
        user = 'root'
        password = 'admin123'
        # Creating connection and cursor for sql using mysql.connector
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            autocommit=True
        )
        self.cursor = self.connection.cursor()
        # Output CSV file name
        self.filename = 'books.csv'

    # Function to insert data into table
    def insert_data(self, data_dict):
        try:
            # Getting key and value in a list from the data_dict to insert it into table
            field_list = []
            value_list = []
            for field in data_dict:
                field_list.append(str(field))
                value_list.append(str(data_dict[field]).replace("'", "’"))
            fields = ','.join(field_list)
            values = "','".join(value_list)
            insert_db = f"INSERT INTO {self.database_name}.{self.table_name} " + "( " + fields + " ) values ( '" + values + "' )"
            self.cursor.execute(insert_db)
            logging.info(f'Inserted data into table!')
        except Exception as e:
            logging.info(f'Error in inserting data into table! {e}')

    # Function to get response from the website and fetching webpage content
    def get_response(self, page):
        try:
            resp = requests.get(f'https://books.toscrape.com/catalogue/page-{page}.html', headers=self.headers, timeout=10)
            if resp.status_code != 200:
                logging.info(f'Error in response for page {page}! Status code: {resp.status_code}')
            soup = BeautifulSoup(resp.text, 'lxml')
            return soup
        except Exception as e:
            logging.info(f'Error in taking response from website!!!!! {e}')
            return None

    # Save data into CSV file
    def save_csv_data(self, data_dict):
        try:
            df = pd.DataFrame([data_dict])
            if os.path.exists(self.filename):
                df.to_csv(self.filename, mode='a', index=False, header=False)
            else:
                df.to_csv(self.filename, mode='a', index=False, header=True)
            logging.info(f'Inserted data into CSV!')
        except Exception as e:
            logging.info(f'Error in inserting data into CSV! {e}')

    # Create database function which creates database using create database query
    def create_database(self):
        create_query = f"""CREATE DATABASE IF NOT EXISTS {self.database_name}"""
        self.cursor.execute(create_query)

    # Create table function which creates table using create table query
    def create_table(self):
        create_query = f"""
        CREATE TABLE IF NOT EXISTS {self.database_name}.{self.table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            URL VARCHAR(500) UNIQUE,
            Title VARCHAR(500),
            Price VARCHAR(50),
            Availability VARCHAR(50),
            Rating INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_query)

    # This function removes all newline, tab, and carriage-return characters from text and trims leading/trailing spaces, returning a clean single-line string.
    def clean_text(self, text):
        return text.replace('\n', '').replace('\t', '').replace('\r', '').strip()

    # Function to parse webpage to extract data for book
    def get_details(self, book):
        # data_dict dictionary to store data in key value pair
        data_dict = {}
        # ---------------- URL ----------------
        try:
            href = book.find('h3').find('a').get('href', '')
            data_dict['URL'] = self.clean_text('http://books.toscrape.com/catalogue/' + href)
        except Exception as e:
            logging.info(f'Error in taking URL! {e}')
            data_dict['URL'] = ''

        # ---------------- Title ----------------
        try:
            data_dict['Title'] = self.clean_text(book.find('h3').find('a').get('title', ''))
        except Exception as e:
            logging.info(f'Error in taking title! {e}')
            data_dict['Title'] = ''

        # ---------------- Price ----------------
        try:
            price = book.find('p', class_='price_color').get_text(strip=True)
            data_dict['Price'] = self.clean_text(price.replace('Â', ''))
        except Exception as e:
            logging.info(f'Error in taking price! {e}')
            data_dict['Price'] = ''

        # ---------------- Availability ----------------
        try:
            availability = book.find('p', class_='instock availability').get_text(strip=True)
            data_dict['Availability'] = self.clean_text(availability)
        except Exception as e:
            logging.info(f'Error in taking availability! {e}')
            data_dict['Availability'] = ''

        # ---------------- Rating ----------------
        try:
            rating_tag = book.find('p', class_='star-rating')
            rating_classes = rating_tag.get('class', [])
            rating_map = {
                'One': 1,
                'Two': 2,
                'Three': 3,
                'Four': 4,
                'Five': 5
            }
            data_dict['Rating'] = next((rating_map[c] for c in rating_classes if c in rating_map), 0)
        except Exception as e:
            logging.info(f'Error in taking rating! {e}')
            data_dict['Rating'] = 0

        # ---------------- created_at ----------------
        try:
            data_dict['created_at'] = datetime.datetime.now()
        except Exception as e:
            logging.info(f'Error in taking created_at! {e}')
            data_dict['created_at'] = None

        # Calling function to save data into CSV using pandas
        try:
            self.save_csv_data(data_dict)
        except Exception as e:
            logging.info(f'Error in save csv function :- {e}')

        # Calling function to insert data into table
        try:
            self.insert_data(data_dict)
        except Exception as e:
            logging.info(f'Error in insert data into table function :- {e}')

    # Main function which loops through pages
    def get_data(self):
        logging.info(f'Started scraping for books.toscrape website at {datetime.datetime.now()}')

        # Loop for pagination from 1 to 5
        for page in range(1, 6):
            logging.info(f'Started scraping for page {page}!')

            # Calling function to take response from books.toscrape website for the page and store it in soup variable
            try:
                soup = self.get_response(page)
            except Exception as e:
                logging.info(f'Error in taking response from website!!!!! {e}')
                break

            # Xpath to select all books from the page
            try:
                books = soup.find_all('article', class_='product_pod')
            except:
                books = []

            # If there are no books on any page then it will go to the next page
            if not books:
                logging.info(f'Got no books on the page {page}!')
                continue

            # Looping through all the books and scraping URL, Title, Price, Availability and Rating by calling get_details function
            for book in books:
                try:
                    self.get_details(book)
                except Exception as e:
                    logging.info(f'Error in parsing the data for book :- {e}!')


if __name__ == '__main__':
    # Created an object for books_to_scrape class
    books_obj = books_to_scrape()
    # Called create database function
    books_obj.create_database()
    # Called create table function
    books_obj.create_table()
    # Called get data function to get all the data
    books_obj.get_data()
