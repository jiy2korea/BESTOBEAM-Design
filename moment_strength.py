# BESTOBEAM의 휨강도 산정

import math

A_r_table = {'D10': 71.3, 'D13': 126.7, 'D16': 198.6,
       'D19': 286.7, 'D22': 387.1, 'D25': 507.7}    # 철근 단면적 [mm2]

phi = 0.9           # KBC2016 0709.3.2.1

endCondition = 'Pin-Pin'  # 'Fixed end', 'Fix-Pin', 'Fix-Free'

W_L = 50            # 활하중 [kN/m]
W_D1 = 41.4         # 고정하중(데크플레이트, 토핑콘크리트, 강재보) [kN/m]
W_D2 = 31           # 고정하중(콘크리트 양생 후 마감에 의한 고정하중) [kN/m]
W_C = 56.4          # 시공시 하중

# 재료
F_y = 355           # 강재의 항복강도 [MPa]
F_r = 500           # 철근의 항복강도 [MPa]
E_s = 205000        # 강재의 탄성계수 [MPa]
E_c = 25811         # 콘크리트의 탄성계수 [MPa]
f_ck = 24           # 콘크리트의 설계기준압축강도 [MPa]

E_scr = E_s / E_c   # 강재/콘크리트 탄성비

# 강재단면          U : H_s x B_s x t [mm]
H_s = 600
B_s = 300
B_tf = 80
t = 12
A_st = 2 * B_tf * t             # 상부 플랜지 면적
A_sw = 2 * H_s * t              # 웨브 면적
A_sb = (B_s-2*t) * t            # 하부 플랜지 면적
A_s = A_st + A_sb + A_sw        # 강재 전체 단면적
y_s = (A_st*(H_s-t/2) + A_sw*H_s/2 + A_sb*t/2) / A_s  # U단면 도심 위치 from 하부
I_st = 2 * (B_tf*t**3) / 12     # 상부 플랜지 Ixx
I_sw = 2 * (t*H_s**3) / 12      # 웨브 Ixx
I_sb = (B_s-2*t)*t**3 /12       # 하부 플랜지 Ixx
I_s = (I_st + A_st*(H_s-t/2-y_s)**2) + (I_sw + A_sw*(H_s/2-y_s)**2) + (I_sb + A_sb*(t/2-y_s)**2)    # 강재 전체 단면 Ixx
P_y = A_s* F_y                  # 강재단면의 인장강도

# 하부철근
n_rb = 2                        # 하부 철근 개수
D_rb = 'D25'                    # 하부 철근 지름
A_rb = A_r_table[D_rb] * n_rb   # 하부 철근 총단면적
P_rb = A_rb * F_r

span = 14500                    # 보스팬

# 전단연결재(L-앵글)
h_a = 50                        # 앵글의 높이
F_a = 31000 * h_a**(3/4) * f_ck**(2/3) / \
    B_s**(1/2)                  # 전단연결재 1개의 강도 [N]  / 실험결과 반영
S_a = 300                       # 전단연결재 간격
N_a = math.floor(span / S_a)    # 전단연결재 개수
Q_n = F_a * N_a

class WTRatio ():

    def __init__(self, *, width, thickness) -> None:
        self.width = width
        self.thickness = thickness

        self.judgment = ''

    def Judgment(self):
        if (self.w_t_Ratio <= self.lambda_p):
            return 'Compact'
        elif (self.w_t_Ratio <= self.lambda_r):
            return 'NonCompact'
        else:
            return 'Slender'

    def TopFlange(self):        # KBC2016 <표 0702.4.1> (5)
        self.lambda_p = 0.54 * (E_s/F_y)**(1/2)
        self.lambda_r = 0.91 * (E_s/F_y)**(1/2)
        self.w_t_Ratio = self.width / self.thickness
        return self.Judgment()

    def Web(self):              # KBC2016 <표 0702.4.1> (9)
        self.lambda_p = 3.76 * (E_s/F_y)**(1/2)
        self.lambda_r = 5.70 * (E_s/F_y)**(1/2)
        self.w_t_Ratio = (self.width-2*self.thickness) / \
            self.thickness  # 순수 웨브 높이
        return self.Judgment()

    def BottomFlange(self):     # KBC2016 <표 0702.4.1> (12)
        self.lambda_p = 1.12 * (E_s/F_y)**(1/2)
        self.lambda_r = 1.40 * (E_s/F_y)**(1/2)
        self.w_t_Ratio = (self.width-2*self.thickness) / \
            self.thickness  # 순수 플렌지 폭
        return self.Judgment()


