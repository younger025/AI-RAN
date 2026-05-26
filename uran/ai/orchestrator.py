from uran.ai.intent_agent import IntentAgent
from uran.ai.environment_agent import EnvironmentAgent
from uran.ai.module_selection_agent import ModuleSelectionAgent
from uran.ai.parameter_gen_agent import ParameterGenAgent
from uran.ai.critic_agent import CriticAgent
from uran.ai.intent_schema import IntentSpec, EnvironmentSpec
from uran.ai.plan_schema import PlanSpec


class AIOrchestrator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.intent_agent = IntentAgent()
        self.environment_agent = EnvironmentAgent()
        self.module_agent = ModuleSelectionAgent()
        self.param_agent = ParameterGenAgent()
        self.critic_agent = CriticAgent()

    def generate_plan(self, raw_intent: str, environment: EnvironmentSpec = None):
        intent = self.intent_agent.run(raw_intent)

        env = self.environment_agent.run(intent, environment)

        module_selection = self.module_agent.run(intent, env)

        candidate_plans = self.param_agent.run(intent, module_selection)

        candidate_plans = self.critic_agent.run(intent, candidate_plans)

        trace = []
        trace.extend(self.intent_agent.get_trace())
        trace.extend(self.environment_agent.get_trace())
        trace.extend(self.module_agent.get_trace())
        trace.extend(self.param_agent.get_trace())
        trace.extend(self.critic_agent.get_trace())

        return {
            "intent": intent,
            "environment": env,
            "candidate_plans": candidate_plans,
            "trace": trace,
        }