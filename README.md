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
- You can set the number of pages to scrape by changing the `pages_to_scrape` variable in the `scrape_urls.py` script.

### Step 2: Scoring and Filtering

Run the `score_and_filter.py` script in the `url_filter_and_extraction` directory:

```bash
$ python ./url_filter_and_extraction/score_and_filter.py
```

- This script scores each file based on its content. Files with a score greater than a cutoff score are moved to the `filtered` directory.
- You can set the cutoff score by changing the `CUTOFF_SCORE` variable in the `score_and_filter.py` script.

### Step 3: Data Extraction

Run the `extraction.py` script in the `url_filter_and_extraction` directory:

```bash
$ python ./url_filter_and_extraction/extraction.py
```

- This script extracts important information from the filtered files and stores them in the `shared_data/unstructured_data` directory, along with their URLs.
- You can adjust the prompt used for extraction by changing the `generate_extraction_prompt` function in the `extraction.py` script to better suit your needs.

### Step 4: Data Processing

Finally, process the extracted data using the `processor.py` script in the `data_processor` directory:

```bash
$ python ./data_processor/processor.py
```

- This script processes the unstructured data, validates it using a pydantic schema, and stores it in a structured format either in JSON or CSV in the `shared_data/structured_data_*` directories.
- If using JSON, files belonging to the same role are stored in the same folder.
- If using CSV, data corresponding to the same role is stored in the same CSV file.

## Requirements

Ensure you have all necessary dependencies installed. You can manage Python packages using Poetry as specified in your environment setup.

## Notes

- Edit the `.env.sample` file to include your OpenAI API key and save it as `.env`.
- The project is designed to run on Windows using Git Bash as the terminal. Adjust paths and commands if using a different setup.
- The files in the `shared_data` directory are not tracked by git to avoid large file storage issues.
- The code under `RAG` is utility code that is not used in the final pipeline yet.
- The code under `Vector_DB` is utility code that is not used in the final pipeline yet.
