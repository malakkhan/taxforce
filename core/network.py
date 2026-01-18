import numpy as np
import networkx as nx
from collections import defaultdict

from .agents import BaseAgent

class NetworkBuilder:
    def __init__(self, config):
        self.net = config.network
        self.builders = {
            "lognormal": self.build_lognormal,
            "erdos": self.build_erdos,
            "powerlaw": self.build_powerlaw,
        }

    def build(self, agents: list[BaseAgent]):
        topology = self.net["topology"]
        builder = self.builders.get(topology)
        if not builder:
            raise ValueError(f"Unknown topology: {topology}")
        return builder(agents)



    # --- Topology builders ---

    def build_lognormal(self, agents):
        graph = nx.Graph()
        for agent in agents:
            graph.add_node(agent.unique_id, agent=agent)

        groups = self.group_by_sector(agents)

        for agent in agents:
            needed = self.sample_degree() - graph.degree(agent.unique_id)
            if needed <= 0:
                continue

            group_key = agent.group_key
            n_same = int(needed * self.net["homophily"])

            same, other = [], []
            for k, members in groups.items():
                for a in members:
                    id1 = a.unique_id
                    id2 = agent.unique_id
                    if id1 != id2 and not graph.has_edge(id1, id2):
                        if k == group_key: same.append(a)
                        else: other.append(a)

            self.add_edges(graph, agent, same, n_same)
            self.add_edges(graph, agent, other, needed - n_same)

        for agent in agents:
            agent.neighbors = [graph.nodes[n]["agent"] for n in graph.neighbors(agent.unique_id)]

        return graph

    def build_erdos(self, agents):
        raise NotImplementedError

    def build_powerlaw(self, agents):
        raise NotImplementedError



    # --- Helper methods ---

    def group_by_sector(self, agents):
        groups = defaultdict(list)
        for agent in agents:
            groups[agent.group_key].append(agent)
        return groups

    def add_edges(self, graph, agent, candidates, count):
        count = min(count, len(candidates))
        if count <= 0: return

        indices = np.random.choice(len(candidates), size=count, replace=False)
        for i in indices:
            graph.add_edge(agent.unique_id, candidates[i].unique_id)

    # Sample degree from lognormal distribution
    def sample_degree(self):
        mean, std = self.net["degree_mean"], self.net["degree_std"]
        mu = np.log(mean ** 2 / np.sqrt(std ** 2 + mean ** 2))
        sigma = np.sqrt(np.log(1 + std ** 2 / mean ** 2))
        degree = int(np.random.lognormal(mu, sigma))
        return int(np.clip(degree, self.net["degree_min"], self.net["degree_max"]))


def build_network(agents, config):
    return NetworkBuilder(config).build(agents)
