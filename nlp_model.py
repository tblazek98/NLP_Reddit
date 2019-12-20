def clean(posts, math_op, string=False):
    import math
    from nltk.corpus import stopwords

    stopwords_eng = set(stopwords.words('english'))
    cleaned = []
    for i,line in enumerate(posts):
        title = line[0].split(" ")
        text = line[1].split(" ")
        for stopword in stopwords_eng:
            while True:
                try:
                    title.remove(stopword)
                except ValueError:
                    break
                try:
                    text.remove(stopword)
                except ValueError:
                    break
        if string:
            return " ".join(title)
        time = (line[2] // 3600 % 24) + (line[2] // 60 % 60)/60 + (line[2] % 60)/3600

        if math_op == "bins":
            cleaned.append((" ".join(title), " ".join(text), time, int(round(math.log(int(line[-1]),10),0))))
        else:
            cleaned.append((" ".join(title), " ".join(text), time, math.log(int(line[-1]),10)))
    return cleaned

class SklearnModel(object):
    def __init__(self, train, test, model="LinearRegression", text=False):
        from nltk.corpus import stopwords
        from collections import Counter
        from random import uniform
        from sklearn import linear_model, svm
        from sklearn.neural_network import MLPRegressor

        if model == "Ridge":
            self.classifier = linear_model.Ridge()
        elif model == "Lasso":
            self.classifier = linear_model.Lasso()
        elif model == "SVM":
            self.classifier = svm.SVR(gamma='scale')
        elif model == "MLP":
            self.classifier = MLPRegressor(solver='lbfgs')
        else:
            self.classifier = linear_model.LinearRegression()

        self.train_posts = clean(train, "log")
        self.test_posts = clean(test, "log")
        self.text = text

    def make_model(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn import linear_model, svm
        from sklearn.pipeline import FeatureUnion
        import numpy as np
        import pandas as pd
        import scipy.sparse

        titles = []
        scores = []
        both = []
        texts = []
        times = []
        for line in self.train_posts:
            titles.append(line[0])
            texts.append(line[1])
            both.append(line[0] + line[1])
            times.append(line[2])
            scores.append(line[-1])

        if not self.text:
            vectorizer = TfidfVectorizer(ngram_range=(1,3))
            X = vectorizer.fit_transform(titles)
        else:
            vectorizer = TfidfVectorizer(ngram_range=(1,3))

            X = vectorizer.fit_transform(titles)
        self.vectorizer = vectorizer
        self.classifier.fit(X, scores)

    def predict_model(self, test_string=None):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn import linear_model, svm
        import numpy as np
        import pandas as pd
        import scipy.sparse

        if test_string is None:
            titles = []
            texts = []
            both = []
            times = []
            self.scores = []
            for line in self.train_posts:
                titles.append(line[0])
                texts.append(line[1])
                both.append(line[0] + line[1])
                times.append(line[2])
                self.scores.append(line[-1])

            if not self.text:
                vectorizer = TfidfVectorizer(ngram_range=(1,3))
                X = vectorizer.fit_transform(both)
            else:
                vectorizer = TfidfVectorizer(ngram_range=(1,3))
                X = vectorizer.fit_transform(titles)
            self.results = self.classifier.predict(X)
            percent = []
            for predicted,actual in zip(self.results,self.scores):
                percent.append(float((abs(predicted-actual))/actual))
            return 100*sum(percent)/len(percent)
        else:
            cleaned = clean([[test_string,""]], "logs", string=True)
            from scipy.sparse import hstack
            vectorizer = TfidfVectorizer(ngram_range=(1,3))
            try:
                X = self.vectorizer.transform([cleaned])
            except ValueError as e:
                raise ValueError("Test string was not complex enough")
            results = self.classifier.predict(X)
            return results[0]



    def get_r2_score(self):
        from sklearn.metrics import r2_score
        return r2_score(self.results, self.scores)

    def get_mean_squared_error(self):
        from sklearn.metrics import mean_squared_error
        return mean_squared_error(self.results, self.scores)



class AverageScoreModel(object):
    def __init__(self, train, test):
        from nltk.corpus import stopwords
        from collections import Counter
        from random import uniform

        self.train_posts = clean(train, "log")
        self.test_posts = clean(test, "log")

    def make_model(self):
        self.words = {}
        for post in self.train_posts:
            words = post[0]
            value = post[-1]
            for word in words:
                tmp = self.words.get(word,False)
                if tmp == False:
                    self.words[word] = [value]
                else:
                    tmp.append(value)
                    self.words[word] = tmp
        self.counts = {}
        for word,values in self.words.items():
            self.counts[word] = sum(values)/len(values)

    def predict_model(self):
        percent = []
        self.results = []
        self.scores = []
        for title, text, time, value in self.test_posts:
            test_average = []
            title = title.split(" ")
            for word in title:
                val = self.counts.get(word, False)
                if val!=False:
                    test_average.append(val)
            if len(test_average) == 0:
                continue
            avg = sum(test_average)/len(test_average)
            self.results.append(avg)
            self.scores.append(value)
            percent.append(abs(avg-value)/value)
        if len(percent)==0:
            raise RuntimeError
        return 100*sum(percent)/len(percent)

    def get_r2_score(self):
        from sklearn.metrics import r2_score
        return r2_score(self.results, self.scores)

    def get_mean_squared_error(self):
        from sklearn.metrics import mean_squared_error
        return mean_squared_error(self.results, self.scores)

class Baseline(object):
    def __init__(self, lines):
        from nltk.corpus import stopwords
        from collections import Counter
        from random import uniform

        self.train_posts = clean(lines, "bins")

    def get_posts(self):
        return self.posts

    def make_model(self):
        self.words = {}
        for post in self.train_posts:
            words = post[0].split(" ")
            text = post[1]
            value = post[-1]
            for word in words:
                tmp = self.words.get(word,False)
                if tmp == False:
                    self.words[word] = [value]
                else:
                    tmp.append(value)
                    self.words[word] = tmp
        self.counts = {}
        for word,values in self.words.items():
            self.counts[word] = sum(values)/len(values)

    def predict_model(self, test):
        self.test_posts = clean(test, "bins")
        percent = []
        for title, text, time, value in self.test_posts:
            test_average = []
            title = title.split(" ")
            for word in title:
                val = self.counts.get(word, False)
                if val!=False:
                    test_average.append(val)
            if len(test_average) == 0:
                continue
            avg = int(round(sum(test_average)/len(test_average),0))
            if avg == value:
                percent.append(1)
            else:
                percent.append(0)
        if len(percent)==0:
            raise RuntimeError
        return 100*sum(percent)/len(percent)
