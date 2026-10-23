from app.domain.messages import BotMessage
from app.domain.state import DialogueState
from app.task.flow.links import ConditionalFlowLink, FLowLink
from app.task.flow.models import Flow, FlowList
from app.task.flow.steps import ActionFlowStep, CollectFlowStep, EndFlowStep, FlowStep, StartFlowStep
from app.task.runner.runner import ActionCall, ActionRunner
from app.task.runner.models.base import ActionResult
from app.domain.contexts import CollectSystemContext, ResumedSystemContext


class FlowExecuter:
    def __init__(self, runner: ActionRunner) -> None:
        self._runner = runner
    
    async def run(self, state: DialogueState, flows: FlowList) -> list[BotMessage]:
        messages: list[BotMessage] = []
        # 外层循环，调用内层循环执行action
        while True:
            # 内层循环，推进任务
            action_call: ActionCall = self._inner_loop(state, flows)
            # 如果action_call中是 action_listen，则停止外层循环，将messages返回
            if action_call.action_name == "action_listen":
                break
            # 如果不是 action_listen，则调用ActionRunner执行action
            action_result: ActionResult = await self._runner.run(state, action_call)
            # 保存action_result的结果
            messages.extend(action_result.messages)
            state.set_slots(action_result.slot_updates)

        return messages

    def _inner_loop(self, state: DialogueState, flows: FlowList) -> ActionCall:
        while True:
            cur_task = state.get_cur_task()
            # 如果当前state中没任务，则返回action_list终止循环
            if not cur_task:
                return ActionCall(action_name="action_listen")

            print(f"{cur_task.flow_id}----------------{cur_task.step_id}")

            # 当前state中有任务，推进任务
            # 获取当前任务的流程
            flow: Flow = flows.get_flow_by_id(cur_task.flow_id)
            # 获取当前任务的步骤
            step: FlowStep = flow.get_step_by_id(cur_task.step_id)
            # 根据不同的step进行处理
            if isinstance(step, StartFlowStep):
                self._run_start_step(state, step)
            elif isinstance(step, ActionFlowStep):
                call = self._run_action_step(state, step)
                return call
            elif isinstance(step, CollectFlowStep):
                call = self._run_collect_step(state, step, flows)
                if call:
                    return call
            elif isinstance(step, EndFlowStep):
                self._run_end_step(state, step)

    def _run_start_step(self, state: DialogueState, step: StartFlowStep):
        # 直接把流程推进一步
        next_step_id: str = self._get_next_step(state, step.next)
        state.get_cur_task().step_id = next_step_id # type: ignore

    def _run_action_step(self, state: DialogueState, step: ActionFlowStep) -> ActionCall:
        # 先把流程推进一步
        next_step_id: str = self._get_next_step(state, step.next)
        state.get_cur_task().step_id = next_step_id # type: ignore

        if isinstance(step.args, dict):
            # 返回ActionCall
            return ActionCall(
                action_name=step.action,
                action_kwargs=step.args
            )
        else:
            # 如果args是str，
            # 从args中取出配置属性的名称，从system_collect_information上下文获取此属性的值
            attr_name = step.args.split(".")[1]
            assert state.active_system_task is not None
            return ActionCall(
                action_name=step.action,
                action_kwargs=state.active_system_task.to_dict()[attr_name]
            )
            
    def _run_collect_step(self, state: DialogueState, step: CollectFlowStep, flows: FlowList) -> ActionCall | None:
        # 尝试填槽
        if state.focused_object:
            if step.slot_name == "order_number" and state.focused_object.type == "order":
                state.set_slots({"order_number": state.focused_object.id})
            if step.slot_name == "product_id" and state.focused_object.type == "product":
                state.set_slots({"product_id": state.focused_object.id})

        # 判断state中是否有当前需要的填槽数据
        assert state.active_task is not None
        if not state.active_task.slots.get(step.slot_name):
            # 没有数据，开启collect系统任务
            state.start_sys_task(
                CollectSystemContext(
                    flow_id="system_collect_information",
                    step_id=flows.get_flow_by_id("system_collect_information").get_start_step().id,
                    slot_name=step.slot_name,
                    response=step.response.to_dict()
                )
            )
        else:
            # 有数据，判断是否需要验证
            if not step.validation:
                # 不需要验证，流程推进一步
                next_step_id: str = self._get_next_step(state, step.next)
                state.get_cur_task().step_id = next_step_id # type: ignore
            else:
                # 需要验证
                globals_ = {"__builtins__": {}}
                locals_ = {
                    "slots": state.active_task.slots if state.active_task else {},
                    "context": state.active_system_task if state.active_system_task else {}
                }
                if not bool(eval(step.validation.condition, globals_, locals_)):
                    # 校验失败, 清空数据槽位
                    state.remove_slot(step.slot_name)
                    # 判断是否需要进行response
                    if step.validation.failure_response:
                        # 需要启动response任务，返回ActionCell
                        return ActionCall(
                            action_name="action_response",
                            action_kwargs=step.validation.failure_response.to_dict()
                        )
                else:
                    # 校验成功, 流程推进一步
                    next_step_id: str = self._get_next_step(state, step.next)
                    state.get_cur_task().step_id = next_step_id # type: ignore

    def _run_end_step(self, state: DialogueState, step: EndFlowStep):
        if state.active_system_task:
            state.stop_sys_task()
        else:
            state.stop_cur_task()

    def _get_next_step(self, state: DialogueState, links: list[FLowLink]) -> str: # type: ignore
        for link in links:
            if isinstance(link, ConditionalFlowLink):
                globals_ = {"__builtins__": {}}
                locals_ = {
                    "context": state.active_system_task if state.active_system_task else {},
                    "slots": state.active_task.slots if state.active_task else {}
                }
                # 判断条件是否成立
                # eval(expression, globals, locals)
                # expression : 要执行的表达式字符串
                # globals: 全局命名空间，一个包含变量的字典  {"__builtins__":{}}
                # locals: 局部命名空间  {context:{...},slots:{...}}
                if bool(eval(link.condition, globals_, locals_)):
                    # 条件成立
                    return link.target
            else:
                return link.target
