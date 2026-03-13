import argparse
import os 
import logging
import ssl

ROOT = os.path.dirname(__file__) + "/../"

AUDIOS_DIR = os.path.join(ROOT, "app/game/resources/audios/")

logger = logging.getLogger("pc")


import pathlib
import yaml

#TODO: use this instead of ROOT in all files
print(f'File = {__file__}')
BASE_DIR = pathlib.Path(__file__).parent.parent
config_path = BASE_DIR / "config" / "config.yaml"

def get_config(path):
    with open(path) as f:
        parsed_config = yaml.safe_load(f)
        return parsed_config

config = get_config(config_path)

def init_globals():
    global pcs
    pcs = set() 
    
    global args
    parser = argparse.ArgumentParser(
        description="WebRTC audio / data-channels demo"
    )
    
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
#        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
        "--host", default=os.getenv("HOST", "0.0.0.0"), help="Host for HTTP server"
    )

    parser.add_argument(
#        "--port", type=int, default=config["common"]["port"], help=f'Port for HTTP server (default from config.yaml: {config["common"]["port"]})'
       "--port", type=int, default=int(os.getenv("PORT", config["common"]["port"])), help="Port for HTTP server"
    )
    parser.add_argument("--record-to", help="Write received media to a file."),
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()
    
    config["common"]["port"] = args.port

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    global ssl_context    
    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None



