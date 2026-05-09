# Python Data Processing Project

## Overview

This project demonstrates a Python-based data processing pipeline that loads JSON data into a MySQL database and performs analytical queries through an object-oriented architecture.

The project focuses on clean code practices, database interaction, query optimization, and modular application design.

## Features

- Loading and parsing multiple JSON files
- Inserting structured data into a MySQL database
- Executing analytical SQL queries
- Object-Oriented Programming (OOP) architecture
- Application of SOLID principles
- Command-line interface using argparse
- Logging system implementation
- SQL query optimization using indexing
- Modular and maintainable code structure

## Technologies Used

- Python
- MySQL
- SQL
- argparse
- logging
- JSON

## Project Structure

Python-projects/

- │
- ├── data/ # Source JSON files
- ├── data_queries/ # Exported query results
- ├── src/
- │ ├── cli/
- │ │ └── cli.py # Command-line interface
- │ │
- │ ├── db/
- │ │ └── db_con.py # MySQL database connection
- │ │
- │ └── handler/
- │ ├── export.py # Export query results in selected format
- │ ├── loader.py # Load JSON files into the database
- │ └── queries.py # SQL query execution
- │
- ├── queries/ # SQL query files
- ├── index.sql # SQL indexes
- ├── schema.sql # Database schema
- ├── main.py # Application entry point
- └── README.md
