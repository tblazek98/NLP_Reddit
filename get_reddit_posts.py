import csv
import json
from tempfile import NamedTemporaryFile
import datetime
import shutil
import requests
import time
import argparse
from nlp_model import Baseline
import math
DELIMITER = ","
QUOTECHAR = '"'
LINETERMINATOR = "\n"

def calculate_weight(upvotes,awards):
    try:
        return int(math.log(upvotes + (awards*1000)))
    except:
        return -1

class RedditParser(object):
    def __init__(self, subreddit, filename):
        self.subreddit = subreddit
        self.filename = filename
        self.test_filename = "TEST_" + filename
        self.URL = "http://reddit.com/r/"+subreddit
        self.headers = {'user-agent': 'reddit-tblazek'}
        self.posts = {}
        with open(self.filename, 'r') as f:
            data = csv.reader(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
            for i,line in enumerate(data):
                if i==0:
                    self.csv_header = line
                    continue
                if line[0] == subreddit:
                    self.posts[line[2]] = line


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
            if (now - datetime.datetime.utcfromtimestamp(created)).seconds > (60*60*8) + (20*60):
                continue
            post_id = info['id']
            title = info['title'].replace("\n","")
            text = info['selftext'].replace("\n","")
            url = info['url']
            score = ""
            awards = ""
            tmp = [self.subreddit,created,post_id,title,text,url,score,awards,'False']

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
            print(diff, diff.seconds > (60*60*8), diff.seconds < (60*60*8)+(20*60))
            if value[-1]=="False" and diff.seconds > (60*60*8) and diff.seconds < (60*60*8)+(20*60):
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
                self.posts[key][6] = new_score
                self.posts[key][7] = awards
                self.posts[key][-1] = 'True'
        tempfile = NamedTemporaryFile(mode='w', delete=False)
        with open(self.filename, 'r') as csvfile, tempfile:
            reader = csv.DictReader(csvfile, delimiter=DELIMITER, quotechar=QUOTECHAR, fieldnames=self.csv_header)
            writer = csv.DictWriter(tempfile, delimiter=DELIMITER, quotechar=QUOTECHAR, fieldnames=self.csv_header)

            for row in reader:
                if row['id'] in self.posts:
                    row['score'] = self.posts[row['id']][6]
                    row['awards'] = self.posts[row['id']][7]
                    row['updated'] = self.posts[row['id']][-1]
                row = {'id':row['id'], 'subreddit':row['subreddit'], 'created':row['created'], 'title':row['title'], 'text':row['text'], 'score':row['score'], 'url':row['url'], 'awards':row['awards'], 'updated':row['updated']}
                writer.writerow(row)

        shutil.move(tempfile.name, self.filename)

    def proper_posts(self):
        look = {}
        texts = {}
        for key, value in self.posts.items():
            if value[-1] == "True":
                score = calculate_weight(int(value[6]),int(value[7]))
                tmp = [value[3], value[4], score]
                # Check that it has at least 1 upvote or 1 award
                if score > 0:
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
            list_posts.append(value)
        return list_posts


if __name__=="__main__":
    subreddits = ["dadjokes", "todayilearned","askreddit"]
    FILENAME = "reddit_posts.csv"
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', dest='model', action='store_const', const=1, default=0, help='Run the NLP model based off previously gathered data')
    args = parser.parse_args()
    if not args.model:
        for subreddit in subreddits:
            r = RedditParser(subreddit, FILENAME)
            r.get_posts()
            r.update_posts()
        print("[{}] Finished running all subreddits".format(datetime.datetime.now()))
    else:
        all_posts = []
        print("============The baseline performance metrics============")
        for subreddit in subreddits:
            r = RedditParser(subreddit, FILENAME)
            investigate = r.proper_posts()
            all_posts += investigate
            b = Baseline(investigate)
            b.make_model()
            print("r/"+subreddit)
            print("\tAccuracy: " + str(round(b.predict_model(),2)) + "%")
            print("\tSample Size: " + str(len(investigate)))
        b = Baseline(all_posts)
        b.make_model()
        print("Combined Subreddits")
        print("\tAccuracy: " + str(round(b.predict_model(),2)) + "%")
        print("\tSample Size: " + str(len(all_posts)))
