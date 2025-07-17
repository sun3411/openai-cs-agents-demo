import os
from typing import Optional, Dict, Any
from pydantic import BaseModel
import random
from datetime import datetime

# =========================
# Azure OpenAI 配置
# =========================
from openai import AzureOpenAI

api_key = "VjNdZmvvqHVtRPsBp5rCVzDSLuH2m4b6ejonwrVbfWDgoOYpINMfJQQJ99BGACfhMk5XJ3w3AAAAACOGnBYB"
azure_endpoint = "https://15236-md3z6gpl-swedencentral.services.ai.azure.com/"
api_version = "2024-11-20"
llm_client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

# =========================
# 演示数据
# =========================
BILLS = [
    {"bill_id": "BILL-1001", "amount": 1200.50, "status": "已支付", "date": "2024-05-01", "desc": "办公用品采购"},
    {"bill_id": "BILL-1002", "amount": 3500.00, "status": "待支付", "date": "2024-05-10", "desc": "会议场地租赁"},
    {"bill_id": "BILL-1003", "amount": 800.00, "status": "已支付", "date": "2024-04-20", "desc": "交通费"},
]
INVOICES = [
    {"invoice_id": "INV-2001", "amount": 1200.50, "status": "已验真", "date": "2024-05-02", "desc": "办公用品采购发票"},
    {"invoice_id": "INV-2002", "amount": 3500.00, "status": "未验真", "date": "2024-05-11", "desc": "会议场地发票"},
]
REIMBURSEMENTS = [
    {"reimbursement_id": "REIM-3001", "amount": 500.00, "status": "已审核", "date": "2024-05-03", "desc": "差旅报销"},
    {"reimbursement_id": "REIM-3002", "amount": 1200.00, "status": "待审核", "date": "2024-05-12", "desc": "办公用品报销"},
]
BUDGETS = [
    {"subject": "市场部", "total": 100000, "used": 65000, "remain": 35000},
    {"subject": "研发部", "total": 200000, "used": 120000, "remain": 80000},
]

# =========================
# 上下文模型
# =========================
class FinanceContext(BaseModel):
    user_name: Optional[str] = None
    bill_id: Optional[str] = None
    invoice_id: Optional[str] = None
    reimbursement_id: Optional[str] = None
    budget_subject: Optional[str] = None
    last_agent: Optional[str] = None
    # 可扩展更多字段

# =========================
# Agent实现
# =========================

def bill_agent(user_input: str, ctx: FinanceContext) -> str:
    if "全部" in user_input or "所有" in user_input:
        return "\n".join([
            f"账单号: {b['bill_id']} 金额: {b['amount']} 状态: {b['status']} 日期: {b['date']} 描述: {b['desc']}" for b in BILLS
        ])
    for b in BILLS:
        if b["bill_id"] in user_input:
            return f"账单号: {b['bill_id']} 金额: {b['amount']} 状态: {b['status']} 日期: {b['date']} 描述: {b['desc']}"
    return "未找到相关账单。"

def invoice_agent(user_input: str, ctx: FinanceContext) -> str:
    for inv in INVOICES:
        if inv["invoice_id"] in user_input:
            return f"发票号: {inv['invoice_id']} 金额: {inv['amount']} 状态: {inv['status']} 日期: {inv['date']} 描述: {inv['desc']}"
    if "开票" in user_input:
        new_id = f"INV-{random.randint(3000,3999)}"
        INVOICES.append({"invoice_id": new_id, "amount": 1000.0, "status": "未验真", "date": datetime.now().strftime('%Y-%m-%d'), "desc": "用户开票"})
        return f"已成功开具发票，发票号: {new_id} 金额: 1000.0 描述: 用户开票"
    return "未找到相关发票。"

def reimbursement_agent(user_input: str, ctx: FinanceContext) -> str:
    for r in REIMBURSEMENTS:
        if r["reimbursement_id"] in user_input:
            r["status"] = "已审核"
            return f"报销单号: {r['reimbursement_id']} 金额: {r['amount']} 状态: {r['status']} 日期: {r['date']} 描述: {r['desc']}"
    return "未找到相关报销单。"

def budget_agent(user_input: str, ctx: FinanceContext) -> str:
    for b in BUDGETS:
        if b["subject"] in user_input:
            return f"科目: {b['subject']} 总预算: {b['total']} 已用: {b['used']} 剩余: {b['remain']}"
    return "未找到相关预算科目。"

def faq_agent(user_input: str, ctx: FinanceContext) -> str:
    q = user_input.lower()
    if "报销" in q:
        return "报销需提供发票、审批单等材料，具体流程请咨询财务部。"
    elif "发票" in q:
        return "发票需真实有效，抬头与公司名称一致。"
    elif "预算" in q:
        return "预算调整需部门负责人审批。"
    elif "账单" in q:
        return "账单可在系统内查询，支付状态实时更新。"
    return "很抱歉，暂时无法回答该问题。"

# =========================
# 分流Agent（意图识别）
# =========================

def triage_agent(user_input: str, ctx: FinanceContext) -> str:
    """简单规则分流，可后续用LLM增强"""
    if any(k in user_input for k in ["账单", "BILL-"]):
        ctx.last_agent = "账单Agent"
        return bill_agent(user_input, ctx)
    if any(k in user_input for k in ["发票", "开票", "验真", "INV-"]):
        ctx.last_agent = "发票Agent"
        return invoice_agent(user_input, ctx)
    if any(k in user_input for k in ["报销", "REIM-"]):
        ctx.last_agent = "报销Agent"
        return reimbursement_agent(user_input, ctx)
    if any(k in user_input for k in ["预算", "科目"]):
        ctx.last_agent = "预算Agent"
        return budget_agent(user_input, ctx)
    if any(k in user_input for k in ["FAQ", "常见问题", "政策"]):
        ctx.last_agent = "FAQ Agent"
        return faq_agent(user_input, ctx)
    # 默认尝试FAQ
    ctx.last_agent = "FAQ Agent"
    return faq_agent(user_input, ctx)

# =========================
# LLM调用（可选：复杂意图识别/守护规则）
# =========================

def call_azure_llm(messages, deployment_name: str) -> str:
    response = llm_client.chat.completions.create(
        model=deployment_name,  # Azure部署名
        messages=messages,
        temperature=0.2,
        max_tokens=512,
    )
    return response.choices[0].message.content

# =========================
# 对外统一接口
# =========================

def handle_user_message(user_input: str, ctx: FinanceContext) -> Dict[str, Any]:
    """主入口，分流到各Agent"""
    reply = triage_agent(user_input, ctx)
    return {
        "reply": reply,
        "context": ctx.dict(),
        "agent": ctx.last_agent or "分流Agent"
    }
