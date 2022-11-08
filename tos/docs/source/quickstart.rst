Quickstart
==========

Installing the package
----------------------

First thing you should grab the latest version of the source code using git

.. code-block:: bash

    git clone git clone git@bitbucket.org:odarbelaeze/tos.git

as this library is very unstable yet we recomend to use a virtualenv to
install it on, and also the library also support python3

.. code-block:: bash

    cd tos
    sudo pip3 install virtualenv virtualenvwrapper
    source /usr/local/bin/virtualenvwrapper.sh
    mkvirtualenv -a $(pwd) -r piprequirements -p /usr/bin/python3.4 tosenv
    python setup.py develop

If you have issues installing Igraph we recomend to install the Igraph C
library from [here](http://igraph.org/c/#downloads), the installation is
very straightforward.

Using the library
-----------------

The library is divided in two tiers right now the **interpreters** and the
**TreeOfScience** client class, in order to perform a simple analysis, you
shoud perform the following operations.

.. code-block:: python
    :linenos:

    from tos.interpreters import IsiInterpreter
    from tos.graph.tree_of_science import TreeOfScience
    data = open('sample_data/isi.txt', 'r').read()
    tos = TreeOfScience(IsiInterpreter(), {'data': data})

    # Now you can query the tos instance
    root_articles = tos.root()['label']
    trunk_articles = tos.trunk()['label']

The queries performed over the **TreeOfScience** instance return igraph's
**VertexSeq** instances, refer back to the
[documentation](http://igraph.org/python/doc/igraph.VertexSeq-class.html)
to learn more.

Exploring the builtin documentation
-----------------------------------

In order to build and explore the provided documentation from the repository
folder you should peform:

.. code-block:: bash

    cd docs
    make html # Or may be pdf
    xdg-open build/html/index.html


