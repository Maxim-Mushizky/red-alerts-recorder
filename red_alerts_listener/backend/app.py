from flask import Flask
import os
from red_alerts_listener.backend.routes.map_routes import map_blueprint
from DEFINITIONS import ROOT_DIR

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(map_blueprint,
                       static_url_path="",
                       static_folder=os.path.join(ROOT_DIR, "red_alerts_listener/frontend/static"),
                       template_folder=os.path.join(ROOT_DIR, "red_alerts_listener/frontend/templates")
                       )

if __name__ == '__main__':
    app.run(debug=True)
