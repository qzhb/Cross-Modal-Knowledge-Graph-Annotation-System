import numpy as np
import pickle as pkl
import sys
import os
import networkx as nx
import matplotlib.pyplot as plt

from node_classes import CharacterNode, ObjectNode, RelationNode, C2CRelationNode, C2ORelationNode, C2CInteractionNode


class DataManagement:
    """
    class for the overall data management
    """
    def __init__(self, path=None):
        """

        :param scene: str, the scene of the video clique
        :param event: str, the event of the video clique
        :param plot: str, the conclusion for the plot of the video clique
        :param path: str, the path for all the data files

        c_node_num_cnt: counting the number of character nodes
        o_node_num_cnt: counting the number of object nodes
        c2cr_node_num_cnt: counting the number of character-character relation nodes
        c2or_node_num_cnt: counting the number of character-object relation nodes
        c2ci_node_num_cnt: counting the number of character-character interaction nodes

        character_nodes: {character_name: CharacterNode}
        object_nodes: {(object_category+index): ObjectNode}
        c2c_relation_nodes: {(character1_name, relation_name, character2_name): C2CRelationNode}
        c2o_relation_nodes: {(character_name, relation_name, object_name): C2ORelationNode}
        c2c_interaction_nodes: {(character1_name, interaction_name, character2_name): C2CInteractionNode}

        c2c_relation_links: {character_node_name:
             {(right_character_node_name, c2c_relation_node_id): if_directed?, ...}, ...}
        c2o_relation_links: {character_node_name:
             {(right_object_node_name, c2o_relation_node_id): if_directed?, ...}, ...}
        c2c_interaction_links: {character_node_name:
             {(right_character_node_name, c2c_interaction_node_id): if_directed?, ...}, ...}

        object_category_distribution: recording each object-category's number of occurrence

        graph_nx: key: (node_token,node_id), (str, int)
        """
        self.scene = None
        self.event = None
        self.plot = None
        self.c_node_num_cnt = 0
        self.o_node_num_cnt = 0
        self.c2cr_node_num_cnt = 0
        self.c2or_node_num_cnt = 0
        self.c2ci_node_num_cnt = 0
        self.character_nodes = dict()
        self.object_nodes = dict()
        self.c2c_relation_nodes = dict()
        self.c2o_relation_nodes = dict()
        self.c2c_interaction_nodes = dict()
        self.c2c_relation_links = dict()
        self.c2o_relation_links = dict()
        self.c2c_interaction_links = dict()
        self.object_category_distribution = dict()
        self.object_dict, self.c2c_relation_dict, self.c2o_relation_dict, self.c2c_interaction_dict,\
            self.action_dict, self.expression_dict = self.load_indexes(path)
        self.node_token = ['cha', 'obj', 'c2c_rel', 'c2o_rel', 'c2c_ita']
        self.color_set = ['r', 'b', 'g', 'y', 'm']
        self.graph_nx = nx.DiGraph()

    @staticmethod
    def pickle_load(path, name):
        """
        load file {name} in {path}
        :param path: str
        :param name: str
        :return: None
        """
        with open(path+name, 'rb') as f:
            if sys.version_info > (3, 0):
                return pkl.load(f, encoding='latin1')
            else:
                return pkl.load(f)

    @staticmethod
    def pickle_save(path, name, obj):
        """
        save obj to file {name} in {path}
        :param path: str
        :param name: str
        :param obj: no restriction
        :return: None
        """
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path+name, 'wb') as f:
            pkl.dump(obj, f)

    # def save_nodes_and_links(self, path):
    #     self.pickle_save(path, "character.node", self.character_nodes)
    #     self.pickle_save(path, "object.node", self.object_nodes)
    #     self.pickle_save(path, "c2c.relation.node", self.c2c_relation_nodes)
    #     self.pickle_save(path, "c2o.relation.node", self.c2o_relation_nodes)
    #     self.pickle_save(path, "c2c.interaction.node", self.c2c_interaction_nodes)
    #     self.pickle_save(path, "c2c.relation.link", self.c2c_relation_links)
    #     self.pickle_save(path, "c2o.relation.link", self.c2o_relation_links)
    #     self.pickle_save(path, "c2c.interaction.link", self.c2c_interaction_links)
    #     self.pickle_save(path, "overall.info", {"scene": self.scene, "event": self.event, "plot": self.plot})
    #     self.pickle_save(path, "graph.nx.info", self.graph_nx)
    #     self.pickle_save(path, "count.info", {'c_node': self.c_node_num_cnt,
    #                                           'o_node': self.o_node_num_cnt,
    #                                           'c2cr_node': self.c2cr_node_num_cnt,
    #                                           'c2o_node': self.c2or_node_num_cnt,
    #                                           'c2ci_node': self.c2ci_node_num_cnt})
    #
    # def load_nodes_and_links(self, path):
    #     self.character_nodes = self.pickle_load(path, "character.node")
    #     self.object_nodes = self.pickle_load(path, "object.node")
    #     self.c2c_relation_nodes = self.pickle_load(path, "c2c.relation.node")
    #     self.c2o_relation_nodes = self.pickle_load(path, "c2o.relation.node")
    #     self.c2c_interaction_nodes = self.pickle_load(path, "c2c.interaction.node")
    #     self.c2c_relation_links = self.pickle_load(path, "c2c.relation.link")
    #     self.c2o_relation_links = self.pickle_load(path, "c2o.relation.link")
    #     self.c2c_interaction_links = self.pickle_load(path, "c2c.interaction.link")
    #     t_dict = self.pickle_load(path, "overall.info")
    #     self.scene = t_dict["scene"]
    #     self.event = t_dict["event"]
    #     self.plot = t_dict["plot"]
    #     self.graph_nx = self.pickle_load(path, "graph.nx.info")
    #
    #     count_dict = self.pickle_load(path, "count.info")
    #     self.c_node_num_cnt = count_dict["c_node"]
    #     self.o_node_num_cnt = count_dict["o_node"]
    #     self.c2cr_node_num_cnt = count_dict["c2cr_node"]
    #     self.c2or_node_num_cnt = count_dict["c2o_node"]
    #     self.c2ci_node_num_cnt = count_dict["c2ci_node"]

    def save_nodes_and_links(self, path):
        self.pickle_save(path, "character.node", self.character_nodes)
        self.pickle_save(path, "object.node", self.object_nodes)
        self.pickle_save(path, "c2c.relation.node", self.c2c_relation_nodes)
        self.pickle_save(path, "c2o.relation.node", self.c2o_relation_nodes)
        self.pickle_save(path, "c2c.interaction.node", self.c2c_interaction_nodes)
        self.pickle_save(path, "c2c.relation.link", self.c2c_relation_links)
        self.pickle_save(path, "c2o.relation.link", self.c2o_relation_links)
        self.pickle_save(path, "c2c.interaction.link", self.c2c_interaction_links)

        self.pickle_save(path, "overall.info", {"scene": self.scene, "event": self.event, "plot": self.plot})
        self.pickle_save(path, "graph.nx.info", self.graph_nx)

        self.pickle_save(path, "count.info", {'c_node': self.c_node_num_cnt,
                                              'o_node': self.o_node_num_cnt,
                                              'c2cr_node': self.c2cr_node_num_cnt,
                                              'c2or_node': self.c2or_node_num_cnt,
                                              'c2ci_node': self.c2ci_node_num_cnt,
                                              'object_category_distribution': self.object_category_distribution})

    def load_nodes_and_links(self, path):
        t_dict = self.pickle_load(path, "overall.info")
        self.scene = t_dict["scene"]
        self.event = t_dict["event"]
        self.plot = t_dict["plot"]
        self.character_nodes = self.pickle_load(path, "character.node")
        self.object_nodes = self.pickle_load(path, "object.node")
        self.c2c_relation_nodes = self.pickle_load(path, "c2c.relation.node")
        self.c2o_relation_nodes = self.pickle_load(path, "c2o.relation.node")
        self.c2c_interaction_nodes = self.pickle_load(path, "c2c.interaction.node")
        if os.path.exists(path+"count.info"):
            count_dict = self.pickle_load(path, "count.info")
            self.c_node_num_cnt = count_dict["c_node"]
            self.o_node_num_cnt = count_dict["o_node"]
            self.c2cr_node_num_cnt = count_dict["c2cr_node"]
            self.c2or_node_num_cnt = count_dict["c2or_node"]
            self.c2ci_node_num_cnt = count_dict["c2ci_node"]
            self.object_category_distribution = count_dict["object_category_distribution"]
            self.c2c_relation_links = self.pickle_load(path, "c2c.relation.link")
            self.c2o_relation_links = self.pickle_load(path, "c2o.relation.link")
            self.c2c_interaction_links = self.pickle_load(path, "c2c.interaction.link")
            self.graph_nx = self.pickle_load(path, "graph.nx.info")
        else:
            tmp_c = self.character_nodes
            self.character_nodes = dict()
            tmp_o = self.object_nodes
            self.object_nodes = dict()
            tmp_c2cr = self.c2c_relation_nodes
            self.c2c_relation_nodes = dict()
            tmp_c2or = self.c2o_relation_nodes
            self.c2o_relation_nodes = dict()
            tmp_c2ci = self.c2c_interaction_nodes
            self.c2c_interaction_nodes = dict()
            for k in tmp_c.keys():
                self.add_character_node(tmp_c[k].name, tmp_c[k].gender, tmp_c[k].age,tmp_c[k].action,tmp_c[k].expression)
            for k in tmp_o.keys():
                for cat,ans in self.object_dict.items():
                    if ans == tmp_o[k].category:
                        self.add_object_node(cat)
                        break
            for k in tmp_c2cr.keys():
                self.add_c2c_relation_node(tmp_c2cr[k].category, None, tmp_c2cr[k].l_node, tmp_c2cr[k].r_node)
            for k in tmp_c2or.keys():
                self.add_c2o_relation_node(tmp_c2or[k].category, None, tmp_c2or[k].l_node, tmp_c2or[k].r_node)
            for k in tmp_c2ci.keys():
                self.add_c2c_interaction_node(tmp_c2ci[k].category, None, tmp_c2ci[k].why, tmp_c2ci[k].when, tmp_c2ci[k].l_node, tmp_c2ci[k].r_node)

    def save_indexes(self, path):
        # names = ['obj', 'c2c_rel', 'c2o_rel', 'c2c_iac', 'act', 'epr']
        self.pickle_save(path, "obj.dict", self.object_dict)
        self.pickle_save(path, "c2c_rel.dict", self.c2c_relation_dict)
        self.pickle_save(path, "c2o_rel.dict", self.c2o_relation_dict)
        self.pickle_save(path, "c2c_iac.dict", self.c2c_interaction_dict)
        self.pickle_save(path, "act.dict", self.action_dict)
        self.pickle_save(path, "epr.dict", self.expression_dict)

    def load_indexes(self, path=None):
        names = ['obj', 'c2c_rel', 'c2o_rel', 'c2c_iac', 'act', 'epr']
        dicts = list()
        for i in range(len(names)):
            if path is None:
                dicts.append({})
                #self.pickle_save("../Datas/", "{}.dict".format(names[i]), {})
                continue
            dicts.append(self.pickle_load(path, "{}.dict".format(names[i])))
        for key in dicts[0].keys():
            self.object_category_distribution.update({key: 0})
        return tuple(dicts)

    def add_character_node(self, name, gender, age, action=None, expression=None):
        """
        add character node
        :param name: str
        :param gender: str, "male" or "female"
        :param age: str
        :return: None
        """
        self.graph_nx.add_node((self.node_token[0], self.c_node_num_cnt),
                               name=name, gender=gender, age=age, color=self.color_set[0])
        self.character_nodes.update({name: CharacterNode(name, self.c_node_num_cnt, gender, age, action, expression)})
        self.c_node_num_cnt += 1

    def add_object_node(self, category):
        """
        add object node
        :param category: str, name of the corresponding object category
        :return: None
        """
        if category not in self.object_dict:
            self.object_dict.update({category: len(self.object_dict)})
            self.object_category_distribution.update({category: 0})
        self.object_category_distribution[category] += 1
        category_idx = self.object_dict[category]
        o_name = category+str(self.object_category_distribution[category])
        self.graph_nx.add_node((self.node_token[1], self.o_node_num_cnt),
                               name=o_name, category=category, color=self.color_set[1])
        self.object_nodes.update({o_name: ObjectNode(
            category_idx, self.o_node_num_cnt)})
        self.o_node_num_cnt += 1

    def add_c2c_relation_node(self, category, ref, idx1, idx2, directed=True):
        """
        add character-character relation node and update links
        :param category: str, name of the corresponding c2c_relation category
        :param ref: str, name of the new c2c_relation category
        :param idx1: str, name of the character 1
        :param idx2: str, name of the character 2
        :param directed: bool, if this relation is directed
        :return: None
        """
        # idx1 = self.character_nodes[idx1].get_id()
        # idx2 = self.character_nodes[idx2].get_id()
        if ref is not None:
            #assert category is None
            self.c2c_relation_dict.update({ref: len(self.c2c_relation_dict)})
            category = ref
        else:
            if category not in self.c2c_relation_dict:
                return
            #assert category in self.c2c_relation_dict
        # category = self.c2c_relation_dict[category]
        self.graph_nx.add_node((self.node_token[2], self.c2cr_node_num_cnt),
                               l_node=idx1, r_node=idx2, category=category, color=self.color_set[2])
        self.c2c_relation_nodes.update({(idx1, category, idx2): C2CRelationNode(
            self.c2cr_node_num_cnt, idx1, idx2, category)})
        if idx1 not in self.c2c_relation_links:
            self.c2c_relation_links.update({idx1: {}})
        self.c2c_relation_links[idx1].update({(idx2, self.c2cr_node_num_cnt): directed})
        idx1 = self.character_nodes[idx1].get_id()
        idx2 = self.character_nodes[idx2].get_id()
        self.graph_nx.add_edge((self.node_token[0], idx1), (self.node_token[2], self.c2cr_node_num_cnt))
        self.graph_nx.add_edge((self.node_token[2], self.c2cr_node_num_cnt), (self.node_token[0], idx2))
        self.c2cr_node_num_cnt += 1

    def add_c2o_relation_node(self, category, ref, idx1, idx2, directed=True):
        """
        add character-object relation node and update links
        :param category: str, name of the corresponding c2o_relation category
        :param ref: str, name of the new c2o_relation category
        :param idx1: str, name of the character
        :param idx2: str, name of the object
        :param directed: bool, if this relation is directed
        :return: None
        """
        # idx1 = self.character_nodes[idx1].get_id()
        # idx2 = self.object_nodes[idx2].get_id()
        if ref is not None:
            #assert category is None
            self.c2o_relation_dict.update({ref: len(self.c2o_relation_dict)})
            category = ref
        else:
            if category not in self.c2o_relation_dict:
                return
            #assert category in self.c2o_relation_dict
        # category = self.c2o_relation_dict[category]
        self.graph_nx.add_node((self.node_token[3], self.c2or_node_num_cnt),
                               l_node=idx1, r_node=idx2, category=category, color=self.color_set[3])
        self.c2o_relation_nodes.update({(idx1, category, idx2): C2ORelationNode(
            self.c2or_node_num_cnt, idx1, idx2, category)})
        if idx1 not in self.c2o_relation_links:
            self.c2o_relation_links.update({idx1: {}})
        self.c2o_relation_links[idx1].update({(idx2, self.c2or_node_num_cnt): directed})
        idx1 = self.character_nodes[idx1].get_id()
        idx2 = self.object_nodes[idx2].get_id()
        self.graph_nx.add_edge((self.node_token[0], idx1), (self.node_token[3], self.c2or_node_num_cnt))
        self.graph_nx.add_edge((self.node_token[3], self.c2or_node_num_cnt), (self.node_token[1], idx2))
        self.c2or_node_num_cnt += 1

    def add_c2c_interaction_node(self, category, ref, why, when, idx1, idx2, directed=True):
        """
        add character-character interaction node and update links
        :param category: str, name of the corresponding c2c_interaction category
        :param ref: str, name of the new c2c_interaction category
        :param why: str, the reason why this interaction happened
        :param when: tuple, (start_frame, end_frame)
        :param idx1: str, name of the character 1
        :param idx2: str, name of the character 2
        :param directed: bool, if this relation is directed
        :return: None
        """
        # idx1 = self.character_nodes[idx1].get_id()
        # idx2 = self.character_nodes[idx2].get_id()
        if ref is not None:
            #assert category is None
            self.c2c_interaction_dict.update({ref: len(self.c2c_interaction_dict)})
            category = ref
        else:
            if category not in self.c2c_interaction_dict:
                return
            #assert category in self.c2c_interaction_dict
        # category = self.c2c_interaction_dict[category]
        self.graph_nx.add_node((self.node_token[4], self.c2ci_node_num_cnt),
                               l_node=idx1, r_node=idx2, category=category, color=self.color_set[4], why=why, when=when)
        self.c2c_interaction_nodes.update({(idx1, category, idx2, when): C2CInteractionNode(
            self.c2ci_node_num_cnt, idx1, idx2, category, why, when)})
        if idx1 not in self.c2c_interaction_links:
            self.c2c_interaction_links.update({idx1: {}})
        self.c2c_interaction_links[idx1].update({(idx2, self.c2ci_node_num_cnt): directed})
        idx1 = self.character_nodes[idx1].get_id()
        idx2 = self.character_nodes[idx2].get_id()
        self.graph_nx.add_edge((self.node_token[0], idx1), (self.node_token[4], self.c2ci_node_num_cnt))
        self.graph_nx.add_edge((self.node_token[4], self.c2ci_node_num_cnt), (self.node_token[0], idx2))
        self.c2ci_node_num_cnt += 1

    def add_action(self, c_name, act, time_interval):
        """
        add the action of {c_name} in time period {time_interval}
        :param c_name: str, name of the character
        :param act: str, name of the corresponding action category
        :param time_interval: tuple, (start_frame, end_frame)
        :return:None
        """
        if act not in self.action_dict:
            self.action_dict[act] = len(self.action_dict)
        # category_idx = self.action_dict[act]
        self.character_nodes[c_name].add_action((act, time_interval[0], time_interval[1]))

    def add_expression(self, c_name, epr, time_interval):
        """
        add the expression of {c_name} in time period {time_interval}
        :param c_name: str, name of the character
        :param epr: str, name of the corresponding expression category
        :param time_interval: tuple, (start_frame, end_frame)
        :return: None
        """
        if epr not in self.expression_dict:
            self.expression_dict[epr] = len(self.expression_dict)
        # category_idx = self.expression_dict[epr]
        self.character_nodes[c_name].add_expression((epr, time_interval[0], time_interval[1]))

    def get_characters(self):
        """
        return the list of the current characters'name
        :return: list
        """
        return list(self.character_nodes.keys())

    def delete_character_node(self, name):
        """
        delete character node and corresponding relations by the character's name
        :param name: str
        :return: bool
        """
        if name in self.character_nodes:
            tmp_d = list(self.c2c_relation_nodes.keys())
            for k in tmp_d:
                if self.c2c_relation_nodes[k].l_node == name or self.c2c_relation_nodes[k].r_node == name:
                    self.delete_c2c_relation_node(k)
            tmp_d = list(self.c2o_relation_nodes.keys())
            for k in tmp_d:
                if self.c2o_relation_nodes[k].l_node == name:
                    self.delete_c2o_relation_node(k)
            tmp_d = list(self.c2c_interaction_nodes.keys())
            for k in tmp_d:
                if self.c2c_interaction_nodes[k].l_node == name or self.c2c_interaction_nodes[k].r_node == name:
                    self.delete_c2c_interaction_node(k)
            self.graph_nx.remove_node((self.node_token[0], self.character_nodes[name].get_id()))
            del self.character_nodes[name]
            return True
        return False

    def get_objects(self):
        """
        return the list of the current objects'name
        :return: list
        """
        return list(self.object_nodes.keys())

    def delete_object_node(self, name):
        """
        delete by the name of the certain object and its corresponding relations
        :param name: str
        :return: bool
        """
        if name in self.object_nodes:
            tmp_d = list(self.c2o_relation_nodes.keys())
            for k in tmp_d:
                if self.c2o_relation_nodes[k].r_node == name:
                    self.delete_c2o_relation_node(k)
            self.graph_nx.remove_node((self.node_token[1], self.object_nodes[name].get_id()))
            del self.object_nodes[name]
            return True
        return False

    def get_actions(self, name):
        """
        return the list of the actions corresponding to name of certain character
        :param name: str
        :return: list of tuple, [(str, int, int), ...], [(action category, start_frame, end_frame), ...]
        """
        return list(self.character_nodes[name].action.keys())

    def delete_actions(self, name, act):
        """
        delete certain action in the form of (action category, start_frame, end_frame) of character {name}
        :param name: str, name of the corresponding character
        :param act: tuple, (str, int, int), tuple description of the action, (action category, start_frame, end_frame)
        :return: bool
        """
        if name in self.character_nodes and act in self.character_nodes[name].action:
            del self.character_nodes[name].action[act]
            return True
        return False

    def get_expressions(self, name):
        """
        return the list of the expressions corresponding to name of certain character
        :param name: str
        :return: list of tuple, [(str, int, int), ...], [(expression category, start_frame, end_frame), ...]
        """
        return list(self.character_nodes[name].expression.keys())

    def delete_expression(self, name, epr):
        """
        delete certain expression in the form of (expression category, start_frame, end_frame) of character {name}
        :param name: str, name of the corresponding character
        :param epr: tuple, (str, int, int), tuple description of the expression, (expression category, start_frame, end_frame)
        :return: bool
        """
        if name in self.character_nodes and epr in self.character_nodes[name].expression:
            del self.character_nodes[name].expression[epr]
            return True
        return False

    def get_c2c_relations(self):
        """
        return all c2c relations in the form of (str, str, str), (character_name1, relation_name, character_name2)
        :return: list of tuple, [(character_name1, relation_name, character_name2), ...]
        """
        return list(self.c2c_relation_nodes.keys())

    def delete_c2c_relation_node(self, k):
        """
        delete certain c2c_relation_node by its id
        :param k: tuple, (str, str, str), (character_name1, relation_name, character_name2)
        :return: bool
        """
        if k not in self.c2c_relation_nodes:
            return False
        self.graph_nx.remove_node((self.node_token[2], self.c2c_relation_nodes[k].get_id()))
        r_id = self.c2c_relation_nodes[k].get_id()
        l_node = k[0]
        r_node = k[2]
        if l_node in self.c2c_relation_links:
            if (r_node, r_id) in self.c2c_relation_links[l_node]:
                del self.c2c_relation_links[l_node][(r_node, r_id)]
            else:
                return False
        else:
            return False
        del self.c2c_relation_nodes[k]
        return True

    def get_c2o_relations(self):
        """
        return all c2o relations in the form of (str, str, str), (character_name, relation_name, object_name)
        :return: list of tuple, [(character_name, relation_name, object_name), ...]
        """
        return list(self.c2o_relation_nodes.keys())

    def delete_c2o_relation_node(self, k):
        """
        delete certain c2o_relation_node by its id
        :param k: tuple, (str, str, str), (character_name, relation_name, object_name)
        :return: bool
        """
        if k not in self.c2o_relation_nodes:
            return False
        self.graph_nx.remove_node((self.node_token[3], self.c2o_relation_nodes[k].get_id()))
        r_id = self.c2o_relation_nodes[k].get_id()
        l_node = k[0]
        r_node = k[2]
        if l_node in self.c2o_relation_links:
            if (r_node, r_id) in self.c2o_relation_links[l_node]:
                del self.c2o_relation_links[l_node][(r_node, r_id)]
            else:
                return False
        else:
            return False
        del self.c2o_relation_nodes[k]
        return True

    def get_c2c_interactions(self):
        """
        return all c2c interactions in the form of (str, str, str), (character_name1, interaction_name, character_name2)
        :return: list of tuple, [(character_name1, interaction_name, character_name2), ...]
            and dict to correspond tuple (character_name1, interaction_name, character_name2) to its id
        """
        return list(self.c2c_interaction_nodes.keys())

    def delete_c2c_interaction_node(self, k):
        """
        delete certain c2c_interaction_node by its id
        :param k: tuple, (str, str, str, tuple), (character_name1, interaction_name, character_name2, time)
        :return: bool
        """
        if k not in self.c2c_interaction_nodes:
            return False
        self.graph_nx.remove_node((self.node_token[4], self.c2c_interaction_nodes[k].get_id()))
        r_id = self.c2c_interaction_nodes[k].get_id()
        l_node = k[0]
        r_node = k[2]
        if l_node in self.c2c_interaction_links:
            if (r_node, r_id) in self.c2c_interaction_links[l_node]:
                del self.c2c_interaction_links[l_node][(r_node, r_id)]
            else:
                return False
        else:
            return False
        del self.c2c_interaction_nodes[k]
        return True

    def get_c2c_relation_category(self):
        """
        :return: list of names of categories, [name1, name2, ...]
        """
        return list(self.c2c_relation_dict.keys())

    def get_c2o_relation_category(self):
        """
        :return: list of names of categories, [name1, name2, ...]
        """
        return list(self.c2o_relation_dict.keys())

    def get_c2c_interaction_category(self):
        """
        :return: list of names of categories, [name1, name2, ...]
        """
        return list(self.c2c_interaction_dict.keys())

    def graph_data_visualization(self, path="../visualizations/"):
        nc = [c[1] for c in self.graph_nx.nodes.data('color')]
        nx.draw(self.graph_nx, node_color=nc)
        #plt.show()
        if not os.path.exists(path):
            os.makedirs(path)
        nx.draw(self.graph_nx, node_color=nc)
        plt.savefig(path+"graph_data_visualization.png")

    def convert_to_xml(self):
        pass

    def check_duplicate(self):
        pass

