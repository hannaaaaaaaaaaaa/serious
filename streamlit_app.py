import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="함수인가요?", page_icon="🧮")

st.title("🧮 함수인가요?")
st.write("관계식을 입력하고, 이 식이 **함수인지 아닌지** 그래프를 통해 확인해보세요. ")
st.write("곱하기는 * 로 거듭제곱은 ** 로 입력해야 컴퓨터가 이해해요")

st.markdown("예시: `y = x + 2`, `y = x**2`, `x = y**2`, `y = ±x`")

# ----- 예시 버튼 -----
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("y = x + 2"):
        st.session_state["expr"] = "y = x + 2"
with col2:
    if st.button("y = x**2"):
        st.session_state["expr"] = "y = x**2"
with col3:
    if st.button("x = y**2 "):
        st.session_state["expr"] = "x = y**2"

col4, col5 = st.columns(2)
with col4:
    if st.button("y = ±x "):
        st.session_state["expr"] = "y = ±x"


# ----- 식 입력 -----
expr = st.text_input(
    "관계식을 입력하세요",
    value=st.session_state.get("expr", "y = x + 2")
)

# 범위 설정
x_min, x_max = st.slider("x 값 범위", -100, 100, (-20, 20))
y_min, y_max = st.slider("y 값 범위", -100, 100, (-50, 50))

check_btn = st.button("함수인가요?")

# ------------------ 유틸 함수 ------------------
def relation_type(expression: str):
    exp = expression.replace(" ", "").lower()
    if exp.startswith("y="):
        return "y_form"
    elif exp.startswith("x="):
        return "x_form"
    else:
        return "unknown"

def is_function(expression: str):
    exp = expression.replace(" ", "").lower()
    if exp.startswith("y=") and "±" not in exp:
        return True
    return False

def eval_relation(expr: str, x_range, y_range) -> pd.DataFrame:
    exp = expr.replace(" ", "")
    r_type = relation_type(exp)
    points = []

    try:
        if r_type == "y_form":
            right = exp.split("=", 1)[1]
            # ± 처리
            if "±" in right:
                right_plus = right.replace("±", "+")
                right_minus = right.replace("±", "-")
                for x in x_range:
                    try:
                        y1 = eval(right_plus)
                        points.append((x, y1))
                    except Exception:
                        pass
                    try:
                        y2 = eval(right_minus)
                        points.append((x, y2))
                    except Exception:
                        pass
            else:
                for x in x_range:
                    try:
                        y = eval(right)
                        points.append((x, y))
                    except Exception:
                        pass

        elif r_type == "x_form":
            right = exp.split("=", 1)[1]
            for y in y_range:
                try:
                    x = eval(right)
                    points.append((x, y))
                except Exception:
                    pass
        else:
            return pd.DataFrame(columns=["x", "y"])
    except Exception:
        return pd.DataFrame(columns=["x", "y"])

    df = pd.DataFrame(points, columns=["x", "y"])
    return df.dropna()

# ------------------ 본동작 ------------------
if check_btn:
    # 1) 함수 여부
    if is_function(expr):
        st.success("✅ 함수입니다 ")
    else:
        st.error("❌ 함수가 아닙니다")
        st.info("→ 어떤 x에서는 y가 여러 개 생기거나, y가 x로 정해지지 않는 형태일 수 있어요.")

    # 2) 점+선 그래프
    xs = np.linspace(x_min, x_max, 200)
    ys = np.linspace(y_min, y_max, 200)
    df = eval_relation(expr, xs, ys)

    if len(df) > 0:
        st.write("📈 관계식의 그래프")

        base = alt.Chart(df).encode(
            x=alt.X("x:Q", scale=alt.Scale(domain=(x_min, x_max))),
            y=alt.Y("y:Q", scale=alt.Scale(domain=(y_min, y_max)))
        )

        points = base.mark_point(size=40, opacity=0.6)
        line = base.mark_line(strokeWidth=2, opacity=0.7)

        chart = (points + line).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("식을 계산할 수 없었어요. (예: y = x + 2, x = y**2 등)")
        
st.divider()
st.caption("※ 수업용 단순화 버전입니다. 중등 수준의 함수/비함수 비교 시각화용입니다.")
