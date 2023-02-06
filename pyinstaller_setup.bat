@ECHO OFF
TITLE Python Version PDM Installation (2020.04.25)
SET DIST_PATH = D:\setup_rom\python_pdm_2

ECHO Create Dist Program
C:\Users\chen_\AppData\Local\Programs\Python\Python37\Scripts\pyinstaller --distpath D:\setup_rom\python_temp Entry.spec
ECHO **** Finish Create.

SET TEMP_PATH = D:\setup_rom\python_temp\PDM_2
SET EXE_PATH = D:\setup_rom\python_pdm_2\PDM_2

COPY D:\setup_rom\python_temp\PDM_2\PDM_2.exe D:\setup_rom\python_pdm_2\PDM_2
ECHO Delete Cache
RD /s %CD%\build
ECHO **** Finish Delete.
EXIT

ECHO Copy other components
XCOPY %CD%\dlls D:\setup_rom\python_pdm_2\PDM_2\dlls /D/E/-Y
XCOPY %CD%\images D:\setup_rom\python_pdm_2\PDM_2\images /D/E/-Y
COPY pdm_config.ini D:\setup_rom\python_pdm_2\PDM_2\
COPY rt_config.db D:\setup_rom\python_pdm_2\PDM_2\
COPY OPS_ING_MMI.ico D:\setup_rom\python_pdm_2\PDM_2\
ECHO **** Finish Copy.

ECHO All Finished.
