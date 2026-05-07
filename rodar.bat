@echo off

echo =========================
echo ATUALIZANDO MODELO
echo =========================

python modelo.py

echo =========================
echo INICIANDO STREAMLIT
echo =========================

streamlit run app.py

pause