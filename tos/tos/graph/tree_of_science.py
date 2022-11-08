"""
Tree of Scicence Client Class
=============================

The class :class:`~tos.graph.TreeOfScience` uses a :class:`~igraph.Graph`
instance to construct and perform queries about the structure of a reference
citation graph.

"""

import igraph as ig

import tos.graph.utils as utils


class TreeOfScience(object):

    """:class:`~tos.graph.tree_of_science.TreeOfScience` is a helper
    client class allows using instances of
    :class:`~tos.interpreters.interpreter.BaseInterpreter`
    along with some utilities and create a reference graph, it also allows
    basic querys to the graph's structure
    """

    def __init__(self, interpreter, config):
        super(TreeOfScience, self).__init__()
        self.interpreter = interpreter
        self.graph = ig.Graph()
        self.config = config
        self.configure()

    def __build_graph(self):
        entries = self.interpreter.parse(self.config['data'])
        labels = self.interpreter.get_label_list(entries)

        duplicate_options = self.config.get('duplicate_options', {})
        duplicates = utils.detect_duplicate_labels(labels,
                                                   **duplicate_options)
        unique_labels = list(set(utils.patch_list(labels, duplicates)))
        edge_relations = utils.extract_edge_relations(entries,
                                                      self.interpreter)
        unique_edge_relations = list(set(
            utils.patch_tuple_list(edge_relations, duplicates)
        ))

        identifiers = dict(zip(unique_labels, range(len(unique_labels))))
        self.graph = ig.Graph(
            utils.patch_tuple_list(unique_edge_relations, identifiers),
            directed=True
        )

        self.graph.vs['label'] = unique_labels

    def __preprocess_graph(self):
        # Filter out vertices that are not relevant in the dataset
        valid_vs = self.graph.vs.select(
            lambda v: v.indegree() != 1 or v.outdegree() != 0).indices
        self.graph = self.graph.subgraph(valid_vs)

        # Isolate the giant component
        self.graph = self.graph.clusters(ig.WEAK).giant()

    def __post_processg_graph(self):
        self.graph.vs['betweenness'] = self.graph.betweenness()
        self.graph.es['betweenness'] = self.graph.edge_betweenness()

    def configure(self):
        """Configures the :class:`~tos.graph.tree_of_science.TreeOfScience`
        instance according to
        its configuration and a given `data` field given in the config
        dictionary, it creates a graph from the edge relations of the
        entries contained in the data, filters the graph purging unnecesary
        vertices, and then extract the giant component of the graph.
        In a postprocessing stage it adds the edge and vertex betweenness
        to the graphs properties.
        """
        self.__build_graph()
        self.__preprocess_graph()
        self.__post_processg_graph()

    def root(self, offset=0, count=10):
        """Computes the nodes in the root of the graph using
        the following criteria: nodes with high in degree, and zero
        out degree are in the root set, this function returns
        `count` nodes after the `offset` element according to this
        criteria.

        :param int offset: rank of the first node to return
        :param int count: total number of nodes to return
        :returns: sequense of nodes in the root
        :rtype: :class:`~igraph.VertexSeq`
        """
        from operator import itemgetter

        valid_vs = self.graph.vs.select(_outdegree_eq=0).indices
        items = zip(
            self.graph.vs[valid_vs].indices,
            self.graph.vs[valid_vs].indegree(),
            self.graph.vs[valid_vs].outdegree(),
        )

        sorted_items = sorted(items, key=itemgetter(1), reverse=True)
        indices = list(zip(*sorted_items))[0][offset:offset + count]

        return self.graph.vs(indices)

    def trunk(self, offset=0, count=10):
        """Returns `count` nodes after the `ofset` belonging to the trunk
        of the graph, the *trunk degree* is computed according the
        following criteria:

        Compute the vertex betweness a of the graph and return them in
        descending order.

        @TODO: Relate the offset and count with the central point
        dominance.

        :param int offset: rank of the first node to return
        :param int count: total number of nodes to return
        :returns: sequense of nodes in the trunk
        :rtype: :class:`~igraph.VertexSeq`
        """
        from operator import itemgetter

        items = zip(
            self.graph.vs.indices,
            self.graph.vs['betweenness'],
        )

        sorted_items = sorted(items, key=itemgetter(1), reverse=True)
        indices = list(zip(*sorted_items))[0][offset:offset + count]
        return self.graph.vs(indices)

    def branch(self, offset=0, count=10):
        raise NotImplementedError('This feature is not implemented yet')

    def leave(self, offset=0, count=10):
        """Computes the leave nodes in the graph using
        the following criteria: nodes with high out egree, and zero
        in degree are in the leave set, this function returns
        `count` nodes after the `offset` element according to this
        criteria.

        :param int offset: rank of the first node to return
        :param int count: total number of nodes to return
        :returns: sequense of leave nodes
        :rtype: :class:`~igraph.VertexSeq`
        """
        from operator import itemgetter

        valid_vs = self.graph.vs.select(_indegree_eq=0).indices
        items = zip(
            self.graph.vs[valid_vs].indices,
            self.graph.vs[valid_vs].indegree(),
            self.graph.vs[valid_vs].outdegree(),
        )

        sorted_items = sorted(items, key=itemgetter(2), reverse=True)
        indices = list(zip(*sorted_items))[0][offset:offset + count]

        return self.graph.vs(indices)
