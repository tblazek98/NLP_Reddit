import csv
import json
from tempfile import NamedTemporaryFile
import datetime
import shutil
import requests
import time
import argparse
from nlp_model import Baseline, AverageScoreModel, SklearnModel
import math
DELIMITER = ","
QUOTECHAR = '"'
DATA_DIRECTORY = "data/"
LINETERMINATOR = "\n"

def calculate_weight(upvotes,awards,multiplier):
    try:
        return upvotes + (awards*multiplier)
    except:
        return -1

class RedditParser(object):
    def __init__(self, subreddit, directory, model=False):
        self.subreddit = subreddit
        if model:
            self.filename = directory + subreddit + "_train.csv"
            self.test_filename = directory + subreddit + "_test.csv"
        else:
            self.filename = directory
        self.data_directory = directory
        self.URL = "http://reddit.com/r/"+subreddit
        self.headers = {'user-agent': 'reddit-tblazek'}
        self.model = model
        self.care = 'score_10'
        self.hour_index = 0
        self.posts = {}
        self.test_posts = {}
        self.upvotes = 0
        self.awards = 0
        self.multiplier = 0
        if not model:
            with open(self.filename, 'r') as f:
                data = csv.reader(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
                for i,line in enumerate(data):
                    if i==0:
                        self.csv_header = line
                        self.hour_index = self.csv_header.index(self.care)
                        continue
                    if line[0] == subreddit:
                        self.posts[line[2]] = line
        else:
            files = {self.filename: self.posts, self.test_filename: self.test_posts}
            for file, posts in files.items():
                with open(file) as f:
                    data = csv.reader(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
                    for i,line in enumerate(data):
                        if i==0:
                            self.csv_header = line
                            self.hour_index = self.csv_header.index(self.care)
                            continue
                        if line[0] == subreddit or subreddit=="all":
                            posts[line[2]] = line

    def get_posts(self):
        try:
            reddit_response = requests.get(self.URL+"/new.json?limit=100",headers=self.headers)
            data = json.loads(reddit_response.text)
        except Exception as e:
            print("Exception occurred while scrapping Reddit data")
            print(e)
            return
        now = datetime.datetime.utcnow()
        writing = []
        for item in data['data']['children']:
            # This contains the reddit posts
            info = item['data']
            if info['id'] in self.posts:
                continue
            created = info['created_utc']
            if (now - datetime.datetime.utcfromtimestamp(created)).seconds > (60*60*2) + (20*60):
                continue
            post_id = info['id']
            title = info['title'].replace("\n","")
            text = info['selftext'].replace("\n","")
            url = info['url']
            score = ""
            awards = ""
            tmp = [self.subreddit,created,post_id,title,text,url,score,awards,"","","","","","","","","","","","","","","","",'False']

            writing.append(tmp)
        with open(self.filename,'a') as f:
            writer = csv.writer(f, delimiter=DELIMITER, quotechar=QUOTECHAR,quoting=csv.QUOTE_MINIMAL)
            for tmp in writing:
                # print(tmp)
                self.posts[tmp[2]] = tmp
                writer.writerow(tmp)

    def update_posts(self):
        now = datetime.datetime.utcnow()
        writing = []
        for key, value in self.posts.items():
            diff = now - datetime.datetime.utcfromtimestamp(float(value[1]))
            if value[-1]=="False" and diff.seconds > (60*60*2) and diff.seconds < (60*60*18)+(20*60):
                update_url = "https://reddit.com/by_id/t3_" + key + ".json"
                try:
                    reddit_response = requests.get(update_url,headers=self.headers)
                    reddit_data = json.loads(reddit_response.text)
                except Exception as e:
                    print(e)
                    print("ERROR IN GETTING POST INFORMATION")
                    continue

                post_data = reddit_data['data']['children'][0]['data']
                new_score = post_data['score']
                awards = post_data['total_awards_received']

                if diff.seconds > (60*60*2) and diff.seconds < (60*60*2) + (20*60):
                    self.posts[key][8] = new_score
                    self.posts[key][9] = awards
                elif diff.seconds > (60*60*4) and diff.seconds < (60*60*4) + (20*60):
                    self.posts[key][10] = new_score
                    self.posts[key][11] = awards
                elif diff.seconds > (60*60*6) and diff.seconds < (60*60*6) + (20*60):
                    self.posts[key][12] = new_score
                    self.posts[key][13] = awards
                elif diff.seconds > (60*60*8) and diff.seconds < (60*60*8)+ (20*60):
                    self.posts[key][6] = new_score
                    self.posts[key][7] = awards
                elif diff.seconds > (60*60*10) and diff.seconds < (60*60*10) + (20*60):
                    self.posts[key][14] = new_score
                    self.posts[key][15] = awards
                elif diff.seconds > (60*60*12) and diff.seconds < (60*60*12) + (20*60):
                    self.posts[key][16] = new_score
                    self.posts[key][17] = awards
                elif diff.seconds > (60*60*14) and diff.seconds < (60*60*14) + (20*60):
                    self.posts[key][18] = new_score
                    self.posts[key][19] = awards
                elif diff.seconds > (60*60*16) and diff.seconds < (60*60*16) + (20*60):
                    self.posts[key][20] = new_score
                    self.posts[key][21] = awards
                elif diff.seconds > (60*60*18) and diff.seconds < (60*60*18) + (20*60):
                    self.posts[key][22] = new_score
                    self.posts[key][23] = awards
                    self.posts[key][-1] = 'True'
                else:
                    continue
        tempfile = NamedTemporaryFile(mode='w', delete=False)
        with open(self.filename, 'r') as csvfile, tempfile:
            reader = csv.DictReader(csvfile, delimiter=DELIMITER, quotechar=QUOTECHAR, fieldnames=self.csv_header)
            writer = csv.DictWriter(tempfile, delimiter=DELIMITER, quotechar=QUOTECHAR, fieldnames=self.csv_header)

            for row in reader:
                if row['id'] in self.posts:
                    row['score'] = self.posts[row['id']][6]
                    row['awards'] = self.posts[row['id']][7]
                    row['score_2'] = self.posts[row['id']][8]
                    row['awards_2'] = self.posts[row['id']][9]
                    row['score_4'] = self.posts[row['id']][10]
                    row['awards_4'] = self.posts[row['id']][11]
                    row['score_6'] = self.posts[row['id']][12]
                    row['awards_6'] = self.posts[row['id']][13]
                    row['score_10'] = self.posts[row['id']][14]
                    row['awards_10'] = self.posts[row['id']][15]
                    row['score_12'] = self.posts[row['id']][16]
                    row['awards_12'] = self.posts[row['id']][17]
                    row['score_14'] = self.posts[row['id']][18]
                    row['awards_14'] = self.posts[row['id']][19]
                    row['score_16'] = self.posts[row['id']][20]
                    row['awards_16'] = self.posts[row['id']][21]
                    row['score_18'] = self.posts[row['id']][22]
                    row['awards_18'] = self.posts[row['id']][23]
                    row['updated'] = self.posts[row['id']][-1]
                row = {'id':row['id'], 'subreddit':row['subreddit'], 'created':row['created'], 'title':row['title'], 'text':row['text'], 'score':row['score'], 'url':row['url'], 'awards':row['awards'], 'score_2': row['score_2'], 'awards_2': row['awards_2'], 'score_4': row['score_4'], 'awards_4': row['awards_4'], 'score_6': row['score_6'], 'awards_6': row['awards_6'], 'score_10': row['score_10'], 'awards_10': row['awards_10'], 'score_12':row['score_12'], 'score_14': row['score_14'], 'awards_12': row['awards_12'], 'awards_14': row['awards_14'], 'score_16': row['score_16'], 'awards_16':row['awards_16'], 'score_18': row['score_18'], 'awards_18': row['awards_18'],'updated':row['updated']}
                writer.writerow(row)

        shutil.move(tempfile.name, self.filename)

    def proper_posts(self, posts):
        look = {}
        texts = {}
        for key, value in posts.items():
            if value[-1] == "True" and value[self.hour_index] != "":
                score = int(value[self.hour_index]) + int(value[self.hour_index+1])
                tmp = [value[3], value[4], int(float(value[1])), int(value[self.hour_index]), int(value[self.hour_index+1])]
                # Check that it has at least 2 upvotes or 1 award (this is because each post automatically gets 1)
                if score > 2:
                    # Check for duplicates, if duplicate then we take the highest score
                    combined = tmp[0] + tmp[1]
                    if combined in texts:
                        if texts[combined][0] > score:
                            continue
                        else:
                            # Remove duplicate
                            look.pop(texts[combined][-1], None)
                            texts[combined] = (score,key)
                    else:
                        look[key] = tmp
                        texts[combined] = (score,key)
        list_posts = []
        for key, value in look.items():
            self.upvotes += int(value[2])
            self.awards += int(value[3])
            list_posts.append(value)
        try:
            self.multiplier = float(self.upvotes / self.awards)
        except:
            self.multiplier = 1
        output = []
        for thing in list_posts:
            tmp = thing[:3] + [calculate_weight(thing[3],thing[4], self.multiplier)]
            if tmp[-1] > 0 and 'http://' not in tmp[0] and 'https://' not in tmp[0]:
                output.append(tmp)
        return output


if __name__=="__main__":
    subreddits = ["dadjokes", "todayilearned","askreddit", "showerthoughts","Combined"]
    sklearn_models = ["LinearRegression", "Ridge", "Lasso","SVM", "MLP"]
    FILENAME = "reddit_posts_18.csv"
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', dest='model', action='store_const', const=1, default=0, help='Run the NLP model based off previously gathered data')
    parser.add_argument('-practice', dest='practice_model', action='store', type=str, default=None, help='Test out your own post titles! Options include Linear, Ridge, Lasso, SVM, MLP, average')
    args = parser.parse_args()
    if args.practice_model is not None:
        if args.practice_model not in sklearn_models and args.practice_model != "Average":
            raise ValueError("Not a valid model")
        tmp = ""
        for subreddit in subreddits:
            tmp += subreddit + ", "
        tmp += "all"
        sub = ""
        while sub not in subreddits and sub != "all":
            sub = input("Choose a subreddit between " + tmp + " to practice on: ")

        print("\nCreating the model...")
        r = RedditParser(sub, DATA_DIRECTORY, model=True)
        investigate = r.proper_posts(r.posts)
        test_posts = r.proper_posts(r.test_posts)
        mod = None
        if sub == "Average":
            mod = AverageScoreModel(investigate, test_posts)
        else:
            mod = SklearnModel(investigate, test_posts, model=args.practice_model, text=True)
        mod.make_model()
        while True:
            title = input("Type our your post or type 'quit' to leave: ")
            if title == "quit":
                break
            import math
            print(int(math.exp(mod.predict_model(test_string=title))))
            print("")

    elif not args.model:
        for subreddit in subreddits:
            r = RedditParser(subreddit, FILENAME, model=False)
            r.get_posts()
            r.update_posts()
        print("[{}] Finished running all subreddits".format(datetime.datetime.now()))
    else:
        print("============The baseline performance metrics============")
        tables = []
        sample_size = []

        for subreddit in subreddits:
            table = [["Model", "Average Percent Error", "Mean Squared Error"]]
            if subreddit != "Combined":
                r = RedditParser(subreddit, DATA_DIRECTORY, model=True)
                # This gets rid of duplicate posts and that it has more than 1 upvote
                investigate = r.proper_posts(r.posts)
                print("r/"+subreddit)
            else:
                r = RedditParser("all", DATA_DIRECTORY, model=True)
                investigate = r.proper_posts(r.posts)
                print("Combined Subreddits")

            sample_size.append(len(investigate))
            test_posts = r.proper_posts(r.test_posts)

            b = Baseline(investigate)
            b.make_model()
            print("\tBaseline Bins Model")
            print("\tAccuracy: " + str(round(b.predict_model(test_posts),2)) + "%\n")
            a = AverageScoreModel(investigate, test_posts)
            a.make_model()
            table.append(["Average Score Model", round(a.predict_model(),2), round(a.get_mean_squared_error(),6)])

            for lin_model in sklearn_models:
                l = SklearnModel(investigate, test_posts, model=lin_model, text=True)
                l.make_model()
                error = round(l.predict_model(),2)
                mse = round(l.get_mean_squared_error(),6)
                r2 = round(l.get_r2_score(),6)
                table.append([lin_model, error, mse])
            tables.append(table)
        subreddits.append("Combined Subreddits")
        for i, table in enumerate(tables):
            print("r/" + subreddits[i] + ": ")
            print("Sample Size: " + str(sample_size[i]))
            for line in table:
                print(line)
