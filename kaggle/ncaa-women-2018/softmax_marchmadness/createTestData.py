#!/usr/local/bin/python
#
# Creates input vectors for softmax regression from seed and mean points scored for each year.
# 
#

import csv
import sys
import numpy as np

def main():

    year = ['2018']
    count = 0
    x = np.ones((1,37)) 
    labels = np.zeros((1,1))

    for i in range(len(year)):
        print year[i]        
        with open('WStage2DataFiles/WNCAATourneySeeds.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # skip the header
            seedsbyyear = []
            for row in reader:
                if (row[0]==year[i]):
                    seedsbyyear.append(row)

        mean_points_home = []
        mean_points_away = []
        teams = []
        # for every tourney team that year
        for j in range(len(seedsbyyear)):
            seed = seedsbyyear[j][1]
            team = seedsbyyear[j][2]
            teams.append(team)
            with open('WStage2DataFiles/WRegularSeasonCompactResults.csv', 'rb') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None) # skip the header
                points_home = []
                points_away = []
                for row in reader:
                    if (row[0] == year[i]):
                        if (row[2] == team): # This team won the regular season game
                            if (row[7] == '0'): # Number of overtimes this game
                                if (row[6] == 'H'): # Row 6 is if the team that won was home (H) or away (A)
                                    points_home.append(float(row[3]))
                                elif (row[6] == 'A'):
                                    points_away.append(float(row[3]))
                        if (row[4] == team): # This team lost the regular season game
                            if (row[7] == '0'):
                                if (row[6] == 'H'):
                                    points_away.append(float(row[3]))
                                elif (row[6] == 'A'):
                                    points_home.append(float(row[3]))
            # If we didn't find any home or away points data,
            # both fields are zero. We will check for this later with "nopointsdata".
            if (len(points_home)==0 or len(points_away)==0): 
                mean_points_home.append(75.)
                mean_points_away.append(73.)
            else: 
                mean_points_home.append(sum(points_home)/float(len(points_home)))
                mean_points_away.append(sum(points_away)/float(len(points_away)))
        
        teamdata = np.zeros((64,19)) # teamdata[:,0-15] is the seed, one-hot encoded
        for j in range(len(mean_points_home)):
            teamdata[j,np.mod(j,16)] = 1
            teamdata[j,16] = mean_points_home[j]
            teamdata[j,17] = mean_points_away[j]
            teamdata[j,18] = float(teams[j])

        # We want to fill the arrays x and labels.
        # Each row of x is a NCAA Tournament matchup.
        # x[:,0:18] is data for the first team, and x[:,18:36] is data for the second team.
        # x[:,36] is the bias term
        with open('WSampleSubmissionStage2.csv', 'rb') as csvfile:
           reader = csv.reader(csvfile)
           next(reader, None) # skip the header
           for row in reader:
                temp=np.ones((1,37)) 
                if (row[0][0:4] == year[i]):
                    for k in range(len(mean_points_home)):  # 64 for women's
                        if (teamdata[k,18] == float(row[0][5:9])):
                            temp[0,0:18] = teamdata[k,0:18]
                        if (teamdata[k,18] == float(row[0][10:14])):
                            temp[0,18:36] = teamdata[k,0:18]

                    if (count == 0):
                        x[count,:] = temp[0,:]
                    else:
                        x = np.append(x,[temp[0,:]],axis=0)
                    count += 1


    print count
    np.save('testdata_2018.npy', x)
                                   

if __name__ == '__main__':
    main()

