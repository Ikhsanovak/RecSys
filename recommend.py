import csv
import numpy


def open_csv_file(csv_file_name: str):  # открытие файла
    result = dict()
    with open(csv_file_name) as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # т.к. в наших csv файлах есть заголовки, не записываем их в результат
        lines = list(reader)
    for line in lines:
        values = list()
        for value in line[1:len(line)]:
            values.append(value)
        result[line[0]] = values
    return result


class RecommendationForUser:
    def __init__(self, user_name: str, users_rates: dict, users_days_of_week: dict, users_places: dict):
        super().__init__()

        self.users_rates = users_rates
        self.users_days_of_week = users_days_of_week
        self.users_places = users_places
        self.kNN = 4

        self.user_name = user_name
        self.user_rate = self.get_user_rates()
        self.user_average_rate = self.get_average_user_rate(self.user_rate)
        self.similarity = self.get_similarity_with_users()

    # список оценок пользователя
    def get_user_rates(self) -> list:
        current_user_rates = list()
        for user_name, user_rates in self.users_rates.items():
            if user_name == self.user_name:
                current_user_rates = user_rates
                break
        return current_user_rates

    # средняя оценка пользователя
    @staticmethod
    def get_average_user_rate(user_film_rates: list) -> float:
        avg = 0.0
        count = 0
        for user_film_rate in user_film_rates:
            if int(user_film_rate) != -1:
                avg += int(user_film_rate)
                count += 1
        return avg / count

    # метрика косинуса (формула из задания)
    @staticmethod
    def similarity_metric(user1_film_rates: list, user2_film_rates: list) -> float:
        sumUV = 0
        sumU2 = 0
        sumV2 = 0
        for i in range(len(user1_film_rates)):
            user1_rate = user1_film_rates[i]
            user2_rate = user2_film_rates[i]
            if int(user1_rate) != -1 and int(user2_rate) != -1:
                sumUV += int(user1_rate) * int(user2_rate)
                sumU2 += int(user1_rate) * int(user1_rate)
                sumV2 += int(user2_rate) * int(user2_rate)
        metric = sumUV / (numpy.sqrt(sumV2) * numpy.sqrt(sumU2))
        return metric

    # сходство данного пользователя со всеми остальными пользователями
    def get_similarity_with_users(self) -> dict:
        similarity = dict()
        for user_name, user_rates in self.users_rates.items():
            if user_name != self.user_name:
                similarity[user_name] = self.similarity_metric(self.user_rate, user_rates)
        return similarity

    # получение пользователей, наиболее похожих на данного
    def get_close_users(self, n: int, film_number: int) -> list:
        similarity_with_all_users = list(self.similarity.items())
        similarity_with_all_users.sort(key=lambda value: value[1], reverse=True)
        close_users = list()
        i = 0
        while i < n:
            user_name = similarity_with_all_users[i][0]
            rates = self.users_rates[user_name]
            if int(rates[film_number]) != -1:
                close_users.append(user_name)
            i += 1
        return close_users

    # расчет оценки для конкретного фильма (по формуле в задании)
    def set_rate_for_film(self, film_number: int) -> float:
        numerator = 0.0
        denominator = 0.0
        close_users = self.get_close_users(self.kNN, film_number)
        for user_name, user_rates in self.users_rates.items():
            if user_name in close_users:
                avg_rate = RecommendationForUser.get_average_user_rate(user_rates)
                rate = user_rates[film_number]
                numerator += self.similarity[user_name] * (int(rate) - avg_rate)
                denominator += numpy.abs(self.similarity[user_name])
        if denominator != 0:
            rate = self.user_average_rate + (numerator / denominator)
            return numpy.round(rate, 3)
        else:
            return -1

    # оценки для всех фильмов
    def set_rates(self) -> dict:
        rates = dict()
        for film_number in range(len(self.user_rate)):
            film_rate = self.user_rate[film_number]
            if int(film_rate) == -1:
                rates["Movie " + str(film_number)] = self.set_rate_for_film(film_number)
        return rates

    # рекомендация фильма для пользователя дома в выходные
    # идея аналогична первому заданию, только берутся те фильмы, которые не были просмотрены данным пользователем и
    # были просмотрены в выходные дни дома другими пользователями
    def recommendation(self):
        recommendation_list = dict()
        recommendation_movie = dict()
        for user_name, user_rates in self.users_rates.items():
            if user_name != self.user_name:
                for film_number in range(len(user_rates)):
                    if self.conditions_for_suitable_film(user_name, film_number):
                        recommendation_rate = float(self.similarity[user_name]) * int(user_rates[film_number])
                        if film_number not in recommendation_list.keys() or recommendation_list[film_number] < recommendation_rate:
                            recommendation_list[film_number] = recommendation_rate
        sorted_recommendations = list(recommendation_list.items())
        sorted_recommendations.sort(key=lambda value: value[1], reverse=True)
        recommendation_movie["Movie " + str(sorted_recommendations[0][0] + 1)] = round(sorted_recommendations[0][1], 3)
        return recommendation_movie

    # проверка условий, подходит ли фильм для рекомендации
    def conditions_for_suitable_film(self, user_name, film_number):
        was_watched = int(self.user_rate[film_number]) == -1
        watched_at_weekend = (self.users_days_of_week[user_name][film_number].strip() == "Sat") or \
                             (self.users_days_of_week[user_name][film_number].strip() == "Sun")
        watched_at_home = self.users_places[user_name][film_number].strip() == "h"
        if was_watched and watched_at_weekend and watched_at_home:
            return True
        else:
            return False

