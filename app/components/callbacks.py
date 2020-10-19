import time

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.tools as tls
import matplotlib.pyplot as plt
import shap
import xgboost as xgb
from dash.dependencies import Input, Output, State
from sklearn.model_selection import train_test_split

from app.components.utils import db


def register_callbacks(app):
    @app.callback(Output("puma", "options"), Input("state", "value"))
    def get_pumas(state):
        data = db.loc.find({"STATE": state})
        df = pd.DataFrame(list(data))
        pumas = list(df.LOCATION.values)
        return [{"label": puma, "value": puma} for puma in pumas]

    @app.callback(Output("store", "data"), [Input("puma", "value")])
    def get_model_df(puma):
        data = db.lab.find({"LOCATION": puma})
        df = pd.DataFrame(data).drop(columns="_id")
        return df.to_dict("records")

    @app.callback(Output("salary-graph-title", "children"), [Input("puma", "value")])
    def get_salary_graph_title(puma):
        return f"{puma}"

    @app.callback(Output("salary-graph", "figure"), [Input("store", "data")])
    def get_salary_graph(data):
        return px.scatter(
            data,
            x="AGE",
            y="SALARY",
            color="HOURS",
            size="WGHT",
            hover_name="OCCUPATION",
            hover_data=["FIELD", "SECTOR", "INDUSTRY", "SCHOOLING"],
            template="simple_white",
        )

    @app.callback(Output("industry", "options"), [Input("sector", "value")])
    def get_industries(sector):
        data = db.ind.find({"SECTOR": sector})
        df = pd.DataFrame(list(data))
        industries = list(df.INDUSTRY.values)
        return [{"label": industry, "value": industry} for industry in industries]

    @app.callback(Output("occupation", "options"), [Input("field", "value")])
    def get_occupations(field):
        data = db.occ.find({"FIELD": field})
        df = pd.DataFrame(list(data))
        occupations = list(df.OCCUPATION.values)
        return [
            {"label": occupation, "value": occupation} for occupation in occupations
        ]

    @app.callback(
        [
            Output("model-alert", "children"),
            Output("model-graph", "figure"),
        ],
        [Input("store", "data"), State("go-button", "n_clicks")],
    )
    def query_and_train(data, n_clicks):
        print(n_clicks)
        t0 = time.time()
        df = pd.DataFrame(data)

        # Data setup
        features = [
            "OCCP",
            "INDP",
            "AGE",
            "HOURS",
            "SCHL",
            "COW",
        ]
        target = "SALARY"
        weight = "WGHT"
        sum_weights = df[weight].sum()
        sample_size = min(sum_weights, 500000)
        dfs = df.sample(sample_size, weights=df[weight], replace=True)
        X = pd.get_dummies(dfs[features], drop_first=True)
        y = dfs[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

        # Model Training
        model = xgb.XGBRegressor()
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)],
        )
        explainer = shap.explainers.Tree(model)

        X_shap = pd.DataFrame(explainer(X_test).values, columns=[col + "_CONTRIBUTION" for col in X.columns])
        X_shap['SALARY_BASE'] = explainer.expected_value
        X_shap['SALARY_PREDICTION'] = model.predict(X_test)
        df_test = dfs.iloc[X_test.index].reset_index(drop=True)
        df_out = pd.concat([df_test, X_shap], axis=1)
        df_out['RESIDUAL'] = df_out['SALARY_PREDICTION'] - df_out['SALARY']

        fig = px.scatter(
            df_out.to_dict('records'),
            x="SALARY_PREDICTION",
            y="RESIDUAL",
            template="simple_white",
        )

        t1 = time.time()
        exec_time = t1 - t0
        query_size = dfs.shape[0]

        alert_msg = f"Queried {query_size} records.\nTotal time: {exec_time:.2f}s."
        alert = dbc.Alert(alert_msg, color="light", dismissable=True)
        return alert, fig

    @app.callback(Output("state", "value"), [Input("state", "options")])
    def set_state(available_options):
        return available_options[0]["value"]

    @app.callback(Output("puma", "value"), [Input("puma", "options")])
    def set_puma(available_options):
        return available_options[0]["value"]

    @app.callback(Output("schooling", "value"), [Input("schooling", "options")])
    def set_schooling(available_options):
        return available_options[0]["value"]

    @app.callback(Output("sector", "value"), [Input("sector", "options")])
    def set_sector(available_options):
        return available_options[0]["value"]

    @app.callback(Output("field", "value"), [Input("field", "options")])
    def set_field(available_options):
        return available_options[0]["value"]

    @app.callback(Output("occupation", "value"), [Input("occupation", "options")])
    def set_occupation(available_options):
        return available_options[0]["value"]

    @app.callback(Output("industry", "value"), [Input("industry", "options")])
    def set_industry(available_options):
        return available_options[0]["value"]
