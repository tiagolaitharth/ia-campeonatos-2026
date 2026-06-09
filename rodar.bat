@echo off

cd /d "C:\Users\Pichau\OneDrive\ia-sulamericanos"

echo =========================
echo TREINANDO IA
echo =========================

python modelo.py

python zeroazero.py

echo =========================
echo ENVIANDO PARA GITHUB
echo =========================

git add .

git commit -m "Atualizacao automatica"

git push

echo =========================
echo FINALIZADO
echo =========================

pause