WTR_topFlange = WTRatio(width=B_tf, thickness=t)
WTR_Web = WTRatio(width=H_s, thickness=t)
WTR_bottomFlange = WTRatio(width=B_s, thickness=t)

print('Top Flange is ', WTR_topFlange.TopFlange())
print('Web is ', WTR_Web.Web())
print('Bottom Flange is ', WTR_bottomFlange.BottomFlange())


S1 = 10000                      # s1: 좌측경간
S2 = 10000                      # s2: 우측경간
d_s = 150                       # 슬래브 두께

def EffectiveWidth(*, span, bay):          # KBC2016 0709.3.1.1 유효폭
    b1 = span / 8
    b2 = bay / 2
    # b3 = "보 중심선에서 슬래브 가장자리까지의 거리"       <== 추후 구현
    return min(b1, b2)

b_eff = EffectiveWidth(span=span, bay=S1) + \
    EffectiveWidth(span=span, bay=S2)                   # 슬래프 유효폭
A_cs = b_eff*d_s                                        # 콘크리트 슬래브 단면적 (유효폭 내)
A_cb = (B_s-2*t)*(H_s-t)                                # U 내부 콘크리트 단면적
I_cs = (b_eff*d_s**3)/12                                # 콘크리트 슬래브 Ixx
I_cb = ((B_s-2*t)*(H_s-t)**3)/12                        # U 내부 콘크리트 Ixx
A_c = A_cs + A_cb                                       # 전제 콘크리트 단면적
y_c = (A_cs*(H_s+d_s/2) + A_cb*((H_s-t)/2+t)) / (A_cs+A_cb) # 전체 콘크리트 단면 도심 from 하부
I_c = (I_cs + A_cs*(H_s+d_s/2 - y_c)**2) + (I_cb + A_cb*((H_s-t)/2+t - y_c)**2) # 전체 콘크리트 단면 Ixx

A_ctr = A_c / E_scr                                     # 콘크리트 to 강재 환산단면적
I_ctr = I_c / E_scr                                     # 콘크리트 to 강재 환산단면 Ixx

y_com = (A_s*y_s + A_c/E_scr*y_c) / (A_s+A_c/E_scr)                 # 완전합성환산단면 도심 from 하부
I_com = (I_s + A_s*(y_s-y_com)**2) + (I_ctr + A_ctr*(y_c-y_com)**2) # 완전합성환산단면 Ixx


# 콘크리트 압축력 KBC2016 0709.3.2.1
C1 = P_y + P_rb                 # 강재+철근의 인장강도
C2 = 0.85 * f_ck * A_cs         # 콘크리트 슬래브 압축강도
C3 = Q_n                        # 전단연결재 강도
C = min(C1, C2, C3)             # 콘크리트 슬래브의 압축력 산정
a = C / (0.85 * f_ck * b_eff)   # 압축블럭의 깊이

compositeRatio = 1
if (min(C1,C2)>Q_n):
    compositeRatio = Q_n/min(C1,C2)
    
print('합성률: {:.0%}'.format(compositeRatio))

# 처짐 검토
I_equiv = I_s + (compositeRatio)**(1/2) * (I_com-I_s)    # 불완전합성보 유효단면2차모멘트 / 완전합성일 경우 I_com과 같음
I_eff = 0.75 * I_equiv

