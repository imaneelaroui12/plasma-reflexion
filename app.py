import math

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.patches import Circle
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Plasma et onde électromagnétique", page_icon="📡", layout="wide")

# Constantes SI. Les valeurs viennent du CODATA 2022.
C0 = 299_792_458.0
E_CHARGE = 1.602_176_634e-19
EPS0 = 8.854_187_8188e-12
M_E = 9.109_383_7139e-31
T0_K = 300.0

DEFAULTS = {
    "temp_k": 300,
    "freq_ghz": 2.45,
    "angle_deg": 30,
    "log_ne0": 17.0,
    "polarisation": "TE",
    "playing": False,
}


def reset_controls():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


def set_playing(value):
    st.session_state.playing = value


for state_key, state_value in DEFAULTS.items():
    st.session_state.setdefault(state_key, state_value)

st.title("Réflexion d'une onde électromagnétique sur un plasma")
st.caption("Mini-projet GSR1 — Imane Elaroui | Enseignant : El Mamouni")

with st.sidebar:
    st.header("Commandes")
    left, right = st.columns(2)
    left.button("Lecture", use_container_width=True, on_click=set_playing, args=(True,))
    right.button("Pause", use_container_width=True, on_click=set_playing, args=(False,))
    st.button("Réinitialiser", use_container_width=True, on_click=reset_controls)

    temp_k = st.slider(
        "Température commune T (K)",
        min_value=300,
        max_value=3000,
        step=50,
        key="temp_k",
    )
    freq_ghz = st.slider(
        "Fréquence de l'onde f (GHz)",
        min_value=0.5,
        max_value=10.0,
        step=0.05,
        key="freq_ghz",
    )
    angle_deg = st.slider(
        "Angle d'incidence θᵢ (°)",
        min_value=0,
        max_value=80,
        step=1,
        key="angle_deg",
    )
    log_ne0 = st.slider(
        "log₁₀ de la densité de référence Nₑ₀ (m⁻³)",
        min_value=15.0,
        max_value=19.0,
        step=0.1,
        key="log_ne0",
    )
    polarisation = st.radio(
        "Polarisation",
        options=["TE", "TM"],
        horizontal=True,
        key="polarisation",
    )
    st.caption("T₀ est fixé à 300 K. La densité de référence Nₑ₀ est réglable sur une échelle logarithmique.")

if st.session_state.playing:
    frame = st_autorefresh(interval=250, key="animation_refresh")
    phase = 2 * math.pi * (frame % 32) / 32
else:
    phase = 0.0

ne0 = 10 ** log_ne0
ne = ne0 * T0_K / temp_k
omega_p = math.sqrt(ne * E_CHARGE**2 / (EPS0 * M_E))
fp_hz = omega_p / (2 * math.pi)
freq_hz = freq_ghz * 1e9
omega = 2 * math.pi * freq_hz
epsilon_r = 1.0 - (omega_p / omega) ** 2
theta_i = math.radians(angle_deg)
cos_i = math.cos(theta_i)
sin_i = math.sin(theta_i)
q_squared = epsilon_r - sin_i**2
propagative = q_squared > 1e-10
q = complex(math.sqrt(q_squared), 0.0) if propagative else complex(0.0, math.sqrt(max(0.0, -q_squared)))


