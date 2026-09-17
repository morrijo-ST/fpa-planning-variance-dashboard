import random
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="FP&A Planning & Variance",layout="wide")
st.title("FP&A Planning & Variance Dashboard")
st.caption("Synthetic budget, actual, rolling forecast, variance drivers, and executive commentary.")
random.seed(13)
months=pd.date_range("2026-01-01",periods=12,freq="MS")
deps=["Sales","R&D","G&A","Customer Success"]
rows=[]
for m in months:
    for d in deps:
        budget=random.uniform(450000,1800000)
        actual=budget*random.uniform(.88,1.14)
        forecast=actual*random.uniform(.97,1.08)
        rows.append([m,d,budget,actual,forecast])
df=pd.DataFrame(rows,columns=["month","department","budget","actual","forecast"])
df["variance"]=df.actual-df.budget
df["variance_pct"]=df.variance/df.budget

depsel=st.sidebar.multiselect("Department",deps,default=deps)
scenario=st.sidebar.slider("Forecast scenario adjustment",-0.10,0.10,0.00,0.01)
f=df[df.department.isin(depsel)].copy()
f["scenario_forecast"]=f.forecast*(1+scenario)

c1,c2,c3,c4=st.columns(4)
c1.metric("Budget",f"${f.budget.sum()/1e6:,.1f}M")
c2.metric("Actual",f"${f.actual.sum()/1e6:,.1f}M",f"{f.variance.sum()/1e6:+.1f}M vs budget")
c3.metric("Rolling Forecast",f"${f.scenario_forecast.sum()/1e6:,.1f}M")
c4.metric("Variance %",f"{f.variance.sum()/f.budget.sum():+.1%}")

monthly=f.groupby("month",as_index=False)[["budget","actual","scenario_forecast"]].sum()
st.subheader("Monthly plan vs actual vs forecast")
st.plotly_chart(px.line(monthly,x="month",y=["budget","actual","scenario_forecast"],markers=True),use_container_width=True)

bydep=f.groupby("department",as_index=False).agg(budget=("budget","sum"),actual=("actual","sum"),variance=("variance","sum"))
bydep["status"]=bydep.variance.apply(lambda x:"Unfavorable" if x>0 else "Favorable")
st.subheader("Department variance")
st.plotly_chart(px.bar(bydep,x="department",y="variance",color="status"),use_container_width=True)

worst=bydep.sort_values("variance",ascending=False).iloc[0]
best=bydep.sort_values("variance").iloc[0]
st.subheader("Executive commentary")
st.info(f"Largest unfavorable cost variance: {worst.department} at ${worst.variance/1e6:+.2f}M. Largest favorable variance: {best.department} at ${best.variance/1e6:+.2f}M. Scenario adjustment is {scenario:+.0%}, producing a rolling forecast of ${f.scenario_forecast.sum()/1e6:,.1f}M.")

st.dataframe(f.sort_values(["month","department"]),use_container_width=True,hide_index=True)
