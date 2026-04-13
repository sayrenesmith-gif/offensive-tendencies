import streamlit as st
import pandas as pd

st.set_page_config(page_title="Football Tendencies", layout="wide")
st.title("Football Tendency Scout")
st.write("Upload your Excel file to chart offensive tendencies by formation, down, distance, hash, and play type.")

@st.cache_data
def load_workbook(file):
xl = pd.ExcelFile(file)
frames = []
for sh in xl.sheet_names:
df = pd.read_excel(file, sheet_name=sh)
df.columns = [str(c).strip() for c in df.columns]
df["sheet"] = sh
frames.append(df)
plays = pd.concat(frames, ignore_index=True)
for c in ["PLAY TYPE", "OFF FORM", "OFF PLAY", "OFF STR", "PLAY DIR", "HASH", "RESULT"]:
if c in plays.columns:
    plays[c] = plays[c].astype(str).str.strip().replace({"nan": "", "None": ""})
plays["is_run"] = plays["PLAY TYPE"].str.lower().eq("run")
plays["is_pass"] = plays["PLAY TYPE"].str.lower().eq("pass")
plays["dist_bucket"] = pd.cut(
pd.to_numeric(plays["DIST"], errors="coerce"),
bins=[-1, 3, 7, 100],
labels=["short", "medium", "long"]
)
return plays

uploaded = st.file_uploader("Upload Excel", type=["xlsx"])
if uploaded:
df = load_workbook(uploaded)

c1, c2, c3 = st.columns(3)
c1.metric("Plays", len(df))
c2.metric("Run plays", int(df["is_run"].sum()))
c3.metric("Pass plays", int(df["is_pass"].sum()))

st.subheader("Raw Data")
st.dataframe(df, use_container_width=True, height=350)

st.subheader("Formation Tendencies")
form = df[df["OFF FORM"].ne("")].groupby("OFF FORM").agg(
plays=("OFF FORM", "size"),
runs=("is_run", "sum"),
passes=("is_pass", "sum")
).reset_index()
form["run_pct"] = (form["runs"] / form["plays"] * 100).round(1)
form["pass_pct"] = (form["passes"] / form["plays"] * 100).round(1)
st.dataframe(form.sort_values("plays", ascending=False), use_container_width=True)

st.subheader("Down and Distance")
dd = df.groupby(["DN", "dist_bucket"]).agg(
plays=("PLAY #", "size"),
runs=("is_run", "sum"),
passes=("is_pass", "sum")
).reset_index()
dd["run_pct"] = (dd["runs"] / dd["plays"] * 100).round(1)
dd["pass_pct"] = (dd["passes"] / dd["plays"] * 100).round(1)
st.dataframe(dd.sort_values(["DN", "dist_bucket"]), use_container_width=True)

st.download_button(
"Download cleaned CSV",
df.to_csv(index=False).encode("utf-8"),
file_name="cleaned_plays.csv",
mime="text/csv"
)
