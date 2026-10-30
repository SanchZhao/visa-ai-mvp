import os
import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="澳签材料助手",
    page_icon="🧾",
    layout="wide",
)

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def build_profile_summary(profile):
    return f"""
申请人信息：
- 姓名：{profile.get('name', '')}
- 国籍：{profile.get('nationality', '')}
- 签证类型：{profile.get('visa_type', '')}
- 申请目的：{profile.get('purpose', '')}
- 教育背景：{profile.get('education', '')}
- 工作经历：{profile.get('work_experience', '')}
- 资产/资金：{profile.get('funds', '')}
- 家庭情况：{profile.get('family', '')}
- 出行计划：{profile.get('travel_plan', '')}
- 备注：{profile.get('notes', '')}
"""

def generate_demo_text(profile):
    name = profile.get("name", "申请人")
    visa_type = profile.get("visa_type", "签证")
    purpose = profile.get("purpose", "旅行/学习/工作")
    education = profile.get("education", "")
    work = profile.get("work_experience", "")
    funds = profile.get("funds", "")
    family = profile.get("family", "")
    travel_plan = profile.get("travel_plan", "")

    return f"""
# {visa_type}材料说明草稿

## 1. 个人背景介绍
{name} 目前具备稳定的生活及职业背景，申请此类签证的目的是 {purpose}。在过去的学习和工作经历中，{name} 已展示出良好的职业素养和责任感。{education} {work}

## 2. 申请目的说明
申请此签证的主要目的是{purpose}。在申请过程中，{name} 提供了真实、完整的材料，以证明其赴澳目的符合相关规定，并且具有合理安排。{travel_plan}

## 3. 资金与生活保障说明
在资金方面，{name} 提供了有关财务能力的支持材料，显示其具备覆盖相关期间生活及返程所需的资金条件。相关支持材料包括：{funds}。这体现了申请人在澳大利亚期间能够保持稳定安排的能力。

## 4. 家庭与社会联系说明
{family}

## 5. 材料完整性说明
申请材料已按要求准备，内容真实、完整、连贯，能够充分展示申请人的背景、目的及符合签证要求的条件。建议在提交前进行细致检查，并准备相应的补充材料以增强整体说服力。

## 6. 建议的补充材料
- 身份证明文件
- 学历/工作证明
- 财务证明文件
- 旅行计划说明
- 相关支持材料扫描件

以上内容仅为文书初稿，建议由申请人根据实际材料进行人工审核与调整。
"""

def generate_ai_text(profile):
    client = get_client()
    if not client:
        return generate_demo_text(profile)

    prompt = f"""
你是专业的澳大利亚签证材料文书辅助助手。请基于以下申请人信息，写一段清晰、专业、适合签证材料使用的说明文稿。请保持真实、简洁、逻辑清晰，适合人工审核后再润色。

申请人信息：
{build_profile_summary(profile)}

要求：
1. 语气专业、真实、简洁
2. 可用于签证材料说明
3. 不要编造事实
4. 结构清晰，可以分段
5. 适合后续转为正式文书
"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "你是专业的澳大利亚签证材料文书助手。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1200,
    )

    return response.choices[0].message.content

def build_material_checklist(profile):
    required = {
        "身份证明": "护照、身份证等",
        "学历证明": "学历证书、成绩单、在读证明等",
        "工作经历证明": "工作证明、职位说明、工资证明等",
        "资金证明": "银行流水、存款证明、资产证明等",
        "旅行计划": "行程安排、访问说明等",
        "居住安排": "住宿证明、接待安排等",
        "其他补充材料": "个人经历说明、支持信等",
    }

    missing = []
    for key in required:
        if not profile.get(key.lower().replace(" ", "_"), ""):
            missing.append(key)

    return required, missing

st.title("澳签材料助手 MVP")
st.caption("适合从 0 到 1 逐步做一个 AI 辅助签证材料管理工具")

with st.form("profile_form"):
    col1, col2 = st.columns(2)

    with col1:
        visa_type = st.selectbox("签证类型", ["旅游签", "学生签", "工作签", "其他"])
        name = st.text_input("姓名")
        nationality = st.text_input("国籍")
        purpose = st.text_input("申请目的")
        education = st.text_area("教育背景")
        work_experience = st.text_area("工作经历")
        funds = st.text_area("资金/资产说明")

    with col2:
        family = st.text_area("家庭情况")
        travel_plan = st.text_area("旅行计划 / 赴澳目的")
        notes = st.text_area("备注")
        submit = st.form_submit_button("生成文书草稿")

if submit:
    profile = {
        "name": name,
        "nationality": nationality,
        "visa_type": visa_type,
        "purpose": purpose,
        "education": education,
        "work_experience": work_experience,
        "funds": funds,
        "family": family,
        "travel_plan": travel_plan,
        "notes": notes,
    }

    st.success("已生成材料说明草稿")

    with st.spinner("正在生成文书..."):
        draft = generate_ai_text(profile)

    st.subheader("文书草稿")
    st.write(draft)

    st.subheader("资料完整性检查")
    required, missing = build_material_checklist(profile)
    for key, value in required.items():
        if key in missing:
            st.warning(f"缺少：{key}（建议准备：{value}）")
        else:
            st.success(f"已准备：{key}（{value}）")

    st.download_button(
        label="下载 Markdown",
        data=draft,
        file_name=f"{name or 'visa_material'}_draft.md",
        mime="text/markdown",
    )

st.sidebar.header("使用说明")
st.sidebar.write("""
1. 填写申请人资料
2. 点击“生成文书草稿”
3. 审核 AI 生成结果
4. 根据实际情况补充材料
5. 导出为 Markdown
""")

st.sidebar.markdown("""
### 下一步扩展方向
- 新增表格式资料收集
- 多种签证模板
- 自动生成材料清单
- 导出 Word / PDF
- 加入 AI 审稿和改写
- 接入数据库保存历史记录
""")
