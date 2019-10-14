import csv
import json
from tempfile import NamedTemporaryFile
import datetime
import shutil
import requests
import time
DELIMITER = ","
QUOTECHAR = '"'
LINETERMINATOR = "\n"

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
            if now - datetime.datetime.utcfromtimestamp(created) > datetime.timedelta(hours=8):
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
            if value[-1]=="False" and diff > datetime.timedelta(hours=8) and diff < datetime.timedelta(hours=8, minutes=20):
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


if __name__=="__main__":
    subreddits = ["dadjokes", "todayilearned","askreddit"]
    FILENAME = "reddit_posts.csv"
    for subreddit in subreddits:
        r = RedditParser(subreddit, FILENAME)
        r.get_posts()
        r.update_posts()

