from typing import List


def delta_f(f_ck):
    if f_ck <= 40:
        return 4
    elif f_ck >= 60:
        return 6
    else:
        return (f_ck-40)/10


# 철근 단면적 [mm2]
A_r_table = {'D10': 71.3, 'D13': 126.7, 'D16': 198.6, 'D19': 286.7, 'D22': 387.1, 'D25': 507.7}    


# 직사각형단면의 면적, 도심, 도심축에 대한 단면2차모멘트
class SquareSectionProperties:
    
    def __init__(self, H, B, x, y) -> None:        
        self.H = H
        self.B = B
        self.locationX = x
        self.locationY = y
        self.area = H * B
        self.centerX = B/2
        self.centerY = H/2
        self.inertiaX = B * H**3 / 12
        self.inertiaY = H * B**3 / 12


# 조합단면의 총면적, 도심, 도심축에 대한 단면2차모멘트        
class CombinedSectionProperties:
    
    def __init__(self,*squares) -> None:
        self.area = 0
        self.momentAtAxisX = 0
        self.momentAtAxisY = 0
        self.inertiaX = 0
        self.inertiaY = 0
        
        for square in squares:
            self.area += square.area
            self.momentAtAxisX += square.area * square.locationY
            self.momentAtAxisY += square.area * square.locationX
        
        self.centerX = self.momentAtAxisY / self.area
        self.centerY = self.momentAtAxisX / self.area
        
        for square in squares:
            self.inertiaX += square.inertiaX + square.area * (square.locationY - self.centerY)**2
            self.inertiaY += square.inertiaY + square.area * (square.locationX - self.centerX)**2


# 단면 분할
class DivideY:
    
    def __init__(self, section:SquareSectionProperties, distanceY) -> None:
        self.newH1 = distanceY - (section.locationY - section.H/2)
        self.newH2 = section.H - self.newH1
        self.dividedSection1 = SquareSectionProperties(self.newH1, section.B, section.locationX, (self.newH1/2 + (section.locationY - section.H/2)))
        self.dividedSection2 = SquareSectionProperties(self.newH2, section.B, section.locationX, (distanceY+self.newH2/2))
        

# 소성단면계수[mm3]    
class PlasticSectionCoefficient:
    
    def __init__(self,includedSections:List, dividedSections:List) -> None:
        self.incSecArea = 0
        self.divSecArea = 0
        self.redundantArea = 0
        self.totalThickness = 0
        self.plasticNeutralCenterY = 0
        self.bottomSections = []
        self.topSections = []
        
        for section in includedSections:
            self.incSecArea += section.area
        
        for section in dividedSections:
            self.divSecArea += section.area
            self.redundantArea += section.B * (section.locationY - section.H/2)
            self.totalThickness += section.B            
        
        self.plasticNeutralCenterY = ((self.incSecArea+self.divSecArea)/2-self.incSecArea + self.redundantArea) / self.totalThickness

        for section in includedSections:
            if (section.locationY <= self.plasticNeutralCenterY):
                self.bottomSections.append(section)
            else:
                self.topSections.append(section)
                
        for i in range(len(dividedSections)):
            self.bottomSections.append(DivideY(dividedSections[i], self.plasticNeutralCenterY).dividedSection1)            
            self.topSections.append(DivideY(dividedSections[i], self.plasticNeutralCenterY).dividedSection2)
        
        self.botSecCenterY = CombinedSectionProperties(*self.bottomSections).centerY
        self.topSecCenterY = CombinedSectionProperties(*self.topSections).centerY        
        self.plasticSecCoef = (self.incSecArea+self.divSecArea)/2 * (self.topSecCenterY - self.botSecCenterY)

        
# 판폭두께비
class WTRatio ():

    def __init__(self, *, width, thickness, E_s, F_y) -> None:
        self.width = width
        self.thickness = thickness
        self.E_s = E_s
        self.F_y = F_y
        self.judgment = ''

    def Judgment(self):
        if (self.w_t_Ratio <= self.lambda_p):
            return 'Compact'
        elif (self.w_t_Ratio <= self.lambda_r):
            return 'NonCompact'
        else:
            return 'Slender'

    def TopFlange(self):        # KBC2016 <표 0702.4.1> (5)
        self.lambda_p = 0.54 * (self.E_s/self.F_y)**(1/2)
        self.lambda_r = 0.91 * (self.E_s/self.F_y)**(1/2)
        self.w_t_Ratio = self.width / self.thickness
        return self.Judgment()

    def Web(self):              # KBC2016 <표 0702.4.1> (9)
        self.lambda_p = 3.76 * (self.E_s/self.F_y)**(1/2)
        self.lambda_r = 5.70 * (self.E_s/self.F_y)**(1/2)
        self.w_t_Ratio = (self.width-2*self.thickness) / \
            self.thickness  # 순수 웨브 높이
        return self.Judgment()

    def BottomFlange(self):     # KBC2016 <표 0702.4.1> (12)
        self.lambda_p = 1.12 * (self.E_s/self.F_y)**(1/2)
        self.lambda_r = 1.40 * (self.E_s/self.F_y)**(1/2)
        self.w_t_Ratio = (self.width-2*self.thickness) / \
            self.thickness  # 순수 플렌지 폭
        return self.Judgment()


# 유효폭 KBC2016 0709.3.1.1
def EffectiveWidth(*, span, bay):          
    b1 = span / 8
    b2 = bay / 2
    # b3 = "보 중심선에서 슬래브 가장자리까지의 거리"       <== 추후 구현
    return min(b1, b2)


class Load:
    
    def __init__(self, pointLoad, loadLocation, lineLoad, length) -> None:
        self.pointLoad = pointLoad
        self.a = loadLocation
        self.b = length - loadLocation
        self.lineLoad = lineLoad
        self.length = length
        self.posMoment = 0
        self.negMoment = 0
        self.shearForce = 0        
    
    def FixPoint(self):
        self.posMoment = 2 * self.pointLoad * self.a**2 * self.b**2 / self.length**3
        self.negMoment = self.pointLoad * self.b**2 * (3*self.a + self.b) / self.length**3
        self.shearForce = self.pointLoad * self.a * self.b**2 / self.length**2
        
    def SimplePoint(self):
        self.posMoment = self.pointLoad * self.length / 2
        self.negMoment = 0
        self.shearForce = self.pointLoad / 2
        
    def FixLine(self):
        self.posMoment = self.lineLoad * self.length**2 / 24
        self.negMoment = self.lineLoad * self.length**2 / 12
        self.shearForce = self.lineLoad * self.length / 2

    def SimpleLine(self):
        self.posMoment = self.lineLoad * self.length**2 / 8
        self.negMoment = 0
        self.shearForce = self.lineLoad * self.length / 2
