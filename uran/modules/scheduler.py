from uran.modules.base import CommunicationModule


class SchedulerModule(CommunicationModule):
    def __init__(self, scheduler_type: str):
        super().__init__(
            module_id=f"sched_{scheduler_type}",
            name=f"Scheduler {scheduler_type.replace('_', ' ').title()}",
            module_type="scheduler",
        )
        self.scheduler_type = scheduler_type

    def process(self, context):
        context["scheduler"] = self.scheduler_type
        return context