import numpy as np
import pandas as pd
import streamlit as st
import CoolProp.CoolProp as cp

APP_TITLE = "Kälteträger Rechner"
APP_VERSION = "0.9.5V"

ROUGHNESS_ROWS = [
    ("Gezogene und gepresste Rohre aus Kupfer, Messing, Bronze, Aluminium, Glas oder Kunststoff", "neu, technisch glatt", "0.001 … 0.0015"),
    ("", "gebraucht", "0.010 … 0.0300"),
    ("Gummischlauch", "neu, handelsüblich", "0.0016"),
    ("Rohre aus Gusseisen", "neu, handelsüblich", "0.25 … 0.5"),
    ("", "angerostet", "1.00 … 1.5"),
    ("", "verkrustet", "1.50 … 3.0"),
    ("", "nach mehrjährigem Betrieb gereinigt", "0.30 … 1.5"),
    ("", "städtliche Kanalisation", "1.20"),
    ("Neue nahtlose Stahlrohre, gewalzt oder gezogen", "mit Walzhaut", "0.02 … 0.06"),
    ("", "gebeizt", "0.03 … 0.04"),
    ("", "bei engen Rohren", "… 0.10"),
    ("Neue längsgeschweisste Stahlrohre", "mit Walzhaut", "0.04 … 0.1"),
    ("", "leicht verkrustet", "1.00 … 1.5"),
    ("", "stark verkrustet", "2.00 … 4.0"),
    ("", "gebraucht und gereinigt", "0.15 … 0.2"),
    ("Neue Stahlrohre mit Überzug", "Metallspritzung", "0.08 … 0.09"),
    ("", "tauchverzinkt", "0.07 … 0.10"),
    ("", "handelsüblich verzinkt", "0.10 … 0.16"),
    ("", "bituminiert", "0.050"),
    ("", "zementiert", "0.180"),
    ("", "galvanisiert", "0.008"),
    ("Gebrauchte Stahlrohre", "gleichmässige Rostnarben", "0.15"),
    ("", "leichte Verkrustung", "0.15 … 0.4"),
    ("", "mittlere Verkrustung", "1.50"),
    ("", "starke Verkrustung", "2.00 … 4.0"),
    ("Asbest-Zementrohre", "neu, handelsüblich", "0.03 … 0.1"),
    ("Betonrohre, Druckstollen", "handelsüblich Glattstrich", "0.3 … 0.8"),
    ("", "handelsüblich mittelglatt", "1.0 … 2.0"),
    ("", "handelsüblich rau", "2.0 … 3.0"),
    ("", "mehrjähriger Betrieb mit Wasser", "0.2 … 0.3"),
    ("Neues Tonrohr", "Drainagerohr, gebrannt", "0.6 … 0.8"),
    ("", "aus rohen Tonziegeln", "9.0"),
    ("Medizinisches, Kälte- oder Heizungsgewinderohr", "neu, handelsüblich", "0.045"),
    ("Medizinisches, Kälte- oder Heizungsstahlrohr nahtlos", "neu, handelsüblich", "0.045"),
    ("Medizinisches, Kälte- oder Heizungskupferrohr", "neu, handelsüblich", "0.0005 … 0.0015"),
    ("Medizinisches, Kälte- oder Heizungspräzisionsstahlrohr", "neu, handelsüblich", "0.001 … 0.0015"),
    ("Medizinisches, Kälte- oder Heizungskunststoffrohr", "neu, handelsüblich", "0.001 … 0.0015"),
]

LIMITS_ROWS = [
    ("Wasser", "100 %", "ohne Konzentrationsauswahl"),
    ("Antifrogen N", "10 bis 60 %", "zulässiger Eingabebereich"),
    ("Antifrogen L", "10 bis 60 %", "zulässiger Eingabebereich"),
    ("Kaliumformiat", "40 bis 100 %", "zulässiger Eingabebereich"),
]

st.set_page_config(page_title=APP_TITLE, layout="wide", page_icon="logo.png")