delta_C = (W_C*span**4) / (384*E_s*I_s)
delta_L = (W_L*span**4) / (384*E_s*I_eff)
delta_DL_NS = (W_D1*span**4)/(384*E_s*I_s) + ((W_D2+W_L)*span**4)/(384*E_s*I_eff)
delta_DL_S = ((W_D1+W_D2+W_L)*span**4)/(384*E_s*I_eff)


if (endCondition == 'Fixed end'):   # 양단고정 wl^4/384EI
    pass
elif (endCondition == 'Pin-Pin'):   # 단순보 5wl^4/384EI
    delta_C = 5 * delta_C
    delta_L = 5 * delta_L
    delta_DL_NS = 5 * delta_DL_NS
    delta_DL_S = 5 * delta_DL_S
elif (endCondition == 'Fix-Pin'):   # 고정+힌지 wl^4/185EI
    delta_C = 384/185 * delta_C
    delta_L = 384/185 * delta_L
    delta_DL_NS = 384/185 * delta_DL_NS
    delta_DL_S = 384/185 * delta_DL_S
elif (endCondition == 'Fix-Free'):  # 캔틸레버 wl^4/8EI
    delta_C = 384/8 * delta_C
    delta_L = 384/8 * delta_L
    delta_DL_NS = 384/8 * delta_DL_NS
    delta_DL_S = 384/8 * delta_DL_S

if (delta_C <= 40):
    print('시공시 하중에 의한 처짐 = ', round(delta_C,1), '<', 40, 'OK')
else:
    print('시공시 하중에 의한 처짐 = ', round(delta_C,1), '>', 40, 'NG')

if (delta_L <= span/360):
    print('활하중에 의한 처짐 = ', round(delta_L,1), '<', round(span/360,1), 'OK')
else:
    print('활하중에 의한 처짐 = ', round(delta_L,1), '>', round(span/360,1), 'NG')
    
if (delta_DL_S <= span/250):
    print('고정하중과 활하중에 의한 처짐 / support = ', round(delta_DL_S,1), '<', round(span/250,1), 'OK')
else:
    print('고정하중과 활하중에 의한 처짐 / support = ', round(delta_DL_S,1), '>', round(span/250,1), 'NG')
    
if (delta_DL_NS <= span/250):
    print('고정하중과 활하중에 의한 처짐 / N_support = ', round(delta_DL_NS,1), '<', round(span/250,1), 'OK')
else:
    print('고정하중과 활하중에 의한 처짐 / N_support = ', round(delta_DL_NS,1), '>', round(span/250,1), 'NG')


# 진동 검토
P_o = {'사무실': 0.29, '쇼핑몰': 0.29, '육교(실내)': 0.41, '육교(실외)': 0.41}
beta = {'사무실': 0.03, '쇼핑몰': 0.02, '육교(실내)': 0.01, '육교(실외)': 0.01}
accRatioLimit = {'사무실': 0.005, '쇼핑몰': 0.015, '육교(실내)': 0.015, '육교(실외)': 0.05}
g = 9.81    # 중력가속도 [m/sec^2]
W = 2000
f_n = 0.18 * (g / delta_L)**(1/2)
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
d3 = H_s - y_s

# 정모멘트 휨강도 산정
if (WTR_Web.Web() == 'Compact'):      # 0709.3.2.1 정모멘트에 대한 휨강도
    print('소성모멘트강도')
    # KBC2016 (해 0709.3.10)
    momentStrength = C * (d1 + d2) + P_y * (d3 - d2) + A_rb * F_r * (H_s - d2 - 33)
else:
    print('항복모멘트강도로 계산필요. 계산된 값은 소성모멘트임!!')
    momentStrength = C * (d1 + d2) + P_y * (d3 - d2)          # <== 추후 수정 필요!!

designMomentSterngth = phi * momentStrength

print(round(designMomentSterngth/1000000, 2), 'kN-m')
