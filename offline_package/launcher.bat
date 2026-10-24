@echo off
title Boali Hospital MRI AI Workstation (v1.1.0)
color 0b
echo ======================================================================
echo   پلتفرم تخصصی هوش مصنوعی و ایستگاه کاری ام‌آر‌آی بیمارستان بوعلی مریوان
echo   طراح و توسعه‌دهنده: آرام مصطفائی | نگارش رسمی v1.1.0
echo ======================================================================
echo.
cd /d "%~dp0"
if exist "Boali_MRI_Workstation.exe" (
    start "" "Boali_MRI_Workstation.exe"
) else (
    python Boali_MRI_Workstation.py
)
exit /b
