from sklearn import ensemble
import pandas
import numpy as np
import time
from sklearn import metrics
from misc import Miscellaneous as msc
from sklearn.model_selection import cross_val_score


class RandomForestClassifier:
	rf = None

	def __init__(self):
		self.rf = ensemble.RandomForestClassifier()

	def load_dataset(self, path, split):
		start_time = time.time()
		print('Loading dataset.')
		names = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Speed(mph)', 'Precipitation(in)', 'Month', 'Weekday', 'Hour', 'Minute', 'is_accident']
		dataframe = pandas.read_csv(path, names=names, delimiter=',')
		data = dataframe.values
		data = data.astype('float32')

		samples = len(data)
		print('Data samples ' + str(samples))
		split = int(split * samples)

		self.x_train = data[:split, :-1]
		self.y_train = data[:split, -1:].astype(int)

		self.x_test = data[split:, :-1]
		self.y_test = data[split:, -1:].astype(int)

		print('Training set: ', len(self.x_train))
		print('Test set: ', len(self.x_test))
		print('------------ %s seconds ------------' % (time.time() - start_time))

	def train(self):
		start_time = time.time()
		print('Training')
		self.rf.fit(self.x_train, np.ravel(self.y_train))
		print('------------ %s seconds ------------' % (time.time() - start_time))

	#type >0 for testing score, <0 for training score, =0 for both
	def classification_report(self, type=0):
		start_time = time.time()
		if (type  <= 0):
			print('Training score: ')
			y_true = np.ravel(self.y_train)
			y_pred = self.rf.predict(self.x_train)
			print(metrics.classification_report(y_true, y_pred, digits=3))
		if (type >= 0):
			print('Testing score:')
			y_true = np.ravel(self.y_test)
			y_pred = self.rf.predict(self.x_test)
			print(metrics.classification_report(y_true, y_pred, digits=3))
		print('------------ %s seconds ------------' % (time.time() - start_time))

	def save_model(self):
		msc.save_object('model.sav', self.rf, comp = 6)

	def load_model(self):
		self.rf = msc.load_object('model.sav')

	def predict(self, X):
		return self.rf.predict(X)

def main():
	clf = RandomForestClassifier()
	clf.load_dataset('final_dataset.csv', 0.7)
	clf.train()
	clf.classification_report(0)
	clf.save_model()

if __name__ == "__main__":
    main()