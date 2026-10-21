from typing import Any

from app.domain.state import DialogueState
from app.task.runner.models.base import Action, ActionResult
from app.infra import http_util
from app.conf.config import settings
from app.domain.messages import BotMessage

class LookupOrderStatusAction(Action):
    """查询订单状态"""

    name = "action_lookup_order_status"

    async def run(self, state: DialogueState, args: dict[str, Any]) -> ActionResult:
        # 从任务上下文获取order_number
        assert state.active_task is not None
        order_number = state.active_task.slots.get("order_number")
        # 调用API获取order status
        assert http_util.http_client is not None
        response = await http_util.http_client.get(f"{settings.commerce_api_base_url}/orders/{order_number}/status")
        response_data = response.json()
        print(response_data)
        if response_data.get("code") == 0:
            data = response_data.get("data")
            return ActionResult(
                slot_updates={
                    "order_status": data.get("status"),
                    "order_summary": data.get("status_desc")
                }
            )
        else:
            return ActionResult(
                slot_updates={
                    "order_status": "未知",
                    "order_summary": "未知"
                }
            )

class LookupLogisticsAction(Action):
    """查询订单物流"""

    name = "action_lookup_logistics"

    async def run(self, state: DialogueState, args: dict[str, Any]) -> ActionResult:
        assert state.active_task is not None
        order_number = state.active_task.slots.get("order_number")

        try:
            assert http_util.http_client is not None
            response = await http_util.http_client.get(f"{settings.commerce_api_base_url}/orders/{order_number}/logistics")
        except Exception:
            response = None
        if response is not None:
            response_json = response.json()
            if response_json.get("code") == 0:
                response_data = response_json.get("data")
                return ActionResult(
                    slot_updates={
                        "logistics_company":response_data.get("logistics_company") or "未知",
                        "tracking_number": response_data.get("tracking_number") or "未知",
                        "logistics_status": response_data.get("status_desc") or "未知"
                    }
                )
            else:
                return ActionResult(
                    slot_updates={
                        "logistics_company": "未知",
                        "tracking_number": "未知",
                        "logistics_status": "未知"
                    }
                )
        else:
            return ActionResult(
                slot_updates={
                    "logistics_company": "未知",
                    "tracking_number": "未知",
                    "logistics_status": "未知"
                }
            )
            
class SubmitRefundRequestAction(Action):
    """提交退款申请"""

    name = "action_submit_refund_request"

    async def run(self, state: DialogueState, args: dict[str, Any]) -> ActionResult:
        assert state.active_task is not None
        order_number = state.active_task.slots.get("order_number")
        refund_reason = state.active_task.slots.get("refund_reason")

        # 2.调用业务后端创建退款申请
        url = f"{settings.commerce_api_base_url.rstrip('/')}/orders/{order_number}/refund-applications"
        try:
            assert http_util.http_client is not None
            response = await http_util.http_client.post(url, json={"reason": refund_reason or "", "submitted_by": "system"})
            result = response.json()
        except Exception:
            return ActionResult(slot_updates={
                "refund_status": "退款申请提交失败，请稍后再试。",
            })

        # 3.根据返回结果设置退款状态
        if not isinstance(result, dict):
            return ActionResult(slot_updates={
                "refund_status": "退款申请提交失败，请稍后再试。",
            })

        if result.get("code") == 0:
            return ActionResult(slot_updates={
                "refund_status": "退款申请已提交，后续会尽快为你处理。",
            })

        return ActionResult(slot_updates={
            "refund_status": result.get("message") or "退款申请提交失败，请稍后再试。",
        })

class RecommendSimilarProductsAction(Action):
    """相似商品推荐"""

    name = "action_recommend_similar_products"

    async def run(self, state: DialogueState, args: dict[str, Any]) -> ActionResult:
        assert state.active_task is not None
        product_id = state.active_task.slots.get("product_id")
        label = product_id or "这件商品"

        assert http_util.http_client is not None
        response = await http_util.http_client.get(f"{settings.commerce_api_base_url}/products/{product_id}")
        if response:
            payload = response.json().get("data")
        else:
            payload = None

        if payload:
            label = str(payload.get("title") or "").strip() or label

        text = (
            f"我已经收到你对\"{label}\"的相似商品推荐需求。"
            "不过当前版本还没有接入正式的推荐系统，稍后可以继续补上这部分能力。"
        )
        return ActionResult(messages=[BotMessage(text=text)])

if __name__ == '__main__':
    # 补全测试
    import asyncio

    from app.domain.contexts import TaskContext

    async def test():
        http_util.init_http_client()
        try:
            state = DialogueState(sender_id="u1001")
            state.active_task = TaskContext(
                flow_id="refund_request",
                step_id="refund_submitted",
                slots={
                    "order_number": "A20260410001",
                    "refund_reason": "商品存在质量问题，申请退款",
                },
            )
            action = SubmitRefundRequestAction()
            result = await action.run(state, {})
            print("退款申请提交结果:", result.slot_updates)
        finally:
            await http_util.close_http_client()

    asyncio.run(test())