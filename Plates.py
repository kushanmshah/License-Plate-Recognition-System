import cv2
import math
import Preprocess
import Chars

WIDTH_PADDING = 1.3
HEIGHT_PADDING = 1.5


class PossibleChar:
    def __init__(self, _contour):
        self.contour = _contour
        self.Rectangle = cv2.boundingRect(self.contour)
        [intX, intY, intWidth, intHeight] = self.Rectangle
        self.intRectangleX = intX
        self.intRectangleY = intY
        self.intRectangleWidth = intWidth
        self.intRectangleHeight = intHeight
        self.intRectangleArea = self.intRectangleWidth * self.intRectangleHeight
        self.intCenterX = (self.intRectangleX + self.intRectangleX + self.intRectangleWidth) / 2
        self.intCenterY = (self.intRectangleY + self.intRectangleY + self.intRectangleHeight) / 2
        self.Diagonal = math.sqrt((self.intRectangleWidth ** 2) + (self.intRectangleHeight ** 2))
        self.AspectRatio = float(self.intRectangleWidth) / float(self.intRectangleHeight)


class PossiblePlate:
    def __init__(self):
        self.imgPlate = None
        self.imgGrayscale = None
        self.imgThresh = None
        self.Location = None
        self.strChars = ""


def findPossibleCharsInScene(imgThresh):
    ListPossibleChars = []
    intCount = 0
    imgThreshCopy = imgThresh.copy()
    imgContours, contours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(0, len(contours)):
        pc = PossibleChar(contours[i])
        if Chars.Check(pc):
            intCount = intCount + 1
            ListPossibleChars.append(pc)
    return ListPossibleChars


def Extract_Plate(imgOriginal, ListMatchingChars):
    pp = PossiblePlate()
    ListMatchingChars.sort(key=lambda matchingChar: matchingChar.intCenterX)
    PlateCenterX = (ListMatchingChars[0].intCenterX + ListMatchingChars[
        len(ListMatchingChars) - 1].intCenterX) / 2.0
    PlateCenterY = (ListMatchingChars[0].intCenterY + ListMatchingChars[
        len(ListMatchingChars) - 1].intCenterY) / 2.0
    ptPlateCenter = PlateCenterX, PlateCenterY
    intPlateWidth = int((ListMatchingChars[len(ListMatchingChars) - 1].intRectangleX + ListMatchingChars[
        len(ListMatchingChars) - 1].intRectangleWidth - ListMatchingChars[0].intRectangleX) * WIDTH_PADDING)
    intTotalOfCharHeights = 0
    for matchingChar in ListMatchingChars:
        intTotalOfCharHeights = intTotalOfCharHeights + matchingChar.intRectangleHeight
    AverageCharHeight = intTotalOfCharHeights / len(ListMatchingChars)
    intPlateHeight = int(AverageCharHeight * HEIGHT_PADDING)
    Opposite = ListMatchingChars[len(ListMatchingChars) - 1].intCenterY - ListMatchingChars[0].intCenterY
    Hypotenuse = Chars.Distance(ListMatchingChars[0], ListMatchingChars[len(ListMatchingChars) - 1])
    CorrectionRad = math.asin(Opposite / Hypotenuse)
    CorrectionDeg = CorrectionRad * (180.0 / math.pi)
    pp.Location = (tuple(ptPlateCenter), (intPlateWidth, intPlateHeight), CorrectionDeg)
    rotationMatrix = cv2.getRotationMatrix2D(tuple(ptPlateCenter), CorrectionDeg, 1.0)
    height, width, numChannels = imgOriginal.shape
    imgRotated = cv2.warpAffine(imgOriginal, rotationMatrix, (width, height))
    imgCropped = cv2.getRectSubPix(imgRotated, (intPlateWidth, intPlateHeight), tuple(ptPlateCenter))
    pp.imgPlate = imgCropped
    return pp


def Detect(imgOriginalScene):
    ListPossiblePlates = []
    cv2.destroyAllWindows()
    imgGrayscaleScene, imgThreshScene = Preprocess.Process(imgOriginalScene)
    ListPossibleCharsInScene = findPossibleCharsInScene(imgThreshScene)
    ListofList_MatchingCharsInScene = Chars.MatchList(ListPossibleCharsInScene)
    for ListMatchingChars in ListofList_MatchingCharsInScene:
        possiblePlate = Extract_Plate(imgOriginalScene, ListMatchingChars)
        if possiblePlate.imgPlate is not None:
            ListPossiblePlates.append(possiblePlate)
    return ListPossiblePlates
