# -*- coding: utf-8 -*-

import argparse
import requests
import urllib
import xml.dom.minidom

from subprocess import check_call
from operator import methodcaller

from tos.interpreters import IsiInterpreter
from tos.graph.tree_of_science import TreeOfScience


def get_url_from_doi(doi):
    url = 'http://dx.doi.org/'
    post = {'hdl': doi}
    res = requests.post(url, post, allow_redirects=False)
    page = xml.dom.minidom.parseString(res.text)
    tags = page.getElementsByTagName('A')
    return tags.pop().getAttribute('HREF')


def get_url_from_label(label):
    url = 'https://google.com/'
    get = urllib.parse.urlencode({'q': label})
    return url + '#' + get


def open_url(url, program='xdg-open'):
    check_call([program, url])


def has_doi(label):
    return 'DOI' in label


def get_doi_from_label(label):
    return label.split(', ')[-1].split(' ')[-1]


def build_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input',
        help='input file to be parsed',
        type=argparse.FileType('r'))

    parser.add_argument(
        '--section',
        help='section of the tree of science to display defaults to root',
        type=str,
        choices=['root', 'trunk', 'branch', 'leave'],
        default='root')

    parser.add_argument(
        '--offset',
        help='article to start with',
        type=int,
        default=0)

    parser.add_argument(
        '--count',
        help='number of articles to return',
        type=int,
        default=10)

    parser.add_argument(
        '--program',
        help='program to open the urls with, *open* should be good for mac',
        type=str,
        default='xdg-open')

    return parser


def handle_input(args):
    tos = TreeOfScience(IsiInterpreter(), {'data': args.input.read()})
    method = methodcaller(
        args.section,
        offset=args.offset,
        count=args.count)

    labels = method(tos)['label']
    urls = []

    for label in labels:
        if has_doi(label):
            try:
                urls.append(get_url_from_doi(get_doi_from_label(label)))
            except:
                urls.append(get_url_from_label(label))
        else:
            urls.append(get_url_from_label(label))

    for url in urls:
        open_url(url, args.program)


def main():
    parser = build_argument_parser()
    args = parser.parse_args()
    handle_input(args)


if __name__ == '__main__':
    main()
