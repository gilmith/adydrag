import connexion
from flask_injector import FlaskInjector

from src.infrastructure.di.DependencyModule import DependencyModule


def create_app():
    # Especificamos que queremos la UI de Swagger activa
    options = {
        "swagger_ui": True,
        "swagger_path": "/ui"
    }
    connexion_app = connexion.FlaskApp(__name__, specification_dir='openapi/')
    connexion_app.add_api(
        'openapi.yaml',
        options=options,
        arguments={'title': 'D&D Bot API'}  # Puedes pasar variables al YAML
    )
    flask_injector = FlaskInjector(
        app=connexion_app.app,
        modules=[DependencyModule()]
    )
    # Guardamos el injector en extensions para poder acceder a él desde los adapters
    connexion_app.app.extensions['injector'] = flask_injector.injector
    return connexion_app


if __name__ == "__main__":
    app = create_app()
    # Host 0.0.0.0 es necesario si usas Docker o quieres que sea accesible en tu red
    app.run(host='0.0.0.0', port=5000)