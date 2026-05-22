import io
import numpy as np
import pandas as pd
import streamlit as st
import CoolProp.CoolProp as cp

st.set_page_config(page_title="CCon 0.1 Streamlit", layout="wide")


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
    else:
        if check_moody_diagram >= 200:
            lambda_result = lambda_nikuradse
        elif epsilon_k < 0.001 and Re < 10000:
            lambda_result = lambda_blasius
        elif epsilon_k < 0.0002 and Re < 100000:
            lambda_result = lambda_blasius
        elif epsilon_k < 0.00002 and Re < 1000000:
            lambda_result = lambda_prandtl
        elif epsilon_k < 0.00001:
            lambda_result = lambda_prandtl
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

    pressure_drop_coolant_2 = (
        pressure_drop_coolant_1
        * lambda2
        / lambda1
        * density_coolant_1
        / density_coolant_2
        * (spec_heat_coolant_1**2)
        / (spec_heat_coolant_2**2)
    )

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


st.title("CCon 0.1 Streamlit")
st.caption("Dieses Tool rechnet thermohydraulische Kennwerte von Fluid 1 auf Fluid 2 um.")

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
            df = run_calculation(inputs)
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv_data = df.to_csv(index=False, sep=";").encode("utf-8")
            st.download_button(
                label="CSV herunterladen",
                data=csv_data,
                file_name="ccon-ergebnis.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Fehler bei der Berechnung: {e}")
    else:
        st.info("Eingaben setzen und auf Berechnen klicken.")

st.markdown("---")
st.caption("Deployment: Repo mit app.py und requirements.txt auf GitHub hochladen, dann in Streamlit Community Cloud Deploy wählen.")
