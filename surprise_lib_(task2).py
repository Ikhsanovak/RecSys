import io
from surprise import KNNBaseline
from surprise import Dataset
from surprise import get_dataset_dir
from collections import defaultdict


def read_item_names():
    file_name = get_dataset_dir() + '/ml-100k/ml-100k/u.item'
    rid_to_name = {}
    with io.open(file_name, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            line = line.split('|')
            rid_to_name[line[0]] = (line[1], line[2])
    return rid_to_name


def get_top_n(predictions, n=5):
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, round(est, 3)))
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
    return top_n


user_id = input('User ID: ')

data = Dataset.load_builtin('ml-100k')
trainset = data.build_full_trainset()
sim_options = {'name': 'cosine', 'user_based': True, 'min_support': 5}
algo = KNNBaseline(k=4, sim_options=sim_options)
algo.fit(trainset)

testset = trainset.build_anti_testset()
testset = filter(lambda x: x[0] == user_id, testset)
predictions = algo.test(testset)

top_n = get_top_n(predictions)
rid_to_name = read_item_names()

print('User ' + user_id)
for movie_rid, rating in top_n[user_id]:
    print('{:4s} {:70s} {}'.format(movie_rid, str(rid_to_name[movie_rid]), rating))
