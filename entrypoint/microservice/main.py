import argparse
from waitress import serve
from microservice import create_app

if __name__=='__main__':
    # parse command line arguments
    argparser = argparse.ArgumentParser(description="Microservice")
    subparsers = argparser.add_subparsers()

    argparser_production = subparsers.add_parser('start', help="Runs the service in the production environment")

    # the host and port of the text embedding microservice
    argparser_production.add_argument('-H', '--host', type=str, default='127.0.0.1', help="The host of the microservice")
    argparser_production.add_argument('-p', '--port', type=str, default='4500', help="The port of the microservice")
    argparser_production.add_argument('-e', '--env', type=str, default='production', help="The microservice environment")
    argparser_production.add_argument('-teh', '--embedding_host', type=str, default='localhost', help='The host of the text embedding microservice')
    argparser_production.add_argument('-tep', '--embedding_port', type=str, default='4001', help='The port of the text embedding microservice')
    argparser_production.add_argument('-drh', '--retrieval_host', type=str, default='localhost', help='The host of the document retrieval microservice')
    argparser_production.add_argument('-drp', '--retrieval_port', type=str, default='4100', help='The port of the document retrieval microservice')
    argparser_production.add_argument('-dsh', '--similarity_host', type=str, default='localhost', help='The host of the document similarity microservice')
    argparser_production.add_argument('-dsp', '--similarity_port', type=str, default='4200', help='The port of the document similarity microservice')
    # TODO: the model parameters


    argparser_production.set_defaults(command='start')

    # parse the arguments and call whatever function was selected
    args = argparser.parse_args()

    if args.command == 'start':
        # get the arguments for creating the app
        arguments = {
            "host": args.host,
            "port": args.port,
            "env": args.env,
            "embedding_host" : args.embedding_host,
            "embedding_port" : args.embedding_port,
            "retrieval_host" : args.retrieval_host,
            "retrieval_port" : args.retrieval_port,
            "similarity_host" : args.similarity_host,
            "similarity_port" : args.similarity_port,
        }
        # create the application
        app = create_app(args=arguments)
        # run the application
        if args.env == 'production':
            serve(app, host=args.host, port=args.port)
        elif args.env == 'development':
            app.run(host=arguments["host"], port=arguments["port"], debug=True)

    else:
        raise Exception('Argument command is unknown: {}'.format(args.command))