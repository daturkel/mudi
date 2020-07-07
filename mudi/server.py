"""
Adapted from Louis Tiao's recipe
http://louistiao.me/posts/python-simplehttpserver-recipe-serve-specific-directory/
"""

import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
from pathlib import Path
import posixpath
import os
import sys
import threading
from typing import Optional
from urllib.parse import unquote


class DirectoryServer(HTTPServer):
    def __init__(self, base_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RequestHandlerClass.base_path = base_path


class DirectoryRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = posixpath.normpath(unquote(path))
        words = path.split("/")
        words = filter(None, words)
        path = self.base_path
        for word in words:
            # for windows
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path


def serve(
    serve_dir: Path,
    port: int,
    HandlerClass=DirectoryRequestHandler,
    ServerClass=DirectoryServer,
):
    server_address = ("", port)

    with ServerClass(serve_dir, server_address, HandlerClass) as httpd:
        socket_address = httpd.socket.getsockname()
        logging.info(
            f"Serving http from {serve_dir} at http://{socket_address[0]}:{socket_address[1]}"
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print()
            logging.info("Keyboard interrupt received, exiting.")


def serve_cli(HandlerClass=DirectoryRequestHandler, ServerClass=DirectoryServer):
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", default=os.getcwd(), type=str, nargs="?")
    parser.add_argument("--port", "-p", default=8000, type=int)
    args = parser.parse_args()

    server_address = ("", args.port)
    with ServerClass(args.dir, server_address, HandlerClass) as httpd:
        socket_address = httpd.socket.getsockname()
        print(
            f"Serving http from {args.dir} on {socket_address[0]} port {socket_address[1]}..."
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)


if __name__ == "__main__":
    serve_cli()
