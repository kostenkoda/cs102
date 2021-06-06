import collections, math

class NaiveBayesClassifier:

    def __init__(self, alpha = 1):
        self.alpha = alpha
        self.classes = []
        self.classes_p = dict()
        self.X_set = set()
        self.d = int() #размер вектора признаков
        self.counters = dict()
        self.count_words = dict()

    def fit(self, X, y):
        #определяем априорные вероятности классов
        y_list = y
        self.classes = list(set(y))
        for c in self.classes:
            self.classes_p[c] = y_list.count(c) / len(y_list)

        #множество всех слов
        set_x = str()
        for x in X:
            set_x+=x
        set_x = set(set_x.split(" "))
        self.X_set = set_x
        self.d = len(set_x)

        #подсчет количества слов по классам
        sort_massages = dict()
        for key in self.classes:
            sort_massages[key] = str()
        for i,msg in enumerate(X):
            sort_massages[y[i]]+=msg
        for key in self.classes:
            sort_massages[key] = sort_massages[key].split(" ")

        for key in self.classes:
            self.counters[key] = collections.Counter()

            for word in sort_massages[key]:
                self.counters[key][word]+=1

            self.count_words[key] = sum(self.counters[key].values())




    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        predicts=[]
        for msg in X:
            words = msg.split(" ")
            words_p = dict()
            for key in self.classes:
                words_p[key] = []
            for word in words:
                if word in self.X_set:
                    for key in self.classes:
                        words_p[key].append(
                        (self.counters[key][word] + self.alpha)/(self.count_words[key] + self.d*self.alpha)
                        )
                else:
                    for key in self.classes:
                        words_p[key].append(0)
            keys_res = dict()
            for key in self.classes:
                keys_res[key]=math.log(self.classes_p[key]) + sum([math.log(x) for x in words_p[key] if x > 0])

            with open('temp', 'w') as f:
                for v in keys_res.values():
                    f.write(str(v)+'\n')
                f.write('\n')
                for key in self.classes:
                    f.write(key)
            max_ = keys_res[self.classes[0]]
            predict = self.classes[0]
            for key in self.classes:
                if max_ < keys_res[key]:
                    max_ = keys_res[key]
                    predict = key
            predicts.append(predict)
        return predicts

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        v_len = len(X_test)
        predicts = self.predict(X_test)
        same_results = 0
        for i,target in enumerate(predicts):
            if target == y_test[i]:
                same_results+=1
        return same_results / v_len
