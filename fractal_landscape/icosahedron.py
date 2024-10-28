import sympy as sp

alpha, beta, gamma = sp.symbols('alpha beta gamma')
alpha_val = 2 * sp.pi / 5
x = (1/sp.sin(alpha/2))
beta_in_alpha = (sp.pi-2*sp.asin(x)).simplify()
gamma_in_alpha = (sp.pi - beta_in_alpha).simplify()
gamma_in_beta = sp.pi - beta
beta_val = beta_in_alpha.subs(alpha,alpha_val).simplify()
gamma_val = (sp.pi - beta_val).simplify()


icosahedron_coords = [ # theta, phi
    (0, 0),
    *((sp.pi-gamma, 0+i*alpha) for i in range(5)),
    *((gamma, alpha/2+i*alpha) for i in range(5)),
    (sp.pi, 0)
]
icosahedron_coords = [
    (
        theta.simplify() if isinstance(theta, sp.Expr) else theta,
        phi.simplify() if isinstance(phi, sp.Expr) else phi
    )
    for (theta, phi) in icosahedron_coords
]

