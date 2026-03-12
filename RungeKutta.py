from EquationDIff import dC_dt
def runge_kutta(f, t0, C0, h, n):
    resultats = []
    t = t0
    C = C0
    if C == None:
        C = 0
    for _ in range(n):
        k1 = h * f(t, C)
        k2 = h * f(t + h/2, C + k1/2)
        k3 = h * f(t + h/2, C + k2/2)
        k4 = h * f(t + h, C + k3)
        C += (k1 + 2*k2 + 2*k3 + k4) / 6
        t += h
        resultats.append((t, C))
    return resultats

