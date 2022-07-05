# s1: 좌측경간
# s2: 우측경간
# legnth: 보 길이
# uniformLoad: 등분포 선하중
# location: 하중을 계산할 위치
# deadLoad_Slab: 바닥판 자중
# deadLoad_Topping: 바닥판 마감
# liveLoad_Const.: 시공하중
# liveLoad_Use: 용도별 활하중


# 바닥하중을 보하중으로
def floorLoadToBeamLoad(*, s1, s2, length):  # keyword argument 사용
    uniformLoad = (s1 + s2) * length
    return uniformLoad


# 휨모멘트 (kN, mm)
def bendingMoment(*, uniformLoad, length, location):  # keyword argument 사용
    # wLx/2 - wx^2/2
    M_x = (uniformLoad * length * location / 2) - \
        (uniformLoad * location**2 / 2)
    return M_x


# 전단력 (kN, mm)
def shearForce(*, uniformLoad=0, pointLoad=0, pointLoadLocationRatio=0.5, length, location):  # keyword argument 사용
    if uniformLoad != 0 and pointLoad != 0:
        print('에러!!: uniformLoad와 pointLoad가 둘 다 값이 있습니다.')
    
    elif uniformLoad != 0:
        # wL/2 - wx
        V_x = (uniformLoad * length / 2) - (uniformLoad * location)
        return V_x

    elif pointLoad != 0:
        # Va = P(1-r), Vb = Pr
        Va = pointLoad * (1 - pointLoadLocationRatio)
        Vb = pointLoad * pointLoadLocationRatio
        return [Va, Vb]
        


# 설계전단력 Vd (kN, mm)
def designShearForce(*, uniformLoad, length):
    # wL/2
    designShearForce = shearForce(
        uniformLoad=uniformLoad, length=length, location=0)
    return designShearForce


# 설계휨모멘트 Md (kN, mm)
def designBendingMoment(*, uniformLoad, length):
    # wL^2/8
    designBendingMoment = bendingMoment(
        uniformLoad=uniformLoad, length=length, location=length/2)
    return designBendingMoment


print(shearForce(pointLoad=100, uniformLoad=10, length=5, location=0, pointLoadLocationRatio=0.2))
