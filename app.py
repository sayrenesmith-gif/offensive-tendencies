st.subheader("Down and Distance")
dd = df.groupby(["DN", "dist_bucket"]).agg(
    plays=("PLAY #", "size"),
    runs=("is_run", "sum"),
    passes=("is_pass", "sum")
).reset
