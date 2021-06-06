import csv
import bayes
import string


def clean(s):
        translator = str.maketrans("", "", string.punctuation)
        return s.translate(translator)
if __name__ == "__main__":

    with open("data/SMSSpamCollection") as f:
        data = list(csv.reader(f, delimiter="\t"))

    X, y = [], []

    for target, msg in data:
        X.append(msg)
        y.append(target)

    X = [clean(x).lower() for x in X]


    X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
    alpha = float(input('alpha:\n'))
    model = bayes.NaiveBayesClassifier(alpha)
    model.fit(X_train, y_train)
    print(model.score(X_test, y_test))
