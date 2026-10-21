from pathlib import Path

import yaml

from app.task.flow.models import Flow, FlowList, FlowSlot
from app.task.flow.steps import CollectFlowStep


class FlowLoader:

    def load_many(self, paths: list[Path]) -> FlowList:
        slots = {}
        flows = []

        for path in paths:
            res = self.load(path)
            slots.update(res.slots)
            flows.extend(res.flows)

        return FlowList(
            slots=slots,
            flows=flows
        )

    def load(self, path: Path) -> FlowList:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

            data_slots = data.get("slots", {})
            slots = self._load_slots(data_slots)
            data_flows = data.get("flows", {})
            flows = self._load_flows(data_flows, slots)

            return FlowList(
                slots=slots,
                flows=flows    
            )

    def _load_slots(self, data_slots: dict) -> dict[str, FlowSlot]:
        slots = {}
        for slot_name, slot_val in data_slots.items():
            slots[slot_name] = FlowSlot(name=slot_name, **slot_val)

        return slots

    def _load_flows(self, data_flows: dict, slots: dict[str, FlowSlot]) -> list[Flow]:
        flows = []
        for flow_name, flow_val in data_flows.items():
            flow_val["id"] = flow_name
            flow = Flow.from_dict(flow_val)

            # 从slots中取出当前flow中为CollectFlowStep类型的step所对应的槽信息
            flow.slots = [slots.get(step.slot_name) for step in flow.steps if isinstance(step, CollectFlowStep)] # type: ignore
            flows.append(flow)

        return flows

if __name__ == '__main__':
    flow_path1 = Path(__file__).parents[3]/'flow_config'/'user_flows.yaml'
    flow_path2 = Path(__file__).parents[3]/'flow_config'/'system_flows.yaml'
    loader = FlowLoader()
    flows_list:FlowList = loader.load_many([flow_path1,flow_path2])
    print(len(flows_list.slots))