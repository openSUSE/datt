#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK


# To enable autocompletion, install python3-argcomplete and run:
# $ eval "$(register-python-argcomplete ./datt-cli.py)"


import argparse
import os
import sys

try:
    import argcomplete
except ImportError:
    argcomplete = None

# prefer osc git repo from the project directory
sys.path.insert(0, os.path.dirname(__file__) + "/osc")

import osc.conf
from osc.core import Request

import datt


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-A", "--apiurl",
        metavar="URL/alias",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "req_id",
        metavar="REQUEST-ID",
        nargs=1,
    )
    return parser


def main():
    parser = get_parser()
    if argcomplete:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    osc.conf.get_config(
        override_apiurl=args.apiurl,
        override_http_debug=args.debug,
    )

    apiurl = osc.conf.config["apiurl"]
    req_id = args.req_id[0]
    req = Request.from_api(apiurl, req_id)

    if req.state.name not in ("new", "review"):
        # Requests frequently perform 'delete' action on accepting to delete the source branch.
        # Using such requests would create misleading results (source package no longer exists etc.).
        # It also makes no sense to review the requests that were removed from the review queue.
        msg = f"Unable to process request '{req_id}' because it is in the '{req.state.name}' state"
        print(msg, file=sys.stderr)
        return

    print()
    print(">>>>> ACTIONS <<<<<")
    for action in req.actions:
        print()
        print(action)

        if action.src_pkg_object:
            indent = 4 * " "
            print()
            print(indent + ">>>>> SOURCE FILES <<<<<")
            for fo in action.src_pkg_object.files:
                print(indent + f"{fo.md5} {fo.mtime} {fo.name}")

        if action.tgt_pkg_object:
            indent = 4 * " "
            print()
            print(indent + ">>>>> TARGET FILES <<<<<")
            for fo in action.tgt_pkg_object.files:
                print(indent + f"{fo.md5} {fo.mtime} {fo.name}")

    print()
    print(">>>>> REVIEWS <<<<<")
    for review in req.reviews:
        print(review)

    print()
    print(">>>>> ISSUES <<<<<")
    for issue in req.issues:
        print(issue)

    print()
    print(">>>>> DESCRIPTION <<<<<")
    print(req.description)


if __name__ == "__main__":
    main()