def fresnel(f_hz, electron_density, angle_radians, pol):
    """Coefficients de Fresnel vide -> plasma et coefficients de puissance."""
    omega = 2 * math.pi * f_hz
    omega_p = math.sqrt(electron_density * E_CHARGE**2 / (EPS0 * M_E))
    eps = 1.0 - (omega_p / omega) ** 2
    cos_inc = math.cos(angle_radians)
    sin_inc = math.sin(angle_radians)
    q2 = eps - sin_inc**2

    if q2 > 1e-10:
        qn = complex(math.sqrt(q2), 0.0)
        can_propagate = True
    else:
        qn = complex(0.0, math.sqrt(max(0.0, -q2)))
        can_propagate = False

    if pol == "TE":
        denominator = cos_inc + qn
        if abs(denominator) < 1e-14:
            r = 1.0 + 0.0j
            t = 0.0 + 0.0j
        else:
            r = (cos_inc - qn) / denominator
            t = 2 * cos_inc / denominator
    else:
        denominator = eps * cos_inc + qn
        if abs(denominator) < 1e-14:
            r = 1.0 + 0.0j
            t = 0.0 + 0.0j
        else:
            r = (eps * cos_inc - qn) / denominator
            n2 = complex(eps, 0.0) ** 0.5
            t = 2 * n2 * cos_inc / denominator

    reflectance = abs(r) ** 2
    if can_propagate:
        # Le rapport q/cos(theta_i) convertit |t|^2 en rapport de puissances.
        transmittance = qn.real / cos_inc * abs(t) ** 2
        transmittance = max(0.0, float(transmittance))
    else:
        # Un champ évanescent existe, mais son flux moyen normal est nul.
        reflectance = 1.0
        transmittance = 0.0

    return eps, r, t, reflectance, transmittance, can_propagate, qn


_, r_current, t_current, r_power, t_power, propagative, q_current = fresnel(
    freq_hz, ne, theta_i, polarisation
)
power_sum = r_power + t_power
critical_frequency_ghz = (fp_hz / cos_i) / 1e9

st.latex(r"N_e(T)=N_{e0}\frac{T_0}{T},\qquad \omega_p=\sqrt{\frac{N_e e^2}{\varepsilon_0m_e}},\qquad \varepsilon_r=1-\frac{\omega_p^2}{\omega^2}")
st.caption(f"Références affichées : T₀ = {T0_K:.0f} K ; Nₑ₀ = {ne0:.2e} m⁻³. Plasma homogène, non magnétisé, sans collisions et semi-infini.")

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Densité électronique Nₑ", f"{ne:.3e} m⁻³")
metric2.metric("Fréquence plasma fₚ", f"{fp_hz / 1e9:.3f} GHz")
metric3.metric("Permittivité relative εᵣ", f"{epsilon_r:.4f}")
metric4.metric("Seuil selon θᵢ : fₚ / cos θᵢ", f"{critical_frequency_ghz:.3f} GHz")

if propagative:
    theta_t = math.asin(max(-1.0, min(1.0, sin_i / math.sqrt(epsilon_r))))
    state_label = "Propagative"
    state_color = "green"
    theta_t_text = f"{math.degrees(theta_t):.1f}°"
else:
    theta_t = None
    state_label = "Évanescente"
    state_color = "orange"
    theta_t_text = "pas d'angle réfracté réel"

result_left, result_right = st.columns([1, 2])
with result_left:
    st.subheader("Résultat au réglage courant")
    st.write(f"**État dans le plasma :** {state_label}")
    if propagative:
        st.success("Le champ transmis se propage dans le plasma.")
    else:
        st.warning("Le champ dans le plasma est évanescent.")
    st.write(f"**Polarisation :** {polarisation}")
    st.write(f"**Angle transmis :** {theta_t_text}")
    st.metric("Puissance réfléchie R", f"{100 * r_power:.2f} %")
    st.metric("Puissance transmise T", f"{100 * t_power:.2f} %")
    st.metric("Somme R + T", f"{100 * power_sum:.2f} %")
    st.caption(f"Coefficient d'amplitude réfléchi : Γ = {r_current.real:.3f} {r_current.imag:+.3f}j")
    if not propagative:
        if epsilon_r > 0:
            st.info("εᵣ est positive, mais εᵣ < sin²(θᵢ) : l'angle empêche la propagation normale dans le plasma.")
        else:
            st.info("εᵣ ≤ 0 : le champ dans le plasma est évanescent dans ce modèle.")
    else:
        st.success("Le champ transmis se propage dans le plasma.")
    st.caption("Les pourcentages de puissance utilisent le flux normal, pas seulement le carré du coefficient d'amplitude.")

