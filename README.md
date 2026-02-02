This project scrapes book data from http://books.toscrape.com using Python and BeautifulSoup, stores the extracted information in both a CSV file and a MySQL database, and logs all activities for monitoring and debugging.


🚀 Features

Scrapes book data from multiple pages
Extracts:
- Book URL
- Title
- Price
- Availability
- Rating

Saves data into:
- CSV file (books.csv)
- MySQL database (books_toscrape.books_table)

Automatic database and table creation
Clean text processing to remove unwanted characters
Robust error handling and logging

 🛠️ Technologies Used

Python 3
Requests – for HTTP requests
BeautifulSoup (bs4) – for HTML parsing
Pandas – for CSV handling
MySQL – for structured data storage
Logging – for execution tracking

⚙️ Database Details

Database Name: books_toscrape
Table Name: books_table


▶️ How to Run the Project
1️⃣ Install Dependencies
pip install requests beautifulsoup4 lxml pandas mysql-connector-python

2️⃣ Update MySQL Credentials
Edit the following inside __init__() if needed:
host = 'localhost'
user = 'root'
password = 'admin123'

3️⃣ Run the Script
python books_to_scrape.py

📄 Output
CSV File: books.csv
MySQL Table: books_toscrape.books_table
Logs: books_toscrape log.log


🧹 Data Cleaning
The project includes a text-cleaning utility that:
Removes newline (\n), tab (\t), and carriage return (\r)
Trims leading and trailing spaces
This ensures clean and consistent data storage.
