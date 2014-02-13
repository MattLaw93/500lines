import sys
import numpy
from node import Sphere, Cube
class Scene(object):
    """ Base class for scene nodes.
        Scene nodes currently only include primitives """

    # the default depth from the camera to place an object at
    PLACE_DEPTH = 15.0

    def __init__(self):
        """ Initialize the Scene """
        # The scene keeps a list of nodes that are displayed
        self.node_list = list()
        # Keep track of the currently selected node.
        # Actions may depend on whether or not something is selected
        self.selected_node = None

    def render(self):
        """ Render the scene. This function simply calls the render function for each node. """
        for node in self.node_list:
            node.render()

    def add_node(self, node):
        """ Add a new node to the scene """
        self.node_list.append(node)

    def picking(self, start, direction, mat):
        """ Execute selection.
            Consume: start, direction describing a Ray
                     mat              is the current modelview matrix for the scene """
        mindist = sys.maxint;
        closest_node = None
        # Keep track of the closest hit.
        for node in self.node_list:
            node.select(False)
            hit, distance = node.picking(start, direction, mat)
            if hit and distance < mindist:
                closest_node = node
                mindist = distance

        # If we hit something, keep track of it.
        if closest_node is not None:
            closest_node.select()
            closest_node.depth = mindist
            closest_node.selected_loc = start + direction * mindist
            self.selected_node = closest_node
        else:
            self.selected_node = None

    def move(self, start, direction, mat):
        """ Move the selected node, if there is one.
            Consume:  start, direction  describes the Ray to move to
                      mat               is the modelview matrix for the scene """
        if self.selected_node is None: return

        # Find the current depth and location of the selected node
        node = self.selected_node
        depth = node.depth
        oldloc = node.selected_loc

        # The new location of the node is the same depth along the new ray
        newloc = (start + direction * depth)

        # transform the translation with the modelview matrix
        # TODO: we should probably use the inverse of the transpose of mat. But this works since we don't use translation.
        translation = newloc - oldloc
        pre_tran = numpy.array([translation[0], translation[1], translation[2], 0])
        translation = mat.dot(pre_tran)

        # translate the node and track its location
        node.translate(translation[0], translation[1], translation[2])
        node.selected_loc = newloc


    def place(self, shape, start, direction, mat):
        """ Place a new node.
            Consume:  shape             the shape to add
                      start, direction  describes the Ray to move to
                      mat               is the modelview matrix for the scene """
        new_node = None
        if shape == 'sphere': new_node = Sphere()
        elif shape == 'cube': new_node = Cube()

        new_node.set_color(0.4, 0.4, 0.4)
        self.add_node(new_node)

        # place the node at the cursor in camera-space
        translation = (start + direction * self.PLACE_DEPTH)

        # convert the translation to world-space
        pre_tran = numpy.array([translation[0], translation[1], translation[2], 1])
        mat = numpy.transpose(mat)
        mat = numpy.linalg.inv(mat)
        translation = mat.dot(pre_tran)

        new_node.translate(translation[0], translation[1], translation[2])