with result_right:
    st.subheader("Schéma de l'interface")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axvspan(0, 1.35, color="#eaf3fb", alpha=0.75, zorder=0)
    ax.axvline(0, color="#283747", lw=2)
    ax.text(-1.08, 0.88, "Vide", fontsize=12, color="#37474f")
    ax.text(0.82, 0.88, "Plasma", fontsize=12, color="#24618b")
    ax.annotate(
        "normale",
        xy=(0.50, 0.0),
        xytext=(0.20, -0.22),
        arrowprops={"arrowstyle": "->", "color": "#444"},
        fontsize=9,
    )
    ax.text(-0.83, -0.05, f"θᵢ = {angle_deg}°", fontsize=9)
    ax.text(-0.84, 0.42, f"TE / TM : {polarisation}", fontsize=9)

    def draw_wave(start, end, amplitude, color, phase_value, label, label_xy):
        start = np.asarray(start, dtype=float)
        end = np.asarray(end, dtype=float)
        direction = end - start
        length = np.linalg.norm(direction)
        if length <= 1e-9:
            return
        unit = direction / length
        perpendicular = np.array([-unit[1], unit[0]])
        along = np.linspace(0, 1, 240)
        centre = start[None, :] + along[:, None] * direction[None, :]
        ripple = amplitude * np.sin(12 * math.pi * along - phase_value)
        points = centre + ripple[:, None] * perpendicular[None, :]
        ax.plot(points[:, 0], points[:, 1], color=color, lw=2.2, zorder=4)
        arrow_index = 165
        ax.annotate(
            "",
            xy=points[arrow_index + 5],
            xytext=points[arrow_index],
            arrowprops={"arrowstyle": "->", "color": color, "lw": 1.6},
        )
        ax.text(label_xy[0], label_xy[1], label, color=color, fontsize=9, weight="bold")

    incident_start = (-0.98 * cos_i, -0.98 * sin_i)
    reflected_end = (-0.98 * cos_i, 0.98 * sin_i)
    draw_wave(incident_start, (0, 0), 0.035, "#d35400", phase, "Onde incidente", (-1.05, -0.48))
    draw_wave((0, 0), reflected_end, 0.035 * math.sqrt(r_power), "#8e44ad", -phase, "Onde réfléchie", (-1.06, 0.60))

    ax.annotate("", xy=(0.54, 0.0), xytext=(0.05, 0.0), arrowprops={"arrowstyle": "->", "color": "#222"})
    ax.text(0.44, 0.08, "n", fontsize=11)

    if propagative and theta_t is not None:
        transmitted_end = (1.12 * math.cos(theta_t), 1.12 * math.sin(theta_t))
        draw_wave(
            (0, 0),
            transmitted_end,
            0.035 * math.sqrt(max(t_power, 0.0)),
            "#168aad",
            phase,
            "Onde transmise",
            (0.30, -0.56),
        )
        ax.text(0.10, 0.22, f"θₜ = {math.degrees(theta_t):.1f}°", fontsize=9, color="#168aad")
    else:
        # Le plasma est semi-infini : on ne dessine pas de seconde interface.
        decay_strength = max(0.15, 2 * math.pi * math.sqrt(max(0.0, -q_squared)))
        depth = np.linspace(0, 1.0, 160)
        envelope = 0.44 * np.exp(-decay_strength * depth)
        ax.plot(depth, 0.02 + envelope, color="#168aad", lw=2.4)
        ax.plot(depth, 0.02 - envelope, color="#168aad", lw=1.0, ls="--")
        ax.text(0.28, 0.42, "Champ évanescent\ndécroissant", fontsize=9, color="#168aad")

    # Espacement des particules illustratif : d varie comme N_e^(-1/3).
    spacing = 0.13 * (temp_k / T0_K) ** (1 / 3)
    spacing = min(0.36, max(0.085, spacing))
    xs = np.arange(0.13, 1.25, spacing)
    ys = np.arange(-0.78, 0.78, spacing)
    if len(xs) and len(ys):
        px, py = np.meshgrid(xs, ys)
        ax.scatter(px, py, s=9, color="#4a90c2", alpha=0.28, zorder=1)
    ax.text(0.20, -0.91, "Particules : espacement illustratif, proportionnel à Nₑ⁻¹ᐟ³", fontsize=8, color="#3d6d8f")

    ax.set_xlim(-1.18, 1.38)
    ax.set_ylim(-1.02, 1.02)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Distance normale (échelle illustrative)")
    ax.set_yticks([])
    ax.grid(alpha=0.12)
    st.pyplot(fig, clear_figure=True)

