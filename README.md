# Weather Application - Module 6 Lab

## Student Information
- **Name**: Mark Vincent Senosin Rana
- **Student ID**: 231004379
- **Course**: CCCS 106
- **Section**: BSCS 3A

## Project Overview
The weather app asks the user for the city he/she wanted to check for the city's corresponding weather at the time.

## Features Implemented
The feautes implemented include weather condition icons and colors -- making the background color based on the weather of the city/place that I enter. The next feature used is an alert and warnings whether the weather is too cold or too hot.

### Base Features
- [/] City search functionality
- [/] Current weather display
- [/] Temperature, humidity, wind speed
- [/] Weather icons
- [/] Error handling
- [/] Modern UI with Material Design

### Enhanced Features
1. **Background Changing Color and Weather Icons**
   - I have stated this earlier but this feature is a background color-based on the weather of the city.
   - I chose this feature to easily determine the weather just by seeing the background color.
   - It was hard implementing this feature, finding where to place it and the "kabuohan" of the code is changing because of this added feature.

2. **Weather Alerts and Warnings**
   - This feature displays alerts for extreme weather conditions, for example is extreme hot and extreme cold weather in a city.
   - I chose this feature for the purpose of alerting travelers and adventurer to know the weather condition for their next city goal.
   - At first it was hard inserting this feature and it was not showing on the app, but then I asked a classmate on where to put the code and it worked.

## Screenshots
![DEFAULT PAGE](<SCREENSHOT/DEFAULT PAGE.png>)
![SAMPLE CITY WITH ITS FEATURES](<SCREENSHOT/SAMPLE CITY WITH ITS FEATURES.png>)
![SAMPLE CITY WITH THE WARNING FEATURE (HIGH UV)](<SCREENSHOT/SAMPLE CITY WITH THE WARNING FEATURE (HIGH UV).png>)
![SAMPLE CITY WITH THE WARNING FEATURE](<SCREENSHOT/SAMPLE CITY WITH THE WARNING FEATURE.png>)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/macmac-12/cccs106-projects.git
cd cccs106-projects/mod6_labs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OpenWeatherMap API key to .env