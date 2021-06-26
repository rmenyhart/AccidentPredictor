import datetime
from random import randint, random, uniform
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import time
import math
import csv
from misc import Miscellaneous as msc
from sklearn.utils import resample

class DataPipeline:

	column_names = []
	df = None
	nr_positive_samples = 0
	nr_negative_samples = 0
	nr_features = 0
	dbscan = None
	nr_clusters = 0
	nr_noise = 0


	def clean_dataset(self):
		start_time = time.time()
		print("Preprocessing data...")
		column_names = ['ID','Severity','Start_Time','End_Time','Start_Lat','Start_Lng','End_Lat','End_Lng','Distance(mi)','Description','Number','Street','Side','City','County','State','Zipcode','Country','Timezone','Airport_Code','Weather_Timestamp','Temperature(F)','Wind_Chill(F)','Humidity(%)','Pressure(in)','Visibility(mi)','Wind_Direction','Wind_Speed(mph)','Precipitation(in)','Weather_Condition','Amenity','Bump','Crossing','Give_Way','Junction','No_Exit','Railway','Roundabout','Station','Stop','Traffic_Calming','Traffic_Signal','Turning_Loop','Sunrise_Sunset','Civil_Twilight','Nautical_Twilight','Astronomical_Twilight']
		df = pd.read_csv('US_Accidents_Dec20_Updated.csv', names = column_names, delimiter = ',', skiprows=1)
		df = df.drop(['ID','Severity', 'End_Time','End_Lat','End_Lng','Distance(mi)', 'Description','Number','Street','Side','City','County','State','Zipcode','Country','Timezone','Airport_Code','Weather_Timestamp', 'Wind_Direction', 'Wind_Chill(F)', 'Weather_Condition','Amenity','Bump','Crossing','Give_Way','Junction','No_Exit','Railway','Roundabout','Station','Stop','Traffic_Calming','Traffic_Signal','Turning_Loop','Sunrise_Sunset','Civil_Twilight','Nautical_Twilight','Astronomical_Twilight'], axis = 1)
		df = df.dropna()
		df['Start_Time'] = pd.to_datetime(df['Start_Time'], format = '%Y-%m-%d %H:%M:%S')
		df['Month'] = df['Start_Time'].map(lambda x: x.month)
		df['Weekday'] = df['Start_Time'].map(lambda x: x.weekday())
		df['Hour'] = df['Start_Time'].map(lambda x: x.hour)
		df['QuarterHour'] = df['Start_Time'].map(lambda x: x.minute)
		df['is_accident'] = 1
		df = df.drop(['Start_Time'], axis = 1)
		self.column_names = ['Latitude', 'Longitude', 'Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Speed(mph)', 'Precipitation(in)', 'Month', 'Weekday', 'Hour', 'Minute', 'is_accident']
		df.columns = self.column_names
		self.df = df
		self.nr_positive_samples = len(df)
		self.nr_features = len(df.columns)
		print('Kept ' + str(self.nr_positive_samples) + ' positive samples with ' + str(self.nr_features) + ' columns each.')
		print('------------ %s seconds ------------' % (time.time() - start_time))

	def cluster(self):
		print('DBScan Clustering...')
		start_time = time.time()
		coords = self.df[['Latitude', 'Longitude']]
		dbscan = DBSCAN(eps = 0.02/6371, min_samples = 5, metric = 'haversine').fit(np.radians(coords))
		self.dbscan = dbscan
		self.nr_clusters = len(set(dbscan.labels_))
		self.nr_noise = list(dbscan.labels_).count(-1)
		print('Found ' + str(self.nr_clusters) + ' clusters (' + str(self.nr_noise) + ' outliers, ' + str(self.nr_positive_samples - self.nr_noise) + ' inliers).')
		print('------------ %s seconds ------------' % (time.time() - start_time))	

	def save_centroids(self):
		print('Exporting cluster centers...')
		start_time = time.time()
		out_file = open('cluster_centers.csv', 'w')
		for i in range(0, self.nr_clusters - 1):
			cluster_members = self.df[self.dbscan.labels_ == i]
			cluster_members = cluster_members[['Latitude', 'Longitude']]
			mean = np.mean(cluster_members, axis=0)
			out_file.write(str(mean[0]) + ',' + str(mean[1]) + '\n')
		out_file.close()
		print('------------ %s seconds ------------' % (time.time() - start_time))

	def negative_sampling(self, n_samples = 3, n_features = 7):
		print('Negative sampling...')
		start_time = time.time()
		out_file = open('final_dataset.csv', 'w')
		csv_writer = csv.writer(out_file, delimiter=',')
		max_values = []
		min_values = []
		n = 0
		for column_name in self.df.columns:
			column = self.df[column_name]
			min_values.append(column.min())
			max_values.append(column.max())
		for i in range(len(self.df)):
			if (self.dbscan.labels_[i] != -1):
				positive_sample = self.df.iloc[i, :].values
				csv_writer.writerow(positive_sample)
				for j in range (0, n_samples):
					negative_sample = positive_sample
					features_changed = []
					for k in range(0, n_features):
						c = randint(0, 12)
						while (c in features_changed):
							c = randint(0, 12)
						if (c < 8):
							val = uniform(min_values[c], max_values[c])
							negative_sample[c] = round(val, 2)
						else:
							val = randint(min_values[c], max_values[c])
							negative_sample[c] = round(val, 2)
						negative_sample[12] = 0
						n += 1
						features_changed.append(c)
					csv_writer.writerow(negative_sample)
		print('Generated ' + str(n) + ' negative samples.')
		print('------------ %s seconds ------------' % (time.time() - start_time))

def main():
	start_time = time.time()
	dp = DataPipeline()
	dp.clean_dataset()
	msc.explore_dataset(dp.df)
	dp.cluster()
	dp.save_centroids()
	dp.negative_sampling()
	print('Total runtime: %s seconds' % (time.time() - start_time))

if __name__ == "__main__":
    main()