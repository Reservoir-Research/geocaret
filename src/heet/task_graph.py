"""Representation of a graph mode for structuring tree-like computation
structures in which a number of tasks can be computed partly in parallel and
partly in sequence. This computation structure is meant to be a generalization
of the pipeline structure in which the tasks are computed in sequence."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
import collections
from multimethod import overload
import random
import string
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import numpy as np
import heet.log_setup

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


def random_string(length: int = 10, prefix: Optional[str] = None,
                  suffix: Optional[str] = None, joiner: str = "_") -> str:
    """Generate a random string of a specified length"""
    random_part = ''.join(random.sample(string.ascii_lowercase, length))
    if prefix is None:
        prefix = ""
    if suffix is None:
        suffix = ""
    full_string = joiner.join([prefix, random_part, suffix]).strip(joiner)
    return full_string


class NodeType(Enum):
    """Node types defined for the purpose of differentiating between node
    functions in graphs defining workflows for running structured data analysis
    jobs.
    """
    GENERIC = auto()
    DATA = auto()
    TRANSFORMER = auto()
    INITIAL = auto()
    FINAL = auto()


class LinkType(Enum):
    """Link types defined for the purpose of creating connections between
    nodes in graphs describing branched workflows of data processing tasks.
    """
    GENERIC = auto()
    GATE = auto()


@dataclass
class NodeID:
    """Unique identified of a generic graph node."""
    name: str = ""

    def __post_init__(self) -> None:
        if not bool(self.name):
            self.name = random_string(prefix="node")

    def __eq__(self, other: object) -> bool:
        """ """
        if not isinstance(other, NodeID):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other: object):
        if not isinstance(other, NodeID):
            return NotImplemented
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)


@dataclass
class LinkID:
    """Unique identifier of a generic graph edge."""
    name: str = ""

    def __post_init__(self) -> None:
        if not bool(self.name):
            self.name = random_string(prefix="link")

    @classmethod
    def from_node_ids(cls, node_id1: NodeID, node_id2: NodeID) -> LinkID:
        """Alternative constructor generating default link ids from
        linked node ids."""
        generated_id = "_".join([node_id1.name, node_id2.name])
        return cls(name=generated_id)

    def __eq__(self, other: object) -> bool:
        """ """
        if not isinstance(other, LinkID):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other: object):
        if not isinstance(other, LinkID):
            return NotImplemented
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)


class Node:
    """ """
    type = NodeType.GENERIC

    def __init__(
            self, id: Union[str, NodeID], owner: Optional[Graph] = None,
            **attributes: Any) -> None:
        if not isinstance(id, NodeID):
            self._id = NodeID(id)
        else:
            self._id = id
        self.attributes = attributes
        self._owner: Optional[Graph] = owner

    @property
    def id(self) -> NodeID:
        return self._id

    def __eq__(self, other: object) -> bool:
        """Equality operator for Node objects.
        Assumes that two objects be treated as equal if their ids are the same
        """
        if not isinstance(other, Node):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        # NOTE: Owner information not included in hashing method
        return hash((self.id, frozenset(self.attributes.items())))

    def __str__(self) -> str:
        node_info: str = f"Node {str(self._id)} with attributes:\n"
        attributes: str = f"{self.attributes}"
        if self.owner is not None:
            owner_info = f"Node in grap: self.owner.name"
            return "".join([node_info, attributes, owner_info])
        return "".join([node_info, attributes])

    @property
    def owner(self) -> Optional[Graph]:
        """ """
        return self._owner

    @owner.setter
    def owner(self, owner: Graph) -> None:
        self._owner = owner

    def owner_name(self) -> Optional[str]:
        """ """
        if self.owner is not None:
            return self.owner.name

    @property
    def downstream(self) -> Optional[List[NodeID]]:
        """ """
        if self.owner is not None:
            self.owner.adjacency_list[self.id]


    @property
    def out_links(self) -> List[Link]:
        """ """
        return NotImplemented

    @property
    def upstream(self) -> List[Node]:
        """ """
        return NotImplemented

    @property
    def in_links(self) -> List[Link]:
        """ """
        return NotImplemented


class Link:
    """Representation of a link/edge object."""
    def __init__(
            self, up: Union[Node, NodeID],
            down: Union[Node, NodeID],
            id: Optional[Union[str, LinkID]] = None,
            **attributes: Any) -> None:
        """ """
        if isinstance(up, Node):
            self.up_node_id = up.id
        else:
            self.up_node_id = up
        if isinstance(down, Node):
            self.bottom_node_id = down.id
        else:
            self.bottom_node_id = down
        if id is None:
            self._id = LinkID.from_node_ids(
                self.up_node_id, self.bottom_node_id)
        else:
            if not isinstance(id, LinkID):
                self._id = LinkID(id)
            else:
                self._id = id
        self.attributes = attributes

    @property
    def id(self) -> LinkID:
        return self._id

    def add_attribute(
            self, name: str, value: Any, override: bool = True) -> None:
        """Add attribute, e.g. link weight or any other piece of information"""
        if override is True or name not in self.attributes:
            self.attributes[name] = value
        else:
            logger.debug("Attribute %s cannot be overwritten", name)

    def remove_attribute(self, name) -> None:
        self.attributes.pop(name, None)


class Graph(ABC):
    """ """

    @property
    @abstractmethod
    def name(self) -> str:
        """ """


class DiGraph(Graph):
    """Class for storing directed graphs where nodes and links are objects
    containing logic and data."""
    def __init__(self, name: str = 'default') -> None:
        """Create an empty graph structure"""
        self._name = name
        # Adjacency list is built using node and edge ids and stores graph
        # Topology
        self._adjacency_list: Dict[NodeID, List[Tuple[NodeID, LinkID]]] = {}
        # Node_objects and link objects store node and link objects (logic and
        # data)
        self.node_objects: Dict[NodeID, Node] = {}
        self.link_objects: Dict[LinkID, Link] = {}

    def __contains__(self, item: object) -> bool:
        if isinstance(item, NodeID):
            return item in self.node_objects
        if isinstance(item, Node):
            return item.id in self.node_objects
        if isinstance(item, LinkID):
            return item in self.link_objects
        if isinstance(item, Link):
            return item.id in self.link_objects
        return False

    def __repr__(self) -> str:
        """Textual representation of the graph structure"""
        repr_txt: List[str] = [f"Graph: {self.name}"]
        for up_node_id, node_link_pairs in self.adjacency_list.items():
            for down_node_id, _ in node_link_pairs:
                repr_txt.append(f"{up_node_id.name} --> {down_node_id.name}")
        return "\n".join(repr_txt)

    def describe(self, print_description: bool = True) -> List[str]:
        """ """
        description: List[str] = []
        for node_id, connections in self.adjacency_list.items():
            if len(connections) == 0:
                description.append(
                    f"Node {node_id.name} is not connected to any nodes.")
            else:
                description.append(f"Node {node_id.name} is connected to:")
            for connected_node_id, edge_id in connections:
                description.append(
                    f" * node {connected_node_id.name} with edge {edge_id.name}.")
        if print_description:
            for txt in description:
                print(txt)
        return description

    @property
    def name(self) -> str:
        return self._name

    @overload
    def add_link(self, link: Link, overwrite: bool = True) -> None:
        """Adds link between two nodes defined in the link object.
        Requires that both nodes are already present in the graph."""
        if link.up_node_id in self and link.bottom_node_id in self:
            # Check if the link already exists or whether the nodes are not
            # connected with one another
            update_link: bool = True
            if link.id in self.link_objects and overwrite is False:
                logger.debug(
                    "Link between nodes: %s and %s already exist.",
                    link.up_node_id.name, link.bottom_node_id.name)
                update_link = False
            if update_link is True:
                self._adjacency_list[link.up_node_id].append(
                    (link.bottom_node_id, link.id))
                self.link_objects[link.id] = link
        else:
            if link.up_node_id not in self:
                logger.debug("Upper node %s absent.", link.up_node_id.name)
            if link.bottom_node_id not in self:
                logger.debug("Upper node %s absent.", link.bottom_node_id.name)
            logger.debug("Link coudl not be added.")

    @overload
    def add_link(self, up: Node, down: Node, overwrite: bool = False,
                 **attributes: Any) -> None:
        """Add link (edge) to a graph using a pair of nodes.
        Automatically constructs a link object with link id and attributes."""
        for node in [up, down]:
            self.add_node(node, overwrite)
        # Create and add a link
        link = Link(up, down, **attributes)
        #  Update the data structures
        if link in self and overwrite or link not in self:
            self._adjacency_list[up.id].append((down.id, link.id))
            self.link_objects[link.id] = link
        return None

    def add_node(self, node: Node, overwrite: bool = False) -> None:
        """Add node to adjacency list and node_objects dict."""
        node.owner = self
        if node.id not in self.adjacency_list:
            # TODO: Check `if node not in self`:
            self._adjacency_list[node.id] = []
            self.node_objects[node.id] = node
        else:
            if overwrite is True:
                logger.debug("Overwriting node %s", node.id)
                self._adjacency_list[node.id] = []
                self.node_objects[node.id] = node
            else:
                logger.debug("Node %s already exists.", node.id)
        return None

    def in_out_degrees(self, sort: bool = True) -> Dict[NodeID, List[int]]:
        """Find in and out degrees of each node in the graph.
                Time Complexity: O(V + E)
                Auxiliary Space: O(V + E).
            Returns a dictionary in which keys are node ids and values are
            2x1 vectors in which first element is the in-degree and the second
            element is the out-degree of the node.
        """
        in_out: Dict[NodeID, List[int]] = {}
        for out_node_id, connected_list in self._adjacency_list.items():
            if out_node_id not in in_out:
                in_out[out_node_id] = [0, 0]
            for node_id, _ in connected_list:
                in_out[out_node_id][1] += 1
                if node_id not in in_out:
                    in_out[node_id] = [0, 0]
                in_out[node_id][0] += 1
        if sort is True:
            return dict(sorted(in_out.items()))
        return in_out

    def find_isolated_nodes(self, as_names: bool = False) -> List[NodeID]:
        """Returns a list of isolated node ids."""
        isolated = set()
        for node_id, connections in self.adjacency_list.items():
            if len(connections) == 0:
                isolated.add(node_id)
        if as_names:
            return [node_id.name for node_id in isolated]
        return list(isolated)

    def find_path(
            self, start: Union[str, NodeID],
            end: Union[str, NodeID],
            path: Optional[List[NodeID]] = None,
            as_names: bool = False) -> Union[List[NodeID], List[str]]:
        """Finds path between a pair of nodes. Applies recurrency."""
        if isinstance(start, str):
            start = NodeID(start)
        if isinstance(end, str):
            end = NodeID(end)
        if path is None:
            path = []
        path.append(start)
        if start == end:
            if as_names:
                return [node.name for node in path]
            return path
        for node, _ in self.adjacency_list[start]:
            if node not in path:
                new_path = self.find_path(node, end, path, as_names)
                if new_path:
                    return new_path
                return []

    def breadth_first(
            self, root: Union[str, NodeID],
            custom_fun: Optional[Callable[[NodeID], Any]] = None,
            return_names: bool = False) -> Union[List[NodeID], List[str]]:
        """Breadth first search algorithm. Returns a list of nodes starting
        downwards from the start node."""
        if isinstance(root, str):
            root = NodeID(root)
        seen = set([root])
        queue = collections.deque([root])
        search_list = collections.deque([])
        while queue:
            vertex = queue.popleft()
            # Add custom logic in here
            # (on each visited vertex)
            if custom_fun is not None:
                fun(vertex)
            if return_names:
                search_list.append(vertex.name)
            else:
                search_list.append(vertex)
            for neighbour, _ in self.adjacency_list[vertex]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        return search_list

    def depth_first(self) -> None:
        raise NotImplementedError("Not yet implemented. Come back later.")

    def get_link(self, up_node: Node, down_node: Node) -> Optional[Link]:
        """Return link (edge) between two nodes"""
        try:
            connected_nodes = self._adjacency_list[up_node.id]
        except KeyError:
            logger.debug("Upstream node %s not in graph", up_node.id)
            return None
        for node, link in connected_nodes:
            if node == down_node:
                return link
        logger.debug("Downstream node %s no in graph", down_node.id)

    def link_ids(self) -> List[LinkID]:
        """Return the list of all link ids."""
        return list(self.link_objects.keys())

    def get_node(self, item: Union[NodeID, Node]) -> Optional[Node]:
        """ """
        return None

    def node_ids(self, sort: bool = True) -> List[NodeID]:
        """Return the list of all node ids."""
        node_list = list(self.node_objects.keys())
        if sort is True:
            return sorted(node_list)
        return node_list

    @property
    def adjacency_list(self) -> Dict[NodeID, List[Tuple[NodeID, LinkID]]]:
        """ """
        return self._adjacency_list

    def adjacency_matrix(self, name_indices: bool = True) -> List[List[LinkID]]:
        """Converts the adjacency list (base graph representation) into
        adjacency matrix and returns it in the form of a 2-dim array"""
        if name_indices:
            node_ids = self.node_ids(sort=True)
            indices = [node_id.name for node_id in node_ids]
        else:
            indices = node_ids
        # Create an empty nd-array
        # WORK IN PROGRESS
        mydtype = np.dtype([('c1', np.int16),
                       ('c2', np.int16),
                       ('c3', np.int16),
                       ('c4', np.float32)])

        data = np.array([(1,2.5,3, 4),(66,3.6,2,8)], dtype=mydtype)
        print(indices)
        print(data['c1'])
        return None


if __name__ == '__main__':
    """ """
    def test_node_comparison() -> None:
        node1 = Node(id=NodeID("1"), attr1 = "1")
        node2 = Node(id=NodeID("2"), attr1 = "1")
        node3 = Node(id=NodeID("1"), attr2 = "2")
        node4 = Node(id=NodeID("1"), attr2 = "2")
        assert node1 == node3
        assert node1 != node2
        assert hash(node1 != node2)
        assert hash(node3) == hash(node4)

    def test_link_creation() -> None:
        l1 = Link(
            up=NodeID("1"), down=NodeID("2"), attr1 = 1)
        assert l1.id.name == '1_2'
        assert l1.attributes == dict({'attr1': 1})

    # Run tests
    test_node_comparison()
    test_link_creation()

    g1 = DiGraph(name='test graph 1')
    #g1.add_link(up_node=Node(NodeID("1")), down_node=Node(NodeID("2")))
    #g1.add_link(up_node=Node(NodeID("1")), down_node=Node("3"))
    #g1.add_link(up_node=Node("3"), down_node=Node("4"))
    #g1.add_link(up_node=Node("1"), down_node=Node("5"))
    g1.add_node(node = Node("1"))
    g1.add_node(node = Node("2"))
    g1.add_link(link=Link(NodeID("1"), NodeID("2")), overwrite=True)
    g1.add_link(Node("1"), Node("66"))
    g1.add_link(Node("1"), Node("67"))
    g1.add_link(Node("67"), Node("68"))
    g1.add_link(Node("2"), Node("3"))
    g1.add_link(Node("5"), Node("6"))
    print(g1)
    print("Path:....")
    print(g1.find_path("1", "6"))
    in_out_degs = g1.in_out_degrees()
    print(in_out_degs)
    print(33 in g1)
    print("Printing graph connections")
    print(g1)
    print("BFS")
    print(g1.breadth_first("1", return_names=True))

    #g1.describe()
    g1.adjacency_matrix()
