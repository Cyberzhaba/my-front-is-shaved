import requests


class Request():

    def __init__(self):


        # tests
        self.test_user = {'user_id': 123,
                         'owned_tokens': [123, 345],
                         'buying_tokens': [234, 453],
                          'seed_fraze':["пошел", "нахуй", "пидорас", "я", "тебя", "ненавижу", "сука", "ты", "ебаная", "ебаный", "ты", "сапог"]}

    def get_user(self, user_id):
        return self.test_user

    def create_user(self, user_id):
        return False

    def get_history(self, user_id):
        return ["kakoyto", "spisok", "istorii", "tranzaciy"]