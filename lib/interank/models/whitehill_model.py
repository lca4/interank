"""Use TensorFlow to fit the model with only the skill-difficulty terms."""
import tensorflow as tf

from .model import TensorFlowModel


class WhitehillModel(TensorFlowModel):

    """Class to compute the baseline from Whitehill et al."""

    def __init__(self, *, n_users, n_articles, global_bias=False):
        self._with_global_bias = global_bias
        # Parameters.
        self._skill = tf.Variable(tf.ones([n_users]), name="skill")
        self._difficulty = tf.Variable(tf.ones([n_articles]),
                                       name="difficulty")
        # L2 losses (for regularization purposes).
        self._l2_skill = tf.nn.l2_loss(self._skill)
        self._l2_difficulty = tf.nn.l2_loss(self._difficulty)
        super().__init__(n_users=n_users, n_articles=n_articles)

    def _logit_model(self, user_id, article_id):
        logit = (tf.gather(self._skill, self._user_id)
                 * tf.gather(tf.exp(self._difficulty), self._article_id))
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
    def l2_skill(self):
        return self._l2_skill

    @property
    def l2_difficulty(self):
        return self._l2_difficulty
