from classes import Series, Contour, Section

# A class that represents graphs of Contours. By default, a ContourGraph prunes internal leaves.
class ContourGraph:

    '''
    Construct a contourGraph from the given dict of contours
     contours - a list of Contour traces, all belonging to the same object
     prune - determines whether to prune erroneous leaves from the graph/tree
     pinnedLeaves - when pruning, keep these contours if they are leaves. Usually, this
            should be a list of the Contour objects that mark the upper and lower bound
            of the sub-process as represented in the contour dict. This is default behavior.
    '''
    def __init__(self, contours, prune=True, pinnedLeaves=None):
        # list of closed contours
        self.contours = [contour for contour in contours if contour.closed]
        # A dict of Contour->[Contour] in which the key is a Contour and the value is
        #   the list of Contours that are connected to it
        self.__xmap = {}
        # Get the name of the object for this graph. If we're passed an empty contour list,
        #   use ''
        if contours.empty():
            self.name = ''
        else:
            self.name = contours[0].name

        self.__generateGraph(prune, pinnedLeaves)

    '''
    Compute the graph, and prune if requested
    '''
    def __generateGraph(self, prune, pinnedLeaves):
        if pinnedLeaves is None:
            pinnedLeaves = self.__defaultPinnedLeaves()
        contourQ = self.contours
        while not contourQ.empty():
            contour = contourQ.pop(0)
            candidateNbd = [other for other in contourQ if
                            other.section is not None
                            and abs(other.section - contour.section) == 1]
            nbd = [neighbor for neighbor in candidateNbd if contour.overlaps(neighbor) > 0]
            for neighbor in nbd:
                self.__insertEdge(contour, neighbor)

    '''
    Insert an edge between two Contours
    '''
    def __insertEdge(self, c1, c2):
        self.__insertEdgeHelper(c1, c2)
        self.__insertEdgeHelper(c2, c1)

    def __insertEdgeHelper(self, cc1, cc2):
        if self.__xmap.has_key(cc1):
            self.__xmap[cc1].append(cc2)
        else:
            self.__xxmap[cc1] = [cc2]

    @classmethod
    def fromSeriesAndRegexp(cls, series, regexp):
        contourDict = series.getContours(regexp)
        contourGraphs = [cls(contours) for contours in contourDict.values()]
        return contourGraphs