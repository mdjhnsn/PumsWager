state = "AK"
puma = "Subsistence Alaska"
data = db.lab.find({"LOCATION": puma})
df = pd.DataFrame(data).drop(columns="_id")
data = df.to_dict("records")

group_col = "SCHOOLING"
plot_val = "SALARY"
fig, ax = plt.subplots()
for grp in dfs[group_col].unique():
    subset = dfs[dfs[group_col] == grp]
    ax = sns.kdeplot(
        subset[plot_val].clip(upper=100000), **dict(shade=True, label=grp, alpha=0.1)
    )

fig, ax = plt.subplots()
corr = dfs[features].corr()
mask = np.zeros_like(corr)
mask[np.tril_indices_from(mask)] = True
sns.heatmap(
    corr,
    fmt=".1f",
    vmin=-1,
    vmax=1,
    center=0,
    annot=True,
    ax=ax,
    cmap="RdBu_r",
    mask=mask,
)

# shap.plots.decision(explainer.expected_value, shap_value_i, features=X)

# make a standard partial dependence plot
sample_ind = 420
for col in ["HOURS", "SCHL", "AGE", "INDP", "OCCP"]:
    fig, ax = shap.partial_dependence_plot(
        col,
        xgr.predict,
        X,
        model_expected_value=True,
        feature_expected_value=True,
        show=False,
        ice=False,
        shap_values=shap_values[sample_ind : sample_ind + 1, :],
        shap_value_features=X.iloc[sample_ind : sample_ind + 1, :],
    )
    fig.show()
    fig, ax = shap.plots.scatter(shap_values[:, col], color=shap_values)
    fig.show()

    @app.callback(Output("sample-data", "children"), [Input("store", "data")])
    def get_sample_df(data):
        keep_cols = [
            "STATE",
            "LOCATION",
            "FIELD",
            "OCCUPATION",
            "SECTOR",
            "INDUSTRY",
            "SCHOOLING",
            "AGE",
            "HOURS",
            "SALARY",
            "WGHT",
        ]
        df = pd.DataFrame(data)[keep_cols].sample(1).melt()
        return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


import pandas as pd
import shap
import sklearn
import xgboost as xgb
from pymongo import MongoClient
from sklearn.model_selection import train_test_split

state = "AK"
puma = "Anchorage Municipality (North)"
client = MongoClient("mongodb://localhost:27017/")
db = client.pums18
data = pd.DataFrame(list(db.lab.find({"LOCATION": puma})))

df = pd.DataFrame(data)
sum_weights = df["WGHT"].sum()
sample_size = min(sum_weights, 500000)
dfs = df.sample(sample_size, weights=df["WGHT"], replace=True)
features = [
    "AGE",
    "SCHL",
    "INDP",
    "OCCP",
    "HOURS",
]
target = "SALARY"

shap.plots.beeswarm(shap_values)

X_i = ...
shap_value_i = explainer(X_i)
shap.plots.waterfall(shap_value_i)