def friction_coefficient(di, w, nu, k):
    lambda_result = 0.02
    Re = di * w / nu
    k = k / 1e3
    epsilon_k = k / di
    lambda_hagenpoiseulle = 64 / Re
    lambda_blasius = 0.3164 / Re**0.25
    lambda_nikuradse = (-2 * np.log10(k / 3.71 / di)) ** -2
    lambda_prandtl = 0.02
    for _ in range(10):
        lambda_prandtl = (2 * np.log10(Re * np.sqrt(lambda_prandtl))) ** -2
    lambda_colebrookwhite = 0.02
    for _ in range(10):
        lambda_colebrookwhite = (-2 * np.log10(2.51 / Re / lambda_colebrookwhite + k / 3.71 / di)) ** -2
    check_moody_diagram = Re * np.sqrt(lambda_nikuradse) * k / di
    if Re < 2320:
        lambda_result = lambda_hagenpoiseulle
    elif check_moody_diagram >= 200:
        lambda_result = lambda_nikuradse
    elif epsilon_k < 0.001 and Re < 10000:
        lambda_result = lambda_blasius
    elif epsilon_k < 0.0002 and Re < 100000:
        lambda_result = lambda_blasius
    elif epsilon_k < 0.00002 and Re < 1000000:
        lambda_result = lambda_prandtl
    elif epsilon_k < 0.00001:
        lambda_result = lambda_prandtl
    else:
        lambda_result = lambda_colebrookwhite
    return lambda_result


def build_fluid(name, concentration):
    if name == "Wasser":
        return "INCOMP::Water", "Wasser", 100
    if name == "Antifrogen N":
        return f"INCOMP::AN[{concentration * 1e-2}]", f"Antifrogen N {concentration} %", concentration
    if name == "Antifrogen L":
        return f"INCOMP::AL[{concentration * 1e-2}]", f"Antifrogen L {concentration} %", concentration
    if name == "Kaliumformiat":
        return f"INCOMP::AKF[{concentration * 1e-2}]", f"Kaliumformiat {concentration} %", concentration
    raise ValueError(f"Unbekanntes Fluid: {name}")


def safe_freeze_temp(coolant_name, fluid, atmospheric_pressure):
    if coolant_name == "Wasser":
        return 273.15
    try:
        return cp.PropsSI("T_freeze", "T", 0, "P", atmospheric_pressure, fluid)
    except Exception:
        return np.nan


def build_csv_bytes(df):
    csv_body = df.to_csv(index=False, sep=";")
    header_line = f"{APP_TITLE};{APP_VERSION}"
    return (header_line + "\n" + csv_body).encode("utf-8-sig")


