# BESTOBEAM의 전단강도
# KBC2016 0707.2.1 공칭전단강도

# phi_v V_n = phi_v (0.6 F_y) A_w C_v

import math

# 재료
yieldStrength = 355         # Fy : 강재 항복강도 [MPa]
elasticModulus = 205000     # E : 강재 탄성계수

# 단면          U : H_u x B_u x t [mm]
H_u = 600
B_u = 300
B_t = 80
t = 12

shearCoefficient = 1
webBucklingCoefficient = 5      #k_v : 웨브판좌굴계수 KBC2016 식(0707.2.5)


def WidthToThicknessRatio():    # h/tw : 판폭두께비
    r = (H_u-2*t) / t
    return r

def ShearPhi():                 # phi : 강도감소계수
    if (WidthToThicknessRatio() <= 2.24*math.sqrt(elasticModulus/yieldStrength)):
        phi = 1.0
    else:
        phi = 0.9
    return phi


phi = {'shear': ShearPhi()}


def ShearCoefficient():         # C_v : 전단상수 KBC2016 0707.2.1
    if (WidthToThicknessRatio() <= 2.24*math.sqrt(elasticModulus/yieldStrength)):
        print('전단항복')
        shearCoefficient = 1
    elif (WidthToThicknessRatio() <= 1.10*math.sqrt(webBucklingCoefficient*elasticModulus/yieldStrength)):
        print(1.10*math.sqrt(webBucklingCoefficient*elasticModulus/yieldStrength))
        print('전단항복')
        shearCoefficient = 1
    elif (1.10*math.sqrt(webBucklingCoefficient*elasticModulus/yieldStrength) < WidthToThicknessRatio() <= 1.37*math.sqrt(webBucklingCoefficient*elasticModulus/yieldStrength)):
        print(1.37*math.sqrt(webBucklingCoefficient*elasticModulus/yieldStrength))
        print('비탄성좌굴')
        shearCoefficient = 1.10 * math.sqrt(webBucklingCoefficient*elasticModulus/yieldStrength) / WidthToThicknessRatio()
    else:
        print('탄성좌굴')
        shearCoefficient = 1.51 * elasticModulus * webBucklingCoefficient / (WidthToThicknessRatio()**2 * yieldStrength)
    return shearCoefficient


def ShearArea():                # 전단면적
    A_s = H_u * t *2
    return A_s


def ShearStrength():            # 전단강도
    V_n = 0.6 * yieldStrength * ShearArea() * ShearCoefficient()
    return V_n


def DesignShearStrength():      # 설계전단강도
    phiV_n = ShearStrength() * phi['shear']
    return phiV_n


print(DesignShearStrength())
