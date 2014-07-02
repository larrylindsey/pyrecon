from classes import Series, Contour, Section

# A class that represents graphs of Contours. By default, a ContourGraph prunes internal leaves.
class ContourGraph:

    '''
    Construct a contourGraph from the given dict of contours
     contours - a list of Contour traces, all belonging to the same object
     prune - determines whether to prune erroneous leaves from the graph/tree
     pruneDistance - only prune branches up to this length. Defaults to 4.
    '''
    def __init__(self, contours, prune=True, pruneDistance=4):
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

        self.__generateGraph()
        if prune:
            self.__prune(pruneDistance)

    '''
    Returns the graph-degree of the given contour. If the contour is not part of this
    graph, then its degree is defined to be 0.
    '''
    def degree(self, contour):
        if contour in self.__xmap:
            return len(self.__xmap[contour])
        else:
            return 0

    def __prune(self, pruneDistance):
        sectionMin = self.contours[0].section
        sectionMax = sectionMin

        degreeOneContours = []

        for contour in self.__xmap.keys():
            section = contour.section
            if sectionMin > section:
                sectionMin = section
            if sectionMax < section:
                sectionMax = section
            if self.degree(contour) == 1:
                degreeOneContours.append(contour)

        for contour in degreeOneContours:
            section = contour.section
            if section is not sectionMin and section is not sectionMax:
                self.__removeLeaf(contour)

    #todo
    def __removeLeaf(self, contour):
        pass

    '''
    Compute the graph, and prune if requested
    '''
    def __generateGraph(self):
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
        if cc1 in self.__xmap:
            self.__xmap[cc1].append(cc2)
        else:
            self.__xmap[cc1] = [cc2]

    @classmethod
    def fromSeriesAndRegexp(cls, series, regexp):
        contourDict = series.getContours(regexp)
        contourGraphs = [cls(contours) for contours in contourDict.values()]
        return contourGraphs