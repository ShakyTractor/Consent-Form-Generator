from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import sectionpaths
import fontconfig

# the class for the consent form pdf
class ConsentForm(Canvas):
    def __init__(self, fileName: str):
        super().__init__(filename=fileName, pagesize=A4)

        # sets the dimensions of the page as variables, measured in inches
        self.widthInches, self.heightInches = A4
        self.widthInches /= inch
        self.heightInches /= inch

        # sets the bounds of the page
        self.headerAndFooterHeight = 1
        self.maxYInches = self.heightInches - self.headerAndFooterHeight
        self.minYInches = self.headerAndFooterHeight
        self.totalInches = self.maxYInches - self.minYInches
        self.lineSeperationInches = 0.01  # multiplier so the line seperation will be relative to the font size

        self.currentFontSize = fontconfig.BODY_FONT_SIZE  # sets default font size


    # methods to change the font size and boldness to fit the preset tags explained in the readme
    def changeToHeader(self):
        self.setFont(fontconfig.FONT, fontconfig.HEADER_FONT_SIZE)
        self.currentFontSize = fontconfig.HEADER_FONT_SIZE

    def changeToBody(self):
        self.setFont(fontconfig.FONT, fontconfig.BODY_FONT_SIZE)
        self.currentFontSize = fontconfig.BODY_FONT_SIZE
    
    def changeToBold(self):
        self.setFont(fontconfig.BOLD_FONT, fontconfig.BODY_FONT_SIZE)
        self.currentFontSize = fontconfig.BODY_FONT_SIZE
    
    def changeToTitle(self):
        self.setFont(fontconfig.BOLD_FONT, fontconfig.HEADER_FONT_SIZE)
        self.currentFontSize = fontconfig.TITLE_FONT_SIZE
    

    # calculates the height of a single line given the font size
    def calculateLineHeight(self, fontsize: float):
        return (fontsize / 72) + fontsize*(self.lineSeperationInches)
    

    #calculates the total estimated height of a section given a list of its lines as an argument
    def calculateSectionHeight(self, lines: list) -> float:
        totalHeight = 0

        for line in lines:
            if line[::2] == '{B}':
                totalHeight += self.calculateLineHeight(fontconfig.BODY_FONT_SIZE)
            elif line[::2] == '{H}':
                totalHeight += self.calculateLineHeight(fontconfig.HEADER_FONT_SIZE)
            elif line[::2] == '{T}':
                totalHeight += self.calculateLineHeight(fontconfig.TITLE_FONT_SIZE)
            else:
                totalHeight += self.calculateLineHeight(fontconfig.BODY_FONT_SIZE)
        
        return totalHeight

    # returns a section in the form of a tuple with both a list of the lines with the tags and the estimated height of the section
    def getSection(self, section: str) -> tuple:  # for the section argument, use the given constants at the top of the file
        with open(section) as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]

        return (lines, self.calculateSectionHeight(lines))
    
    # returns a list of all the sections as tuples, see the getSection method above for more details
    def getListOfSectionTuples(self, numberOfPets: int) -> list:
        sections = []

        sections.append(self.getSection(sectionpaths.TITLE))
        sections.append(self.getSection(sectionpaths.CLIENT_DETAILS))
        sections.append(self.getSection(sectionpaths.CONTACT_INFORMATION))

        # the pet details section is duplicated for the amount of pets there are
        for i in range(numberOfPets):
            sections.append(self.getSection(sectionpaths.PET_INFORMATION))

        sections.append(self.getSection(sectionpaths.VET_INFO_AND_CONSENT))
        sections.append(self.getSection(sectionpaths.TERMS_AND_CONDITIONS))
        sections.append(self.getSection(sectionpaths.SOCIAL_MEDIA_CONSENT))
        sections.append(self.getSection(sectionpaths.FINAL_SIGNATURE))

        return sections


    # uses a list of sections and the boundaries of the page to split the list of sections into a 2D array of pages with sections inside
    def splitIntoPages(self, sections: list) -> list:

        # sets up the necessary arrays
        pages = []
        page = []

        # keeps track of the amount of one page used
        inchesUsed = 0

        # iterates through the sections
        for section in sections:
            section_height = section[1]  # gets the height from the tuple
            if inchesUsed + section_height > self.totalInches:  # checks that it can fit on the page
                pages.append(page)  # adds the page to the list of pages and resets the appropriate variables
                page = []
                inchesUsed = 0

            # adds the section to the page and adds a buffer between sections
            page.append(section)
            inchesUsed += section_height + 0.3

        # if the page has something on it, its added to the pages list
        if page:
            pages.append(page)
        
        return pages
    

    def drawPage(self, page: list, pageNumber: int, totalPages: int):

        inchesUsed = 0

        # iterates through the sections in the page
        for i in range(len(page)):
            # iterates through the lines in those sections
            for j in range(len(page[i][0])):
                
                # checks for formatting tags
                if page[i][0][j][:3] == '{B}':
                    self.changeToBold()
                    page[i][0][j] = page[i][0][j][3:]
                elif page[i][0][j][:3] == '{H}':
                    self.changeToHeader()
                    page[i][0][j] = page[i][0][j][3:]
                elif page[i][0][j][:3] == '{T}':
                    self.changeToTitle()
                    page[i][0][j] = page[i][0][j][3:]
                else:
                    self.changeToBody()  # sets to body text if there are no tags
            
                self.drawString(x=1*inch, y=(self.maxYInches - inchesUsed)*inch, text=page[i][0][j])  # types the line 1 inch from the right, and the inches used less then the maximum from the bottom
                inchesUsed += self.calculateLineHeight(self.currentFontSize)
            inchesUsed += 0.3
        
        self.changeToBody()
        self.drawString(text=f'Page {pageNumber}/{totalPages}                                   Gwen\'s Pet Services, Consent Form', x=1*inch, y=0.5*inch)  # adds page numbers on the bottom


    # uses the other methods in order to draw the whole consent form
    def drawConsentForm(self, numberOfPets: int):

        sections = self.getListOfSectionTuples(numberOfPets)
        pages = self.splitIntoPages(sections)
        
        # iterates through all the pages, and draws them
        for i in range(len(pages)):
            self.drawPage(pages[i], i+1, len(pages))
            self.showPage()
        
        self.save()  # saves the pdfs

        