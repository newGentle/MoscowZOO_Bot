import redis


class SessionsCache:
    def __init__(self):
        self.conn = None

    def connect(self, host, port, password):
        self.conn = redis.StrictRedis(host=host,
                                      port=port,
                                      password=password,
                                      charset="utf-8",
                                      decode_responses=True
                                      )

    def check_session(self, user_id):
        if self.conn.get(user_id) is not None:
            return True
        else:
            return False

    def add_session(self, user_id, categories):
        self.conn.set(user_id, 0)
        self.conn.set(user_id + ".at_welcome", 0)
        for cat in categories:
            self.conn.set(user_id + "." + cat, 0)

    def get_question(self, user_id):
        return self.conn.get(user_id)

    def update_score(self, user_id, category, score):
        self.conn.incrby(user_id + "." + category, score)

    def delete_session(self, user_id, categories):
        self.conn.delete(user_id)
        for cat in categories:
            self.conn.delete(user_id + "." + cat)

    def get_scores(self, user_id, categories):
        scores = {}
        for cat in categories:
            scores[cat] = self.conn.get(user_id + "." + cat)
        return scores
