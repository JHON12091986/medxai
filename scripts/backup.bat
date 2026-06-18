@echo off
echo Iniciando copia de seguridad...
robocopy "C:\Users\jhons\bounties_python\nina" "D:\Backups_Bounties\NINA_Backup" /MIR /FFT /Z /W:5 /R:5
echo Backup completado exitosamente.
pause