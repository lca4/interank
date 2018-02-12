import tensorflow as tf

from .model import TensorFlowModel


class DotModel(TensorFlowModel):

    """Class for managing the dot model in TensorFlow."""

    def __init__(self, *, n_users, n_articles, n_dims, global_bias=False):
        self._with_global_bias = global_bias
        self._n_dims = n_dims
        # Parameters.
        self._skill = tf.Variable(tf.zeros([n_users]), name="skill")
        self._difficulty = tf.Variable(tf.zeros([n_articles]),
                name="difficulty")
        self._vec_user = tf.Variable(
                tf.random_uniform([n_users, n_dims],
                        minval=-1e-3, maxval=1e-3, seed=42),
                name="vec_user")
        self._vec_article = tf.Variable(
                tf.random_uniform([n_articles, n_dims],
                        minval=-1e-3, maxval=1e-3, seed=43),
                name="vec_article")
        # L2 losses (for regularization purposes).
        self._l2_skill = tf.nn.l2_loss(self._skill)
        self._l2_difficulty = tf.nn.l2_loss(self._difficulty)
        self._l2_vec_user = tf.nn.l2_loss(self._vec_user)
        self._l2_vec_article = tf.nn.l2_loss(self._vec_article)
        super().__init__(n_users=n_users, n_articles=n_articles)

    def _logit_model(self, user_id, article_id):
        dot_prod = tf.reduce_sum(tf.multiply(
                tf.gather(self._vec_user, user_id),
                tf.gather(self._vec_article, self._article_id)), 1)
        logit = (tf.gather(self._skill, self._user_id)
                - tf.gather(self._difficulty, self._article_id)
                + dot_prod)
        if self._with_global_bias:
            self._global_bias = tf.Variable(0., name="global_bias")
            return logit + self._global_bias
        else:
            self._global_bias = None
            return logit

    @property
    def skill(self):
        return self._skill

    @property
    def difficulty(self):
        return self._difficulty

    @property
    def global_bias(self):
        return self._global_bias

    @property
    def vec_user(self):
        return self._vec_user

    @property
    def vec_article(self):
        return self._vec_article

    @property
    def l2_skill(self):
        return self._l2_skill

    @property
    def l2_difficulty(self):
        return self._l2_difficulty

    @property
    def l2_vec_user(self):
        return self._l2_vec_user

    @property
    def l2_vec_article(self):
        return self._l2_vec_article