def run_calculation(inputs):
    project = inputs["project"]
    coolant_1 = inputs["coolant_1"]
    coolant_2 = inputs["coolant_2"]
    concentration_1 = inputs.get("concentration_1", 100)
    concentration_2 = inputs.get("concentration_2", 100)
    V_or_Q = inputs["V_or_Q"]
    volume_flow_coolant_1 = inputs.get("volume_flow_coolant_1", 0.0)
    heat_capacity = inputs.get("heat_capacity", 0.0)
    pressure_drop_coolant_1 = inputs["pressure_drop_coolant_1"]
    roughness = inputs["roughness"]
    mean_temperature = inputs["mean_temperature"]
    temperature_difference = inputs["temperature_difference"]
    mean_inner_pipe_diameter = inputs["mean_inner_pipe_diameter"]
    atmospheric_pressure = 1.01325 * 1e5
    fluid_1, name_1, concentration_1 = build_fluid(coolant_1, concentration_1)
    fluid_2, name_2, concentration_2 = build_fluid(coolant_2, concentration_2)
    mean_temperature = mean_temperature + 273.15
    volume_flow_coolant_1 = volume_flow_coolant_1 / 3.6 * 1e-3
    heat_capacity = heat_capacity * 1e3
    mean_inner_pipe_diameter = mean_inner_pipe_diameter * 1e-3
    pressure_drop_coolant_1 = pressure_drop_coolant_1 * 1e5
    density_coolant_1 = cp.PropsSI("D", "T", mean_temperature, "P", atmospheric_pressure, fluid_1)
    spec_heat_coolant_1 = cp.PropsSI("C", "T", mean_temperature, "P", atmospheric_pressure, fluid_1)
    dynamic_viscosity_coolant_1 = cp.PropsSI("V", "T", mean_temperature, "P", atmospheric_pressure, fluid_1)
    kinematic_viscosity_coolant_1 = dynamic_viscosity_coolant_1 / density_coolant_1
    T_freeze_coolant_1 = safe_freeze_temp(coolant_1, fluid_1, atmospheric_pressure)
    density_coolant_2 = cp.PropsSI("D", "T", mean_temperature, "P", atmospheric_pressure, fluid_2)
    spec_heat_coolant_2 = cp.PropsSI("C", "T", mean_temperature, "P", atmospheric_pressure, fluid_2)
    dynamic_viscosity_coolant_2 = cp.PropsSI("V", "T", mean_temperature, "P", atmospheric_pressure, fluid_2)
    kinematic_viscosity_coolant_2 = dynamic_viscosity_coolant_2 / density_coolant_2
    T_freeze_coolant_2 = safe_freeze_temp(coolant_2, fluid_2, atmospheric_pressure)
    if "Volumenstrom" in V_or_Q:
        heat_capacity = volume_flow_coolant_1 * density_coolant_1 * spec_heat_coolant_1 * temperature_difference
    elif "Leistung" in V_or_Q:
        volume_flow_coolant_1 = heat_capacity / (density_coolant_1 * spec_heat_coolant_1 * temperature_difference)
    volume_flow_coolant_2 = heat_capacity / (density_coolant_2 * spec_heat_coolant_2 * temperature_difference)
    velocity_coolant_1 = 4 * volume_flow_coolant_1 / np.pi / mean_inner_pipe_diameter**2
    velocity_coolant_2 = 4 * volume_flow_coolant_2 / np.pi / mean_inner_pipe_diameter**2
    lambda1 = friction_coefficient(mean_inner_pipe_diameter, velocity_coolant_1, kinematic_viscosity_coolant_1, roughness)
    lambda2 = friction_coefficient(mean_inner_pipe_diameter, velocity_coolant_2, kinematic_viscosity_coolant_2, roughness)
    pressure_drop_coolant_2 = pressure_drop_coolant_1 * lambda2 / lambda1 * density_coolant_1 / density_coolant_2 * (spec_heat_coolant_1**2) / (spec_heat_coolant_2**2)
    data = {
        "Parameter": [
            "Bezeichnung",
            "Übertragene Leistung [kW]",
            "Volumenstrom [m3/h]",
            "Strömungsgeschwindigkeit [m/s]",
            "Druckverlust [bar]",
            "Dichte [kg/m3]",
            "Spezifische Wärmekapazität [kJ/kg/K]",
            "Mittlere Temperatur [°C]",
            "Gefrierpunkt [°C]",
        ],
        "Kälteträger 1": [
            name_1,
            round(heat_capacity / 1000, 2),
            round(volume_flow_coolant_1 * 3.6 / 1e-3, 2),
            round(velocity_coolant_1, 2),
            round(pressure_drop_coolant_1 / 1e5, 2),
            round(density_coolant_1, 2),
            round(spec_heat_coolant_1 / 1000, 2),
            round(mean_temperature - 273.15, 2),
            round(T_freeze_coolant_1 - 273.15, 2),
        ],
        "Kälteträger 2": [
            name_2,
            round(heat_capacity / 1000, 2),
            round(volume_flow_coolant_2 * 3.6 / 1e-3, 2),
            round(velocity_coolant_2, 2),
            round(pressure_drop_coolant_2 / 1e5, 2),
            round(density_coolant_2, 2),
            round(spec_heat_coolant_2 / 1000, 2),
            round(mean_temperature - 273.15, 2),
            round(T_freeze_coolant_2 - 273.15, 2),
        ],
    }
    return pd.DataFrame(data)

