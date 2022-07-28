import math
import library

## 입력

# 1. Section
# BESTO Beam [U : H_u x B_u x t (mm)]
H_u = 600
B_u = 300
B_tf = 80
t = 12
# H Braket [H : H_s x H_s x t_w x t_f (mm)]
H_s = 800
B_s = 300
t_w = 14
t_f = 26
# 슬래브
d_s = 150   # 슬래브 두께
d_d = 0     # 데크 두께
# 철근
n_rt = 3        # 상부 철근 개수
D_rt = 'D25'    # 상부 철근 지름
n_rb = 2        # 하부 철근 개수
D_rb = 'D25'    # 하부 철근 지름
# 전단 연결재
h_a = 50        # 앵글의 높이
S_a = 300       # 전단연결재 간격

# 2. Material
F_y = 355           # 강재의 항복강도 [MPa]
F_r = 500           # 철근의 항복강도 [MPa]
E_s = 205000        # 강재의 탄성계수 [MPa]
f_ck = 24           # 콘크리트의 설계기준압축강도 [MPa]

# 3. Length and Spacing
length_U = 14500        # 보 길이 [mm]
length_H = 1500         # H브라켓 길이 [mm]
s1 = 10000              # 좌측 간격 [mm]
s2 = 10000              # 우측 간격 [mm]

# 4. Design Conditions
phi = 0.9                   # KBC2016 0709.3.2.1
endCondition = 'Pin-Pin'    # 'Fixed end', 'Fix-Pin', 'Fix-Free'
beamSupport = False
deckSupport = False

# 5. Design Loads
DL_finish = 2.6         # 마감하중 [kN/m^2]
LL_per = 5              # 활하중   [kN/m^2]
LL_con = 1.5            # 시공하중 [kN/m^2]

## 계산

# U 단면
topF1 = library.SquareSectionProperties(H=t, B=B_tf, x=B_tf/2, y=H_u-t/2)
topF2 = library.SquareSectionProperties(H=t, B=B_tf, x=B_tf+B_u+B_tf/2, y=H_u-t/2)
web1 = library.SquareSectionProperties(H=H_u, B=t, x=B_tf+t/2, y=H_u/2)
web2 = library.SquareSectionProperties(H=H_u, B=t, x=B_tf+B_u-t/2, y=H_u/2)
bottomFlange_U = library.SquareSectionProperties(H=t, B=B_u-2*t, x=B_tf+B_u/2, y=t/2)
U_section = library.CombinedSectionProperties(topF1, topF2, web1, web2, bottomFlange_U)
W_U_Section = U_section.area/10**6 * 78.5   # 단위길이당 하중 [kN/m]   강재의 단위중량 78.5 kN/m3
A_s = U_section.area
y_s = U_section.centerY
I_x_U = U_section.inertiaX
P_y = U_section.area* F_y

plasticSecCoef = library.PlasticSectionCoefficient([topF1, topF2, bottomFlange_U], [web1, web2]).plasticSecCoef

# H 단면
topFlange = library.SquareSectionProperties(H=t_f, B=B_s, x=(B_s/2), y=(H_s-t_f/2))
web = library.SquareSectionProperties(H=(H_s-2*t_f), B=t_w, x=(B_s/2), y=(H_s/2))
bottomFlange_H = library.SquareSectionProperties(H=t_f, B=B_s, x=(B_s/2), y=(t_f/2))
H_section = library.CombinedSectionProperties(topFlange, web, bottomFlange_H)
W_H_section = H_section.area/10**6 * 78.5   # 단위길이당 하중 [kN/m]   강재의 단위중량 78.5 kN/m3

