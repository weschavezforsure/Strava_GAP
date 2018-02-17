#!/bin/bash

# Calculates Grade-adjusted pace (in seconds/mile) for up to 100 recent Strava running activities
# 
# Needed: csvkit          https://csvkit.readthedocs.io/en/1.0.2/
#         a Strava API    https://developers.strava.com/
#
# -Wesley Chavez, 02-16-2018
         

# Get first and second page of my activities... I only have 98.  I think I'm only allowed 50 activities per call, so I call twice
curl -X GET https://www.strava.com/api/v3/athlete/activities -d access_token=YOUR_ACCESS_TOKEN -d page=1 -d per_page=50 -s > me_1_50.txt
curl -X GET https://www.strava.com/api/v3/athlete/activities -d access_token=YOUR_ACCESS_TOKEN -d page=2 -d per_page=50 -s > me_2_50.txt

# me_{1,2}_50.txt are literally one line. Separate.
in2csv --format json me_1_50.txt > me_1_50.csv
in2csv --format json me_2_50.txt > me_2_50.csv

# Look for only running activities
csvgrep -c type -r "Run" me_1_50.csv > runs_1.csv
csvgrep -c type -r "Run" me_2_50.csv > runs_2.csv

# Need to know total moving time
csvcut runs_1.csv -c moving_time > moving_time_1.csv
csvcut runs_2.csv -c moving_time > moving_time_2.csv

# Remove csv headers and concatenate
tail -n +2 moving_time_1.csv > moving_time.csv
tail -n +2 moving_time_2.csv >> moving_time.csv

# Need to know total distance
csvcut runs_1.csv -c distance > dist_1.csv
csvcut runs_2.csv -c distance > dist_2.csv

# Remove csv headers and concatenate
tail -n +2 dist_1.csv > dist.csv
tail -n +2 dist_2.csv >> dist.csv

# Look for all activity ids
csvcut runs_1.csv -c id > ids_1.csv
csvcut runs_2.csv -c id > ids_2.csv

# Remove csv headers and concatenate
tail -n +2 ids_1.csv > ids.csv
tail -n +2 ids_2.csv >> ids.csv

# Get altitude data from activities using the ids.  "echo """ is for new lines
while read LINE; do curl -X GET https://www.strava.com/api/v3/activities/"$LINE"/streams/altitude -d access_token=YOUR_ACCESS_TOKEN -d resolution=low -s >> data.txt; echo "" >> data.txt; sleep 1; done < ids.csv

# Save first and last elevation data point.  Resolution=low from the above command means 100 elevation data points, so we cut the first and last.
while read LINE; do if [[ "$LINE" == *"Record Not Found"* ]] ; then echo "0" >> start_elevation.txt; else echo $LINE | in2csv --format json | grep altitude | cut -d, -f 2 >> start_elevation.txt; fi; done < data.txt
while read LINE; do if [[ "$LINE" == *"Record Not Found"* ]] ; then echo "0" >> stop_elevation.txt; else echo $LINE | in2csv --format json | grep altitude | cut -d, -f 101 >> stop_elevation.txt; fi; done < data.txt

# Calculate GAP in minutes/mile
while read -r a && read -r b <&2 && read -r c <&3 && read -r d <&4; do echo -e "$c*1609.34/$d-3.032-.4473*1609.34/$d*($b-$a)" | bc -l >> GAP.txt; done < start_elevation.txt 2< stop_elevation.txt 3< moving_time.csv 4< dist.csv


rm me_1_50.txt
rm me_2_50.txt
rm me_1_50.csv
rm me_2_50.csv
rm runs_1.csv
rm runs_2.csv
rm moving_time_1.csv
rm moving_time_2.csv
rm moving_time.csv
rm dist_1.csv
rm dist_2.csv
rm dist.csv
rm ids_1.csv
rm ids_2.csv
rm ids.csv
rm data.txt
rm start_elevation.txt
rm stop_elevation.txt
