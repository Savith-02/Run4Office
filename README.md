# README

## Overview

This project is a specialized web scraping and data processing pipeline designed to extract, clean, and structure information related to upcoming election dates, filing start and end dates, and office positions in the USA government. The pipeline consists of several stages, including web scraping, data filtering, and data processing, ultimately storing the structured data in JSON or CSV format.

## Project Structure

- **web_crawler_and_scraper**: Contains scripts for web scraping and initial data cleaning.
- **url_filter_and_extraction**: Contains scripts for scoring and filtering data, as well as extracting relevant information.
- **data_processor**: Contains scripts for processing extracted data and storing it in structured formats.

## Usage

### Step 1: Web Scraping

To start the web scraping process, run the following command:

```bash
$ python ./web_crawler_and_scraper/scrape_urls.py
```

- This script will scrape the specified URLs and store the raw HTML content in the `scraped_files` directory.
- The cleaned and formatted files will be stored in the `formatted_files` directory inside `url_filter_and_extraction`.

### Step 2: Scoring and Filtering

Navigate to the `url_filter_and_extraction` directory and run the `score_and_filter.py` script:

```bash
$ python ./url_filter_and_extraction/score_and_filter.py
```

- This script scores each file based on its content. Files with a score greater than 6 are moved to the `filtered` directory.

### Step 3: Data Extraction

Run the `extraction.py` script in the `url_filter_and_extraction` directory:

```bash
$ python ./url_filter_and_extraction/extraction.py
```

- This script extracts important information from the filtered files and stores them in the `shared_data/unstructured_data` directory, along with their URLs.

### Step 4: Data Processing

Finally, process the extracted data using the `processor.py` script in the `data_processor` directory:

```bash
$ python ./data_processor/processor.py
```

- This script processes the unstructured data, validates it, and stores it in a structured format in the `shared_data/structured_data_*` directories.
- If using JSON, files belonging to the same role are stored in the same folder.
- If using CSV, data is stored in the same CSV file.

## Requirements

Ensure you have all necessary dependencies installed. You can manage Python packages using Poetry as specified in your environment setup.

## Notes

- Ensure that the environment variables, such as `OPENAI_API_KEY`, are set up correctly for the scripts to function.
- The project is designed to run on Windows using Git Bash as the terminal and Cursor as the IDE. Adjust paths and commands if using a different setup.
