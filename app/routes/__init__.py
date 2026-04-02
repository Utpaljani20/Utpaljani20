from .upload_route import upload
from .auth_route import auth
def register_routes(app):
    app.register_blueprint(upload, url_prefix="/")
    app.register_blueprint(auth)