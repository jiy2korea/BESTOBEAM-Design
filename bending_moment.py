# 휨모멘트 (kN, mm)

def bendingMoment (*,load, length, location): # keyword argument 사용
    # wLx/2 - wx^2/2
    M_x = (load * length * location / 2 ) - (load * location**2 / 2)
    return M_x