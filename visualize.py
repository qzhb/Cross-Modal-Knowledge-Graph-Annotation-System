import sys
import pdb

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from data_management import DataManagement

plt.rcParams['font.sans-serif'] = ['SimHei']


def visualize(datamanager, filename):
    # get edge names
    collect_edge_categ = lambda x: [b.strip() if len(b) > 0 else 'interact' for a, b, c in x]
    c2c_rnodes = collect_edge_categ(datamanager.c2c_relation_nodes.keys())
    c2o_rnodes = collect_edge_categ(datamanager.c2o_relation_nodes.keys())
    c2c_inodes = collect_edge_categ(datamanager.c2c_interaction_nodes.keys())

    def rename_duplicates(mylist):
        '''
        ['a', 'a'] -> ['a1', 'a2']
        '''
        ret = []
        for i, v in enumerate(mylist):
            totalcount = mylist.count(v)
            count = mylist[:i].count(v)
            ret.append(v + str(count + 1) if totalcount > 1 else v)
        return ret

    # rename duplicates & merge edge names
    c2c_rnodes = rename_duplicates(c2c_rnodes)
    c2o_rnodes = rename_duplicates(c2o_rnodes)
    c2c_inodes = rename_duplicates(c2c_inodes)
    edgenode_names = c2c_rnodes + c2o_rnodes + c2c_inodes
    edgenode_types = {name: type_ for name, type_ in zip(
        edgenode_names, ['edge_c2cr'] * len(c2c_rnodes) +
        ['edge_c2or'] * len(c2o_rnodes) + ['edge_c2ci'] * len(c2c_inodes))}

    # merge nodes (with edges as nodes)
    nodes_df = pd.DataFrame({
        'name': list(datamanager.character_nodes.keys()) + list(datamanager.object_nodes.keys()) + edgenode_names,
        'type': ['character'] * len(datamanager.character_nodes) + ['object'] * len(datamanager.object_nodes) + ['edge'] * len(edgenode_names)
    })

    # merge sources & targets of edges
    edges_from = []
    edges_to = []

    def collect_edge(x, edgenodes, bidirect=False):
        for (a, b, c), edgenode in zip(x, edgenodes):
            edges_from.append(a)
            edges_to.append(edgenode)
            edges_from.append(edgenode)
            edges_to.append(c)
            if bidirect:  # bidirectional
                edges_from.append(c)
                edges_to.append(edgenode)
                edges_from.append(edgenode)
                edges_to.append(a)

    collect_edge(datamanager.c2c_relation_nodes.keys(),
                 c2c_rnodes)  # ('Potron', 'friend', 'Nurse')
    collect_edge(datamanager.c2o_relation_nodes.keys(), c2o_rnodes)
    collect_edge(datamanager.c2c_interaction_nodes.keys(),
                 c2c_inodes, bidirect=True)  # b is ''
    # pdb.set_trace()

    # merge edges
    edges_categ = ['c2c_r'] * len(c2c_rnodes) * 2 + ['c2o_r'] * \
        len(c2o_rnodes) * 2 + ['c2c_i'] * len(c2c_inodes) * 4
    edges_df = pd.DataFrame(
        {'from': edges_from, 'to': edges_to, 'type': edges_categ})

    # build graph
    G = nx.from_pandas_edgelist(edges_df, 'from', 'to', edge_attr='type',
                                create_using=nx.MultiDiGraph())

    # calculate node positions
    from networkx.drawing.nx_pydot import graphviz_layout
    pos = graphviz_layout(G, prog="fdp")

    # re-index nodes_df as the order in G
    nodes_df = nodes_df.set_index('name')
    nodes_df = nodes_df.reindex(G.nodes())
    # categorize nodes_df['type'] to indicate colors
    nodes_df['type'] = pd.Categorical(nodes_df['type'])
    nodes_df['type'].cat.codes

    # set edge colors
    type2num = {'c2c_r': '#87b3bb', 'c2o_r': '#737389', 'c2c_i': '#a68c7c'}
    edge_colors = [type2num[G[u][v][0]['type']] for u, v in G.edges()]

    # merge node types & attributes
    node_type_dict = {row[0]: row[1] for row in nodes_df.itertuples()}
    cnode_attrs_dict = {
        name: [item.gender, item.age, item.action, item.expression]
        for name, item in datamanager.character_nodes.items()}
    onode_attrs_dict = {
        name: item.category for name, item in datamanager.object_nodes.items()}
    enode_c2ci_attrs_dict = {
        name: [item.why, item.when] for name, (key, item) in zip(
            c2c_inodes, datamanager.c2c_interaction_nodes.items())}

    # draw the graph
    nx.draw(G, pos=pos, with_labels=True,
            node_color=nodes_df['type'].cat.codes, cmap=plt.cm.Set3,
            node_size=2500, font_size=12, edge_color=edge_colors)

    # draw additional attributes for nodes
    minl = 100000
    maxr = 0
    maxu = 0
    mind = 100000
    for node, (x, y) in pos.items():
        attr_str = ''
        dx = 0
        if node_type_dict[node] == 'character':
            attr_str = '{}，{}'.format(*cnode_attrs_dict[node][:2])
            if len(cnode_attrs_dict[node][2]) > 0:
                attr_str += '\n动作：{}({}-{})'.format(
                    *list(cnode_attrs_dict[node][2].keys())[0])
                if len(cnode_attrs_dict[node][2]) > 1:
                    attr_str += '…'
            if len(cnode_attrs_dict[node][3]) > 0:
                attr_str += '\n表情：{}({}-{})'.format(
                    *list(cnode_attrs_dict[node][3].keys())[0])
                if len(cnode_attrs_dict[node][3]) > 1:
                    attr_str += '…'
            attr_str = attr_str.replace(',', '')
            dx = -35
        elif node_type_dict[node] == 'object':
            attr_str = '类别：{:.0f}'.format(onode_attrs_dict[node])
            dx = 21
        else:
            if edgenode_types[node] == 'edge_c2ci':
                # show 'why' & 'when'
                attr_str = enode_c2ci_attrs_dict[node][0] if len(
                    enode_c2ci_attrs_dict[node][0]) > 0 else ''
                if len(enode_c2ci_attrs_dict[node][1]) > 0:
                    if len(enode_c2ci_attrs_dict[node][0]) > 0:
                        attr_str += '\n'
                    attr_str += '({}-{})'.format(*enode_c2ci_attrs_dict[node][1])
                dx = 23
        if len(attr_str) > 0:
            textbox = plt.text(x + dx, y, s=attr_str, bbox=dict(
                facecolor='#f0ffff', edgecolor='gray', alpha=0.5, boxstyle='round4'),
                horizontalalignment='center', verticalalignment='center')
            plt.gcf().canvas.draw()
            bbox = textbox.get_bbox_patch().get_extents().inverse_transformed(
                plt.gca().transData)
            minl = min(minl, bbox.x0)
            maxr = max(maxr, bbox.x1)
            maxu = max(maxu, bbox.y1)
            mind = min(mind, bbox.y0)

    # plt.subplots_adjust(top=0.7)
    plt.title('{} - {} - {}'.format(datamanager.plot,
                                    datamanager.scene, datamanager.event),
              fontsize=16)
    l, r = plt.xlim()
    minl = min(minl, l)
    maxr = max(maxr, r)
    plt.xlim(minl - 3, maxr + 3)
    # u, d = plt.ylim()
    # plt.ylim(u, d + 2)
    plt.savefig(filename)
    # plt.show()


# if __name__ == '__main__':
#     datamanager = DataManagement()
#     data_dir = sys.argv[1] if len(sys.argv) > 1 else 'outputdata/tt0119822_25_37/'
#     datamanager.load_nodes_and_links(data_dir)
#     filename = sys.argv[2] if len(sys.argv) > 2 else 'visualization.png'
#     visualize(datamanager, filename)
