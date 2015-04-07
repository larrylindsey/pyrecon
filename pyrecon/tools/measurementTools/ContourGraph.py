import csv
# A class that represents graphs of Contours. By default, a ContourGraph prunes internal leaves.
class ContourGraph:

    '''
    Construct a contourGraph from the given dict of contours
     contours - a list of Contour traces, all belonging to the same object
     prune - determines whether to prune erroneous leaves from the graph/tree
     pruneDistance - only prune branches up to this length. Defaults to 4.
    '''
    def __init__(self, contours, prune=False, pruneDistance=4):
        # list of closed contours
        self.contours = [contour for contour in contours if contour.closed]

        self.__sectionMin = -1
        self.__sectionMax = -1

        # A dict of Contour->[Contour] in which the key is a Contour and the value is
        #   the list of Contours that are connected to it
        self.__xmap = {}
        # Get the name of the object for this graph. If we're passed an empty contour list,
        #   use ''
        if len(self.contours) == 0:
            self.name = ''
        else:
            self.name = self.contours[0].name

        self.__generateGraph()
        if prune:
            self.__prune(pruneDistance)
        else:
            self.__computeSectionRange()

    '''
    Returns the graph-degree of the given contour. If the contour is not part of this
    graph, then its degree is defined to be 0.
    '''
    def degree(self, contour):
        if contour is None:
            return 0
        elif contour in self.__xmap:
            return len(self.__xmap[contour])
        else:
            return 0

    def neighbors(self, contour):
        if contour in self.__xmap:
            return self.__xmap[contour]
        else:
            return []

    def getContours(self):
        return self.contours

    def writeComplexityCSV(self, filename):
        with open(filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['section', 'complexity'])
            sections, complexity = self.complexity()
            writer.writerows(zip(sections, complexity))

    def writeContourPlotCSV(self, filename, cutoff=3):
        with open(filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['x', 'y', 'z', 'complexity'])
            for contour in self.contours:
                n = len(contour.points)
                xs, ys = zip(*contour.points)
                x = sum(xs) / n
                y = sum(ys) / n
                complexity = self.degree(contour) + 1 - cutoff
                writer.writerow([x, y, contour.section, complexity])

    def complexity(self, cutoff=3):
        contourDegrees = [self.degree(contour) for contour in self.contours]
        contourSections = [contour.section for contour in self.contours]
        zipped = zip(contourSections, contourDegrees)

        complexityTuples = [t for t in zipped if t[1] >= cutoff]
        sections = range(self.__sectionMin, self.__sectionMax + 1)
        sectionComplexity = []

        for section in sections:
            sectionDegrees = [t[1] for t in complexityTuples if t[0] == section]
            complx = sum(sectionDegrees) - len(sectionDegrees) * (cutoff - 1)
            sectionComplexity.append(complx)

        return sections, sectionComplexity

    def __computeSectionRange(self):
        sectionMin = self.contours[0].section
        sectionMax = sectionMin
        for contour in self.contours:
            section = contour.section
            if sectionMin > section:
                sectionMin = section
            if sectionMax < section:
                sectionMax = section
        self.__sectionMin = sectionMin
        self.__sectionMax = sectionMax

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

        self.__sectionMin = sectionMin
        self.__sectionMax = sectionMax

        for contour in degreeOneContours:
            section = contour.section
            if section is not sectionMin and section is not sectionMax:
                self.__removeLeaf(contour, pruneDistance)

    def __removeLeaf(self, contour, pruneDistance):
        l = 0 #prune length
        currContour = contour
        seenContours = set()
        while currContour is not None and l <= pruneDistance and self.degree(currContour) < 3:
            l += 1
            seenContours.add(currContour)
            currContour = self.__pruneNextContour(currContour, seenContours)

        if l <= pruneDistance:
            self.__remove(seenContours)

    def __pruneNextContour(self, contour, seenContours):
        nbd = [c for c in self.neighbors(contour) if c not in seenContours]
        if len(nbd) == 0:
            return None
        else:
            return nbd[0]

    def __remove(self, contours):
        for contour in contours:
            nbd = self.neighbors(contour)
            for neighbor in nbd:
                neighborEdges = self.neighbors(neighbor)
                neighborEdges.remove(contour)
                if len(neighborEdges) == 0:
                    del self.__xmap[neighbor]
            if contour in self.__xmap:
                del self.__xmap[contour]

    '''
    Compute the graph, and prune if requested
    '''
    def __generateGraph(self):
        contourQ = list(self.contours)
        while len(contourQ) > 0:
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
