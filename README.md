# 🏙 digicitiesph [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://digicitiesph.streamlit.app/)

A Streamlit web app that extracts the profile of cities of the Philippines from the website Digital Cities PH.

```mermaid
flowchart TD
    A([User]) --> B[Streamlit App]
    B --> C[Selenium]
    C -- extracts each city data\nof province from --> D[(Digital Cities PH\n Website)] 
    D -- transforms each city data\n to respective categories in tables --> E[Pandas]
    E -- load the tables for preview --> B
    B -- exports tables to CSV/Excel --> A

```

# Features

* [X] Select one of 81-82 provinces of the Philippines and extract the Talent, Infrastructure, Business Environment and Digital Parameter data of all the cities/municipalities under it.
* [X] Preview extracted datasets before exporting
* [X] APA Format Citation for the data source Digital Cities PH.
* [X] Export to Excel with worksheets
* [ ] Export to CSV files in zip
* [X] Simple Extraction Mode (general details)
* [ ] Advanced Extraction Mode (more details)
* [X] Post elapsed time on successful extraction
* [X] Skip error button in preview tab when encoutering issues

# Screenshot

![](assets/20230827_224011_image.png)

# Benchmark Test

* Select provinces "Batanes" or "Guimaras" for short benchmark test (provinces with least cities/municipalities)
* Select provinces "Bohol" or "Cebu" for long benchmark test (provinces with most cities/municipalities)
