import numpy as np
import networkx as nx
from numba import njit
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

    def build_lognormal_python(self, agents):
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
            agent.neighbor_ids = [n.unique_id for n in agent.neighbors]

        return graph

    def build_lognormal(self, agents):
        n = len(agents)
        reverse_map = {i: a.unique_id for i, a in enumerate(agents)}
        unique_groups = list({a.group_key for a in agents})
        group_to_int = {g: i for i, g in enumerate(unique_groups)}
        
        group_ids = np.array([group_to_int[a.group_key] for a in agents], dtype=np.int32)
        target_degrees = np.array([self.sample_degree() for _ in agents], dtype=np.int32)

        raw_edges = self.compute_edges_numba(n, group_ids, target_degrees, self.net["homophily"])
        
        graph = nx.Graph()
        graph.add_nodes_from((a.unique_id, {'agent': a}) for a in agents)
        graph.add_edges_from([(reverse_map[u], reverse_map[v]) for u, v in raw_edges])

        for agent in agents:
            neighbors = list(graph[agent.unique_id]) 
            agent.neighbor_ids = neighbors
            agent.neighbors = [graph.nodes[n_id]['agent'] for n_id in neighbors]

        return graph

    @staticmethod
    @njit(cache=True)
    def compute_edges_numba(n_agents, group_ids, target_degrees, homophily):
        edges = []
        current_deg = np.zeros(n_agents, dtype=np.int32)
        adj = np.zeros((n_agents, n_agents), dtype=np.bool_) 

        for i in range(n_agents):
            needed = target_degrees[i] - current_deg[i]
            if needed <= 0:
                continue
                
            n_same = int(needed * homophily)
            same_cands = []
            other_cands = []
            
            for j in range(n_agents):
                if i == j or adj[i, j]: 
                    continue
                if group_ids[j] == group_ids[i]:
                    same_cands.append(j)
                else:
                    other_cands.append(j)
                    
            for candidates, count in [(same_cands, n_same), (other_cands, needed - n_same)]:
                if count <= 0 or not candidates:
                    continue
                    
                cand_arr = np.array(candidates)
                n_cands = len(cand_arr)
                count = min(count, n_cands)
                
                for k in range(count):
                    idx = np.random.randint(k, n_cands)
                    cand_arr[k], cand_arr[idx] = cand_arr[idx], cand_arr[k]
                    target = cand_arr[k]
                    edges.append((i, target))
                    adj[i, target] = True
                    adj[target, i] = True
                    current_deg[i] += 1
                    current_deg[target] += 1
        return edges

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
