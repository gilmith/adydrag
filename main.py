from flask import Flask, request, jsonify
from injector import Injector

from src.infrastructure.adapters.rest.TeamsAdapter import TeamsAdapter
from src.infrastructure.di.DependencyModule import DependencyModule


def create_app():

    flask_app = Flask(__name__)
    
    # Initialize the injector and configure it with the dependency module
    injector = Injector(modules=[DependencyModule()])
    teams_adapter = injector.get(TeamsAdapter)
    
    @flask_app.route('/api/messages', methods=['POST'])
    def process_message():
        return jsonify(teams_adapter.process_message())
    
    flask_app.name = "adyd_rag"
    return flask_app


if __name__ == "__main__":
    app = create_app()
    # Host 0.0.0.0 es necesario si usas Docker o quieres que sea accesible en tu red
    app.run(host='0.0.0.0', port=5000)