# 콘크리트 단면
E_c = 8500*(f_ck + library.delta_f(f_ck))**(1/3)         # 콘크리트의 탄성계수 [MPa] KBC 식(0503.4.2)
b_eff = library.EffectiveWidth(span=length_U, bay=s1) + library.EffectiveWidth(span=length_U, bay=s2)         #유효폭
concInU = library.SquareSectionProperties(H=(H_u-t), B=(B_u-2*t), x=(B_tf+B_u/2), y=(H_u-t)/2+t)
concSlab = library.SquareSectionProperties(H=d_s, B=b_eff, x=B_tf+B_u/2, y=(H_u+d_s/2))
concInDeck = library.SquareSectionProperties(H=(d_d-t) if d_d>=t else 0, B=(B_u-2*t), x=(B_tf+B_u/2), y=(H_u+(d_d-t)/2))
concSection = library.CombinedSectionProperties(concInU, concSlab, concInDeck)
W_concSection = concSection.area/10**6 * 24 # 단위길이당 하중 [kN/m]    철근콘크리트 단위중량 24kN/m3
A_c = concSection.area      # 전제 콘크리트 단면적
y_c = concSection.centerY   # 전체 콘크리트 단면 도심 from 하부
I_c = concSection.inertiaX  # 전체 콘크리트 단면 Ixx

# 합성단면
E_scr = E_s / E_c   # 강재/콘크리트 탄성계수비
U_section.locationX = U_section.centerX
U_section.locationY = U_section.centerY
tranConcSection = concSection
tranConcSection.area = concSection.area / E_scr
tranConcSection.inertiaX = concSection.inertiaX / E_scr
tranConcSection.locationX = concSection.centerX
tranConcSection.locationY = concSection.centerY
compositeSection = library.CombinedSectionProperties(U_section, tranConcSection)
I_com = compositeSection.inertiaX # 완전합성환산단면 Ixx


# 하부철근
A_rb = library.A_r_table[D_rb] * n_rb   # 하부 철근 총단면적
P_rb = A_rb * F_r

# 전단연결재(L-앵글)
F_a = 31000 * h_a**(3/4) * f_ck**(2/3) / B_u**(1/2)     # 전단연결재 1개의 강도 [N]  / 실험결과 반영
N_a = math.floor(length_U / S_a)    # 전단연결재 개수
Q_n = F_a * N_a

# U단면 판폭두께비 검토
WTR_topFlange = library.WTRatio(width=B_tf, thickness=t, E_s=E_s, F_y=F_y)
WTR_Web = library.WTRatio(width=H_u, thickness=t, E_s=E_s, F_y=F_y)
WTR_bottomFlange = library.WTRatio(width=B_u, thickness=t, E_s=E_s, F_y=F_y)
print('Top Flange is ', WTR_topFlange.TopFlange())
print('Web is ', WTR_Web.Web())
print('Bottom Flange is ', WTR_bottomFlange.BottomFlange())

# 콘크리트 압축력 KBC2016 0709.3.2.1
C1 = P_y + P_rb                     # 강재+철근의 인장강도
C2 = 0.85 * f_ck * concSlab.area    # 콘크리트 슬래브 압축강도
C3 = Q_n                            # 전단연결재 강도
C = min(C1, C2, C3)                 # 콘크리트 슬래브의 압축력 산정
a = C / (0.85 * f_ck * b_eff)       # 압축블럭의 깊이

# 합성률
compositeRatio = 1
if (min(C1,C2)>Q_n):
    compositeRatio = Q_n/min(C1,C2)
print('합성률: {:.0%}'.format(compositeRatio))

# 단위길이당 하중
W_L = (s1+s2)/2/1000 * LL_per               # 활하중 [kN/m]
W_D1 = W_concSection + W_U_Section          # 고정하중(데크플레이트, 토핑콘크리트, 강재보) [kN/m]
W_D2 = (s1+s2)/2/1000 * DL_finish           # 고정하중(콘크리트 양생 후 마감에 의한 고정하중) [kN/m]
W_C = (s1+s2)/2/1000 * LL_con               # 시공시 하중 [kN/m]

# 처짐 검토
I_equiv = I_x_U + (compositeRatio)**(1/2) * (I_com-I_x_U)    # 불완전합성보 유효단면2차모멘트 / 완전합성일 경우 I_com과 같음
I_eff = 0.75 * I_equiv

if (endCondition == 'Fixed end'):   # 양단고정 wl^4/384EI
    endConditionCoefficient = 1
