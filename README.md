# Driving Weather Forecast

Provides a forecast of weather along a driving route given a start time,
start location, and end location.

## Installation

Use python 2.7 or 3.5. Install dependencies with pip:
 `pip install -r requirements.txt`

## Usage

Tools are available to use separately as command-line tools.

### [Directions](directions.py)

```
usage: directions.py [-h] -s START -d DESTINATION

Driving directions for given addresses

optional arguments:
  -h, --help            show this help message and exit
  -s START, -start START
                        Start Address
  -d DESTINATION, -destination DESTINATION
                        Destination Address
```
Note: make sure to quote your addresses. example command:
`./directions.py -s '123 fake st' -d '456 main st'`

### [Weather](weather.py)
