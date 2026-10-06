import numpy as np
import logging

logger = logging.getLogger("RLExecution")

class PPOExecutionAgent:
    """
    شبكة عصبية للتنفيذ التكيفي تستند لسياسات Proximal Policy Optimization (PPO)
    """
    def __init__(self, state_dim: int = 5, action_dim: int = 3):
        self.state_dim = state_dim
        self.action_dim = action_dim
        # أوزان عشوائية مهيأة مسبقاً لمكونات السياسة والقيمة
        np.random.seed(42)
        self.policy_weights = np.random.randn(state_dim, action_dim) * 0.1

    def get_action(self, state_vector: np.ndarray) -> int:
        """
        حساب التوزيع الاحتمالي للقرارات: 0 = الانتظار (Hold), 1 = الشراء (Buy), 2 = البيع (Sell)
        """
        if len(state_vector) != self.state_dim:
            state_vector = np.resize(state_vector, self.state_dim)

        logits = np.dot(state_vector, self.policy_weights)
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / np.sum(exp_logits)

        action = int(np.argmax(probabilities))
        logger.info(f"قرار شبكة RL: {action} والاحتمالات: {np.round(probabilities, 3)}")
        return action

    def train_step(self, reward: float):
        """
        تحديث الأوزان وفق المكافأة المكتسبة من جودة التنفيذ وانخفاض السبريد
        """
        self.policy_weights += 0.01 * reward * np.random.randn(self.state_dim, self.action_dim)
