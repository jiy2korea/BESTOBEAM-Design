# 전단력 (kN, mm)

def shearForce (*,load, length, location): # keyword argument 사용
    # wL/2 - wx
    V_x = (load * length / 2) - (load * location)
    return V_x