st.subheader("Réflexion et transmission selon la fréquence")
frequencies_ghz = np.linspace(0.25, 10.0, 350)
curves = {}
for pol in ["TE", "TM"]:
    reflected = []
    transmitted = []
    for f_ghz in frequencies_ghz:
        _, _, _, rr, tt, _, _ = fresnel(
            f_ghz * 1e9, ne, theta_i, pol
        )
        reflected.append(100 * rr)
        transmitted.append(100 * tt)
    curves[pol] = (np.asarray(reflected), np.asarray(transmitted))

plot1, plot2 = st.columns(2)
with plot1:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(frequencies_ghz, curves["TE"][0], label="TE", color="#b03a2e")
    ax.plot(frequencies_ghz, curves["TM"][0], label="TM", color="#7d3c98")
    ax.axvline(freq_ghz, color="#222", ls="--", label="Réglage courant")
    ax.scatter([freq_ghz], [100 * r_power], color="#111", s=28, zorder=5)
    ax.set_title("Puissance réfléchie")
    ax.set_xlabel("Fréquence (GHz)")
    ax.set_ylabel("R (%)")
    ax.set_ylim(-3, 103)
    ax.grid(alpha=0.25)
    ax.legend()
    st.pyplot(fig, clear_figure=True)

with plot2:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(frequencies_ghz, curves["TE"][1], label="TE", color="#1f618d")
    ax.plot(frequencies_ghz, curves["TM"][1], label="TM", color="#148f77")
    ax.axvline(freq_ghz, color="#222", ls="--", label="Réglage courant")
    ax.scatter([freq_ghz], [100 * t_power], color="#111", s=28, zorder=5)
    ax.set_title("Puissance transmise")
    ax.set_xlabel("Fréquence (GHz)")
    ax.set_ylabel("T (%)")
    ax.set_ylim(-3, 103)
    ax.grid(alpha=0.25)
    ax.legend()
    st.pyplot(fig, clear_figure=True)

with st.expander("Relations utilisées et hypothèses"):
    st.markdown(
        """
        **Densité et pulsation plasma**
        
            N_e(T) = N_e0 × T0 / T
            ω_p = √(N_e e² / (ε0 m_e))
            f_p = ω_p / (2π)

        **Condition de propagation**
        
            q² = ε_r − sin²(θ_i)
        
        L'onde est propagative si q² > 0. Elle est évanescente si q² ≤ 0. Cela revient à demander f > f_p / cos(θ_i). Le cas évanescent porte un champ qui décroît dans le plasma, mais son flux moyen normal est nul dans ce modèle sans pertes.

        **Fresnel**
        
        Les coefficients TE et TM sont calculés pour une onde venant du vide. En propagation, le coefficient de puissance transmis utilise le rapport de flux q / cos(θ_i) multiplié par |t|². En évanescence, T = 0 et R = 1.
        
        La matière est modélisée comme un milieu semi-infini. Il n'y a pas de réflexion sur une face arrière, pas de champ magnétique externe, pas de collisions et pas d'absorption.
        """
    )
    st.write(
        f"Références constantes : e = {E_CHARGE:.10e} C, "
        f"ε₀ = {EPS0:.10e} F/m, mₑ = {M_E:.10e} kg, "
        f"c = {C0:.0f} m/s. T₀ = {T0_K:.0f} K."
    )

st.caption(
    "Imane Elaroui — GSR1 — Les particules et le schéma sont illustratifs; "
    "les calculs utilisent un plasma homogène semi-infini."
)
