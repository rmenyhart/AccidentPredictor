import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Miscellaneous:
	OG_SIZE = 2906611
	bar_resolution = 200

	def progress_bar(current, total, barLength = 20):
		percent = float(current) * 100 / total
		arrow   = '-' * int(percent/100 * barLength - 1) + '>'
		spaces  = ' ' * (barLength - len(arrow))
		print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')

	def save_object(filename, obj, comp):
		joblib.dump(obj, filename, compress = comp)
		return 1

	def load_object(filename):
		obj = joblib.load(filename)
		return obj

	def explore_dataset(df):
		#column = df["Year"]
		#s = column.value_counts(sort=False).sort_index(ascending=True)
		#s.plot(kind='bar')
		#plt.savefig('acc_per_year.png')

		column = df["Month"]
		s = column.value_counts(sort=False).sort_index(ascending=True)
		s.plot(kind='bar')
		plt.savefig('acc_per_month.png')

		column = df["Weekday"]
		s = column.value_counts(sort=False).sort_index(ascending=True)
		s.plot(kind='bar')
		plt.savefig('acc_per_day.png')

		column = df["Hour"]
		s = column.value_counts(sort=False).sort_index(ascending=True)
		s.plot(kind='bar')
		plt.savefig('acc_per_hour.png')

		grouped = df.groupby(["Month", "Weekday"]).size().reset_index().pivot(index='Month', columns='Weekday')[0]
		plt.figure(figsize=(12, 7))
		sns.heatmap(grouped)
		plt.savefig('acc_by_month_and_day.png')

		grouped = df.groupby(["Weekday", "Hour"]).size().reset_index().pivot(index='Weekday', columns='Hour')[0]
		plt.figure(figsize=(12, 7))
		sns.heatmap(grouped)
		plt.savefig('acc_by_day_and_hour.png')

		out_file = open('means.txt', 'w')
		for column in df.columns:
			out_file.write(column + ' : ' + str(df[column].mean()) + '\n')
		out_file.close()
