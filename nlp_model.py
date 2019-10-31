class Baseline(object):
    def __init__(self, lines, ratio=0.8):
        from nltk.corpus import stopwords
        from collections import Counter
        from random import uniform
        try:
            float(ratio)
        except:
            raise ValueError
        if ratio > 1 or ratio < 0:
            raise ValueError

        self.train_posts = []
        self.test_posts = []
        self.stopwords = set(stopwords.words('english'))
        for i,line in enumerate(lines):
            title = line[0].split(" ")
            rand_val = uniform(0,1)
            for stopword in self.stopwords:
                while True:
                    try:
                        title.remove(stopword)
                    except ValueError:
                        break
            if rand_val <= ratio:
                self.train_posts.append((title, line[-1]))
            else:
                self.test_posts.append((title, line[-1]))

    def get_posts(self):
        return self.posts

    def make_model(self):
        self.words = {}
        for post in self.train_posts:
            words = post[0]
            value = post[1]
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
        for title, value in self.test_posts:
            test_average = []
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
