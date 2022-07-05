# H형강의 전단강도
# KBC2016 0707.2.1 공칭전단강도

# Fy : 재료 항복강도 [MPa]
# E : 재료 탄성계수
# H : H x B x t_w x t_f [mm]
# phi : 강도감소계수
# phi_v V_n = phi_v (0.6 F_y) A_w C_v

import math


F_y = 355
E = 210000
H = 200
B = 200
tw = 10
tf = 20

yieldStrength = 355
shearCoefficient = 1


def ShearPhi():
    if (H/tf <= 2.24*math.sqrt(E/F_y)):
        phi = 1.0
    elif():
        phi = 0.9
    return phi


phi = {'shear': ShearPhi()}


def ShearCoefficient():
    if (H/tf <= 2.24*math.sqrt(E/F_y)):
        shearCoefficient = 1
    elif():
        shearCoefficient = 0.5
    return shearCoefficient


def WebArea():
    A_w = H * tw
    return A_w


def ShearStrength():
    V_n = 0.6 * yieldStrength * WebArea() * ShearCoefficient()
    return V_n


def DesignShearStrength():
    phiV_n = ShearStrength() * phi['shear']
    return phiV_n


print(DesignShearStrength())
