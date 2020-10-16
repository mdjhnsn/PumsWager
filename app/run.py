import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import flask

from app.components.callbacks import register_callbacks
from app.components.layout import header, page_content, footer


server = flask.Flask(__name__)

external_stylesheets = [
    dbc.themes.YETI,
    # "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",
    "https://use.fontawesome.com/releases/v5.10.0/css/all.css",  # Social Media Icons
]

external_scripts = [
    "https://code.jquery.com/jquery-3.5.1.slim.min.js",
    "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js",
]

meta_tags = [{"name": "viewport", "content": "width=device-width, initial-scale=1"}]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts,
    meta_tags=meta_tags,
    server=server,
)

app.layout = html.Div(
    [
        header,
        dbc.Spinner(dcc.Store(id="store"), fullscreen=True),
        page_content,
        footer,
    ]
)

with server.app_context():
    app.title = "PumsWager"
    register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