elif (endCondition == 'Pin-Pin'):   # 단순보 5wl^4/384EI
    endConditionCoefficient = 5
elif (endCondition == 'Fix-Pin'):   # 고정+힌지 wl^4/185EI
    endConditionCoefficient = 384/185
elif (endCondition == 'Fix-Free'):  # 캔틸레버 wl^4/8EI
    endConditionCoefficient = 384/8

delta_C = endConditionCoefficient * (W_C*length_U**4) / (384*E_s*I_x_U)
delta_L = endConditionCoefficient * (W_L*length_U**4) / (384*E_s*I_eff)
delta_DL_NS = endConditionCoefficient * ((W_D1*length_U**4)/(384*E_s*I_x_U) + ((W_D2+W_L)*length_U**4)/(384*E_s*I_eff))
delta_DL_S = endConditionCoefficient * ((W_D1+W_D2+W_L)*length_U**4)/(384*E_s*I_eff)

if (delta_C <= 40):
    print('시공시 하중에 의한 처짐 = ', round(delta_C,1), '<', 40, 'OK')
else:
    print('시공시 하중에 의한 처짐 = ', round(delta_C,1), '>', 40, 'NG')

if (delta_L <= length_U/360):
    print('활하중에 의한 처짐 = ', round(delta_L,1), '<', round(length_U/360,1), 'OK')
else:
    print('활하중에 의한 처짐 = ', round(delta_L,1), '>', round(length_U/360,1), 'NG')
    
if (delta_DL_S <= length_U/250):
    print('고정하중과 활하중에 의한 처짐 / support = ', round(delta_DL_S,1), '<', round(length_U/250,1), 'OK')
else:
    print('고정하중과 활하중에 의한 처짐 / support = ', round(delta_DL_S,1), '>', round(length_U/250,1), 'NG')
    
if (delta_DL_NS <= length_U/250):
    print('고정하중과 활하중에 의한 처짐 / N_support = ', round(delta_DL_NS,1), '<', round(length_U/250,1), 'OK')
else:
    print('고정하중과 활하중에 의한 처짐 / N_support = ', round(delta_DL_NS,1), '>', round(length_U/250,1), 'NG')


# 진동 검토
P_o = {'사무실': 0.29, '쇼핑몰': 0.29, '육교(실내)': 0.41, '육교(실외)': 0.41}
beta = {'사무실': 0.03, '쇼핑몰': 0.02, '육교(실내)': 0.01, '육교(실외)': 0.01}
accRatioLimit = {'사무실': 0.005, '쇼핑몰': 0.015, '육교(실내)': 0.015, '육교(실외)': 0.05}
g = 9.81    # 중력가속도 [m/sec^2]
W = 2000
f_n = 0.18 * (g*1000 / delta_L)**(1/2)
accRatio = P_o['사무실'] * math.exp(-0.35*f_n) / (beta['사무실'] * W)
if (accRatio < accRatioLimit['사무실']):
    print('바닥진동 검토: OK')
else:
    print('바닥진동 검토: NG')



# [KBC2016 해그림 0709.3.3] 정모멘트 산정용 소성응력분포
d1 = d_s - a/2
d2 = 0
if (P_y > C):
    d2 = (C/(0.85*f_ck*b_eff) - d_s) / 2
d3 = H_u - y_s

# 정모멘트 휨강도 산정
if (WTR_Web.Web() == 'Compact'):      # 0709.3.2.1 정모멘트에 대한 휨강도
    print('소성모멘트강도')
    # KBC2016 (해 0709.3.10)
    momentStrength = C * (d1 + d2) + P_y * (d3 - d2) + A_rb * F_r * (H_u - d2 - 33)
else:
    print('항복모멘트강도로 계산필요. 계산된 값은 소성모멘트임!!')
    momentStrength = C * (d1 + d2) + P_y * (d3 - d2)          # <== 추후 수정 필요!!

designMomentSterngth = phi * momentStrength

print(round(designMomentSterngth/1000000, 2), 'kN-m')
