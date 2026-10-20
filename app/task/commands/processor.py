from app.domain.contexts import CanceledSystemContext, InterruptedSystemContext, ResumedSystemContext, StartedSystemContext, TaskContext
from app.domain.state import DialogueState
from app.task.commands.models import CancelFlowCommand, Command, ResumeFlowCommand, SetSlotsCommand, StartFlowCommand
from app.task.flow.models import FlowList


class CommandProcessor:

    def run(self, commands: list[Command], state: DialogueState, flows: FlowList):
        for command in commands:
            if isinstance(command, StartFlowCommand):
                self._start_cmd_handle(command, state, flows)
            elif isinstance(command, CancelFlowCommand):
                self._cancel_cmd_handle(state, flows)
            elif isinstance(command, ResumeFlowCommand):
                self._resume_cmd_handle(command, state, flows)
            elif isinstance(command, SetSlotsCommand): 
                self._setslots_cmd_handle(command, state)

    def _start_cmd_handle(self, command: StartFlowCommand, state: DialogueState, flows: FlowList) -> None:
        # 获取要启动的任务
        target_task_id = command.flow
        target_flow = flows.get_flow_by_id(target_task_id)
        # 取消系统任务
        state.stop_sys_task()
        # 判断当前是否有任务在执行
        cur_task = state.active_task
        if cur_task:
            # 当前有任务在执行，挂起
            state.interrupt_current_task()
            # 将要启动的任务添加到state
            state.start_task(
                TaskContext(
                    flow_id=target_task_id,
                    step_id=target_flow.get_start_step().id,
                )
            )
            # 开启interred系统任务
            state.start_sys_task(
                InterruptedSystemContext(
                    flow_id="system_task_interrupted",
                    step_id=flows.get_flow_by_id("system_task_interrupted").get_start_step().id,
                    interrupted_flow_id=cur_task.flow_id,
                    interrupted_flow_name=flows.get_flow_by_id(cur_task.flow_id).name,
                    started_flow_id=target_task_id,
                    started_step_name=target_flow.name
                )
            )
        else:
            # 当前没有任务在执行，直接启动任务
            state.start_task(
                TaskContext(
                    flow_id=target_task_id,
                    step_id=target_flow.get_start_step().id,
                )
            )
            # 启动started系统任务
            state.start_sys_task(
                StartedSystemContext(
                    flow_id="system_task_started",
                    step_id=flows.get_flow_by_id("system_task_started").get_start_step().id,
                    start_flow_id=target_task_id,
                    start_flow_name=target_flow.name
                )
            )

    def _cancel_cmd_handle(self, state: DialogueState, flows: FlowList) -> None:
        # 获取当前任务
        cur_task = state.active_task
        # 取消当前的任务
        state.stop_cur_task()
        # 启动canceled系统任务
        assert cur_task
        state.start_sys_task(
            CanceledSystemContext(
                flow_id="system_task_canceled",
                step_id=flows.get_flow_by_id("system_task_canceled").get_start_step().id,
                canceled_flow_id=cur_task.flow_id,
                canceled_flow_name=flows.get_flow_by_id(cur_task.flow_id).name
            )
        )

    def _resume_cmd_handle(self, command: ResumeFlowCommand, state: DialogueState, flows: FlowList) -> None:
        # 获取要恢复的任务
        target_task_id = command.flow
        target_flow = flows.get_flow_by_id(target_task_id)
        # 取消系统任务
        state.stop_sys_task()
        # 判断当前是否有任务在执行
        cur_task = state.active_task
        if cur_task:
            # 当前有任务在执行，挂起
            state.interrupt_current_task()
            # 将要恢复的任务添加到state
            state.resume_task(target_task_id)
            # 开启interrupted系统任务
            state.start_sys_task(
                InterruptedSystemContext(
                    flow_id="system_task_interrupted",
                    step_id=flows.get_flow_by_id("system_task_interrupted").get_start_step().id,
                    interrupted_flow_id=cur_task.flow_id,
                    interrupted_flow_name=flows.get_flow_by_id(cur_task.flow_id).name,
                    resumed_flow_id=target_task_id,
                    resumed_step_name=target_flow.name
                )
            )
        else:
            # 当前没有任务在执行，直接恢复任务
            state.resume_task(target_task_id)
            # 启动resumed系统任务
            state.start_sys_task(
                ResumedSystemContext(
                    flow_id="system_task_interrupted",
                    step_id=flows.get_flow_by_id("system_task_interrupted").get_start_step().id,
                    resumed_flow_id=target_task_id,
                    resumed_flow_name=target_flow.name
                )
            )

    def _setslots_cmd_handle(self, command: SetSlotsCommand, state: DialogueState) -> None:
        if command.solts:
            state.set_slots(command.solts)
