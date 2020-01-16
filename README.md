# Gathering data
To gather the data, run `python3 get_reddit_posts.py`. This will automatically update the appropriate posts in `reddit_posts_18.csv` and add any new posts to the watch. This was run
on a server every 10 minutes to continuously track data.

# Splitting into training and testing
Run `python3 split_data.py` to split the data into subreddits and into testing and training data. The current ratio is 90% into training and 10% into testing.

This split data gets placed in the `data/` directory.

# Running the models
Run `python3 get_reddit_posts --model` to run the metrics for the performance of the various models. These models can be found in `nlp_model.py`.

# Testing out your own post titles
Run `python3 get_reddit_posts -practice MODEL` to try out your own post title. It will return the associated score it would receive

# See breakdown by hour
In testing which hour was important for gathering the data, I ran `python3 gather_post_hourly.py`, which gave an hourly breakdown of the number of upvotes.