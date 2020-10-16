import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app.components.utils import get_fields, get_states, get_schooling, get_sectors

header = html.Div(
    [
        dbc.NavbarSimple(
            brand="PumsWager",
            brand_href="/",
            color="white",
            light=True,
        ),
    ],
)

about = dbc.Container(
    [
        html.H2("pums・wager"),
        html.H6("(noun)"),
        dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Span(
                                [
                                    "(1) a modern web application powered by ",
                                    html.Span(
                                        "PUMS",
                                        id="tooltip-target",
                                        style={
                                            "textDecoration": "underline",
                                            "cursor": "pointer",
                                        },
                                    ),
                                    html.P(),
                                    html.Span(
                                        "(2) a tool designed to explain and predict wage earnings"
                                    ),
                                ]
                            ),
                            dbc.Tooltip(
                                "Public-Use Microdata Samples from the US Census Bureau",
                                target="tooltip-target",
                            ),
                        ],
                    ),
                ),
            ],
        ),
    ],
)
state_puma_selector = dbc.CardBody(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("State", className="mr-2"),
                        dbc.Select(id="state", options=get_states()),
                    ],
                ),
                dbc.Col(
                    [
                        dbc.Label(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            "PUMA",
                                            id="tooltip-target2",
                                            style={
                                                "textDecoration": "underline",
                                                "cursor": "pointer",
                                            },
                                        ),
                                        dbc.Tooltip(
                                            "Public-Use Microdata Area",
                                            target="tooltip-target2",
                                        ),
                                    ],
                                ),
                            ],
                            className="mr-2",
                        ),
                        dbc.Select(id="puma"),
                    ],
                ),
            ],
        ),
    ]
)
model_inputs = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Field", className="mr-2"),
                            dbc.Select(id="field", options=get_fields()),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Occupation", className="mr-2"),
                            dbc.Select(id="occupation"),
                        ],
                    ),
                ],
                className="mt-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Sector", className="mr-2"),
                            dbc.Select(id="sector", options=get_sectors()),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Industry", className="mr-2"),
                            dbc.Select(id="industry"),
                        ],
                    ),
                ],
                className="mt-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Schooling", className="mr-2"),
                            dbc.Select(id="schooling", options=get_schooling()),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Age", className="mr-2"),
                            dbc.Select(
                                id="age",
                                value=40,
                                options=[
                                    {"label": i, "value": i} for i in range(20, 80)
                                ],
                            ),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Hrs/Wk", className="mr-2"),
                            dbc.Select(
                                id="hours",
                                value=40,
                                options=[
                                    {"label": i, "value": i} for i in range(5, 99)
                                ],
                            ),
                        ],
                    ),
                ],
                className="mt-2",
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Spinner(html.Div(id="model-output"))),
                    dbc.Col(
                        [
                            dbc.Button(
                                children=["What's my salary?"],
                                id="go-button",
                            ),
                        ]
                    ),
                ],
                className="mt-4",
            ),
            dbc.Spinner(dbc.Col(dcc.Graph(id="coef-graph"))),
        ],
    ),
)
graph_col = dbc.Card(
    [
        state_puma_selector,
        dbc.CardBody(
            [
                html.H2("Salaries by Age"),
                html.H6(id="salary-graph-title"),
                dbc.Spinner(dcc.Graph(id="salary-graph")),
            ],
        ),
    ],
)

page_content = dbc.Container(
    children=[
        dbc.Row(
            [
                dbc.Col([graph_col]),
                dbc.Col([model_inputs]),
            ]
        )
    ],
    fluid=True,
    style={"margin": "auto"},
)

footer = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.P(
                [
                    html.Span("Michael Johnson", className="mr-2"),
                    html.A(
                        html.I(className="fas fa-envelope-square mr-1"),
                        href="mailto:mdjhnsn@gwu.edu",
                    ),
                    html.A(
                        html.I(className="fab fa-github-square mr-1"),
                        href="https://github.com/mdjhnsn",
                    ),
                    html.A(
                        html.I(className="fab fa-linkedin mr-1"),
                        href="https://www.linkedin.com/in/data-arts-data-science/",
                    ),
                    html.A(
                        html.I(className="fab fa-twitter-square mr-1"),
                        href="https://twitter.com/apanelofsky",
                    ),
                ],
                className="footer mt-auto py-3",
            )
        )
    )
)
