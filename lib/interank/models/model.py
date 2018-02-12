import abc
import tensorflow as tf


class TensorFlowModel(metaclass=abc.ABCMeta):

    def __init__(self, *, n_users, n_articles):
        self._n_users = n_users
        self._n_articles = n_articles
        self._build_tf_graph()

    def _build_tf_graph(self):
        # Placeholders.
        self._user_id = tf.placeholder(
                tf.int32, shape=[None], name="user_id")
        self._article_id = tf.placeholder(
                tf.int32, shape=[None], name="article_id")
        self._quality = tf.placeholder(
                tf.float32, shape=[None], name="quality")

        logit = self._logit_model(self._user_id, self._article_id)
        self._probability = tf.nn.sigmoid(logit)

        cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(
                labels=self._quality, logits=logit)
        self._log_likelihood = tf.reduce_sum(
                -cross_entropy, name='log_likelihood')
        self._avg_log_loss = tf.reduce_mean(
                cross_entropy, name='avg_log_loss')

    @abc.abstractmethod
    def _logit_model(self, user_id, article_id):
        """Defines how the prediction is made."""

    @property
    def n_users(self):
        return self._n_users

    @property
    def n_articles(self):
        return self._n_articles

    @property
    def user_id(self):
        return self._user_id

    @property
    def article_id(self):
        return self._article_id

    @property
    def quality(self):
        return self._quality

    @property
    def probability(self):
        return self._probability

    @property
    def log_likelihood(self):
        return self._log_likelihood

    @property
    def avg_log_loss(self):
        return self._avg_log_loss
