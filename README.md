# Driving Weather Forecast

Provides a forecast of weather along a driving route given a start time,
start location, and end location.

## Installation

Use python 2.7 or 3.5. Install dependencies with pip:
 `pip install -r requirements.txt`
 
### Configuration

A config.ini template is provided. Create a 'development' directory and copy 
this file into there so it is untracked (through .gitignore). Get an api key 
for the various services listed in order to run everything.


## Usage

Tools are available to use separately as command-line tools.

### [Directions](directions.py)

```
usage: directions.py [-h] -o ORIGIN -d DESTINATION [-dt DEPARTURE_DATE_TIME]

Driving directions for given addresses

required arguments:
  -o ORIGIN, --origin ORIGIN
                        Start Address
  -d DESTINATION, --destination DESTINATION
                        Destination Address
optional arguments:
  -h, --help            show this help message and exit
  -dt DEPARTURE_DATE_TIME, --date_time DEPARTURE_DATE_TIME
                        Enter departure date and time in the future in the
                        format YYYY-MM-DDThh:mm in 24 hour format.
```
Note: make sure to quote your addresses. example command:
`./directions.py -s "123 fake st" -d "456 main st"`

### [Weather](weather.py)
