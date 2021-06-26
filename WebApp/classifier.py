import joblib
import sklearn

class Classifier:
	clf = None

	def load_classifier(self, file_name):
		self.clf = joblib.load(file_name)
		return self.clf

	def predict(self, data):
		return self.clf.predict(data)
		