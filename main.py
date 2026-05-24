from connexion import FlaskApp
from flask_injector import FlaskInjector

om src.infrastructure.adapters.rest.TeamsAdapter import TeamsAdapter
from src.infrastructure.di.DependencyModule import DependencyModule


def create_app():

    connexion_app = FlaskApp(__name__)
    flask_injector = FlaskInjector(
        app=connexion_app.app,
        modules=[DependencyModule()]
    )
    connexion_app.app.extensions['injector'] = flask_injector.injector
    injector = flask_injector.injector
    teams_adapter = injector.get(TeamsAdapter)
    connexion_app.add_url_rule(
        '/api/messages',
        view_func=teams_adapter.process_message,
        methods=['POST']
    )
    return connexion_app


if __name__ == "__main__":
    app = create_app()
    # Host 0.0.0.0 es necesario si usas Docker o quieres que sea accesible en tu red
    app.run(host='0.0.0.0', port=5000)