st.markdown(
    f"""
    <div style='display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:0.2rem;'>
        <div style='font-size:3rem; font-weight:700; line-height:1.1;'>{APP_TITLE}</div>
        <div style='color:#9ca3af; font-size:1rem; line-height:1.1;'>{APP_VERSION}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Rechnet thermohydraulische Kennwerte von einem Kälteträger auf einen anderen um.")

left, right = st.columns([1, 1.25])

with left:
    project = st.text_input("Projekt", value="Projekt")
    c1_col, c1pct_col = st.columns(2)
    with c1_col:
        coolant_1 = st.selectbox("Fluid 1", ["Wasser", "Antifrogen N", "Antifrogen L", "Kaliumformiat"], index=0)
    with c1pct_col:
        concentration_1 = st.number_input("Konzentration Fluid 1 [%]", value=100.0, step=1.0, disabled=(coolant_1 == "Wasser"))
        if coolant_1 == "Wasser":
            concentration_1 = 100.0
    vq_col, vqval_col = st.columns(2)
    with vq_col:
        V_or_Q = st.selectbox("Basis", ["Volumenstrom Fluid 1 [m3/h]:", "Übertragene Leistung Fluid 1 [kW]:"], index=0)
    with vqval_col:
        vq_value = st.number_input("Wert", value=10.0, step=0.1)
    pressure_drop_coolant_1 = st.number_input("Druckverlust Fluid 1 [bar]", value=2.5, step=0.1)
    t_col, dt_col = st.columns(2)
    with t_col:
        mean_temperature = st.number_input("Mittlere Temperatur [°C]", value=7.5, step=0.1)
    with dt_col:
        temperature_difference = st.number_input("Temperaturdifferenz [K]", value=5.0, step=0.1)
    di_col, rough_col = st.columns(2)
    with di_col:
        mean_inner_pipe_diameter = st.number_input("Rohrinnendurchmesser [mm]", value=25.0, step=0.1)
    with rough_col:
        roughness = st.number_input("Rohrrauheit [mm]", value=0.0015, step=0.0001, format="%.4f")
    c2_col, c2pct_col = st.columns(2)
    with c2_col:
        coolant_2 = st.selectbox("Fluid 2", ["Wasser", "Antifrogen N", "Antifrogen L", "Kaliumformiat"], index=1)
    with c2pct_col:
        concentration_2 = st.number_input("Konzentration Fluid 2 [%]", value=34.0, step=1.0, disabled=(coolant_2 == "Wasser"))
        if coolant_2 == "Wasser":
            concentration_2 = 100.0
    run = st.button("Berechnen", use_container_width=True)

if "result_df" not in st.session_state:
    st.session_state.result_df = None
if "result_error" not in st.session_state:
    st.session_state.result_error = None

with right:
    st.subheader("Ergebnis")
    if run:
        try:
            inputs = {
                "project": project,
                "coolant_1": coolant_1,
                "coolant_2": coolant_2,
                "concentration_1": float(concentration_1),
                "concentration_2": float(concentration_2),
                "V_or_Q": V_or_Q,
                "volume_flow_coolant_1": float(vq_value),
                "heat_capacity": float(vq_value),
                "pressure_drop_coolant_1": float(pressure_drop_coolant_1),
                "roughness": float(roughness),
                "mean_temperature": float(mean_temperature),
                "temperature_difference": float(temperature_difference),
                "mean_inner_pipe_diameter": float(mean_inner_pipe_diameter),
            }
            st.session_state.result_df = run_calculation(inputs)
            st.session_state.result_error = None
        except Exception as e:
            st.session_state.result_df = None
            st.session_state.result_error = f"Fehler bei der Berechnung: {e}"

    if st.session_state.result_error:
        st.error(st.session_state.result_error)
    elif st.session_state.result_df is not None:
        st.dataframe(st.session_state.result_df, use_container_width=True, hide_index=True)
        st.download_button(
            label="CSV herunterladen",
            data=build_csv_bytes(st.session_state.result_df),
            file_name=f"{project.replace(' ', '_')}_Kälteträger-Rechner.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("Eingaben setzen und auf Berechnen klicken.")

st.markdown("---")
with st.expander("Anleitung"):
    st.markdown(
        """
Mit diesem Tool kannst du von einem **Kälteträger 1** auf einen **Kälteträger 2** umrechnen.

Für die Berechnung wählst du zuerst beim Kälteträger 1 entweder den **Volumenstrom** oder die **übertragene Leistung** als Ausgangsbasis.
Danach gibst du den **Druckverlust mit Kälteträger 1** an.

Zusätzlich werden allgemeine Angaben benötigt:
- mittlere Temperatur,
- Temperaturdifferenz,
- Rohrinnendurchmesser,
- Rohrrauheit,
- sowie Kälteträger 2 mit seiner Konzentration.

Ein wesentlicher Nutzen des Rechners ist, dass neben den hydraulischen Kenngrößen auch **thermodynamische Eigenschaften** der gewählten Kälteträger berechnet und gegenübergestellt werden. Dazu gehören insbesondere **Dichte**, **spezifische Wärmekapazität** und **Gefrierpunkt**.

Die **mittlere Temperatur** und die **Temperaturdifferenz** können zum Beispiel den Anwendungsfall von **Vorlauf und Rücklauf eines Kühlgeräts** abbilden.

Die Berechnungslogik kann im GitHub-Repository nachvollzogen werden:
[https://github.com/div-ne/Kaeltetraeger-Rechner](https://github.com/div-ne/Kaeltetraeger-Rechner)
"""
    )
with st.expander("Rohrrauheitswerte"):
    st.caption("Orientierungswerte aus deiner Tabelle für die Eingabe von k [mm].")
    roughness_df = pd.DataFrame(ROUGHNESS_ROWS, columns=["Werkstoff und Rohrart", "Zustand der Rohre", "k [mm]"])
    st.dataframe(roughness_df, use_container_width=True, hide_index=True)
with st.expander("Grenzen der Kälteträger"):
    st.caption("Zulässige Konzentrationsbereiche für die Eingabe in diesem Tool.")
    limits_df = pd.DataFrame(LIMITS_ROWS, columns=["Kälteträger", "Mögliche Konzentration [%]", "Hinweis"])
    st.dataframe(limits_df, use_container_width=True, hide_index=True)
