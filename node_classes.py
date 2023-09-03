import numpy as np


class Node:
    """
    super class for nodes
    """
    def __init__(self, node_type=1):
        self.node_type = node_type


class CharacterNode(Node):
    def __init__(self, name, c_id, gender, age, action=None, expression=None):
        """
        node class for character
        :param name: str
        :param c_id: int, an unique id for character nodes
        :param gender: str
        :param age: str
        :param action: dict, {(action_name,start_frame,end_frame): num0,  ...}
        :param expression: dict, {(expression_name,start_frame,end_frame): num0, ...}
        """
        super(CharacterNode, self).__init__(1)
        self.name = name
        self.c_id = c_id
        self.gender = gender
        self.age = age
        if action is None:
            self.action = dict()
        else:
            self.action = action
        if expression is None:
            self.expression = dict()
        else:
            self.expression = expression

    def get_id(self):
        return self.c_id

    def add_action(self, act):
        """
        should be called by DataManagement class method
        :param act: tuple, (str, int, int), (action category, start_frame, end_frame)
        :return: None
        """
        self.action.update({act: len(self.action)})

    def add_expression(self, epr):
        """
        should be called by DataManagement class method
        :param epr: tuple, (str, int, int), (expression category, start_frame, end_frame)
        :return: None
        """
        self.expression.update({epr: len(self.expression)})


class ObjectNode(Node):
    def __init__(self, category, o_id):
        """
        node class for object
        :param category: int, index of corresponding object category
        :param o_id: int
        """
        super(ObjectNode, self).__init__(2)
        self.category = category
        self.o_id = o_id

    def get_id(self):
        return self.o_id


class RelationNode(Node):
    def __init__(self, r_id, l_node, r_node, category, why=None, when=None):
        """
        initialization for character-character relation or character-object relation or
        character-character interaction
        :param r_id: int, id
        :param l_node: str, left node name
        :param r_node: str, right node name
        :param category: str, name of the corresponding category
        :param why: str, only for character-character interaction, the reason why this interaction happened
        :param when: tuple, (start_frame, end_frame), only for character-character interaction, frame interval
        """
        super(RelationNode, self).__init__(1)
        self.r_id = r_id
        self.l_node = l_node
        self.r_node = r_node
        self.category = category
        self.why = None
        self.when = None

    def get_id(self):
        return self.r_id


class C2CRelationNode(RelationNode):
    """
    character-character relation
    """
    def __init__(self, r_id, l_node, r_node, category, why=None, when=None):
        super(C2CRelationNode, self).__init__(r_id, l_node, r_node, category, why, when)


class C2ORelationNode(RelationNode):
    """
    character-object relation
    """
    def __init__(self, r_id, l_node, r_node, category, why=None, when=None):
        super(C2ORelationNode, self).__init__(r_id, l_node, r_node, category, why, when)


class C2CInteractionNode(RelationNode):
    """
    character-character interaction
    """
    def __init__(self, r_id, l_node, r_node, category, why=None, when=None):
        super(C2CInteractionNode, self).__init__(r_id, l_node, r_node, category, why, when)
        self.why = why
        self.when = when
