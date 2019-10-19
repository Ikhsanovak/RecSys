import json

from recommend import open_csv_file
from recommend import RecommendationForUser

data = "data/data.csv"
context_day = "data/context_day.csv"
context_place = "data/context_place.csv"

users_rates = open_csv_file(data)
users_days_of_week = open_csv_file(context_day)
users_places = open_csv_file(context_place)

user_name = "User 3"
recommendation_for_user = RecommendationForUser(user_name=user_name,
                                       users_rates=users_rates,
                                       users_days_of_week=users_days_of_week,
                                       users_places=users_places)

result = {
    "User": user_name,
    "1": recommendation_for_user.set_rates(),
    "2": recommendation_for_user.recommendation()
}

with open(user_name + '.json', 'w') as outfile:
    json.dump(obj=result, fp=outfile, indent=4)
