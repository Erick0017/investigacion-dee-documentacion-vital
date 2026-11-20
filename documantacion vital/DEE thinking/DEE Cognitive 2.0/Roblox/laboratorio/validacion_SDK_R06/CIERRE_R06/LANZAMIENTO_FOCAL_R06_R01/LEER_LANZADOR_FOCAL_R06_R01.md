# Lanzamiento focal bajo Python -I · corrección externa R01

El comando directo sellar_ventana_focal_R06.py no insertaba su directorio antes de importar sdk_common; preparar_escenas_focales_R06.py también necesita ese bootstrap. El fallo observado ocurrió antes de crear ventana/identidad/Native. Las30fuentes f0c15... permanecen EXACTAS, sin retocar actor/lector ni borrarlas.

Root ya selló la ventana mediante su launcher: start1795021039 (18Nov16:57:19UTC), last1795034260 y hard1795037860. NO RESELLAR. Esta nota registra elhecho comunicado porRoot, no una lectura de susdatosactivos.

Copie el NUEVO backend/lanzar_focal_R06_R01.py albackend del SHORT existente. Está fuera de la carpeta congelada. Comprueba SHA delmanifiesto f0c15... y los30miembros antesde ejecutar. Sólo permite verify/seal/prepare/scenes/start; añade sys.pathfocal y hace runpy delCLI exacto. No cambia argv de sus procesos internos ni el algoritmo. Preparar/iniciar/verificar ya tenían bootstrap propio; el wrapper permiteun único estilo deuso.

CWD=SHORT/RUNTIME_PRIVADO_LOCAL; PY=dependencias/producto/motor/python313/python.exe.

Ayuda, sólo parse/stdlib:

    <PY> -I -B backend/lanzar_focal_R06_R01.py --help
    <PY> -I -B backend/lanzar_focal_R06_R01.py scenes --help

Diagnóstico FS (no lee registrycontenido/ledger/Native/SQLite/token/procesos):

    <PY> -I -B backend/lanzar_focal_R06_R01.py diagnose-zero

Detectar un archivo ausente no certifica estadoNative0. El diagnóstico no recupera ni reejecuta nada. Si hayventana, informaDO_NOT_RESEAL. El wrapper rechaza sealcuandoexisteventana; --help sigueRO.

Comandos restantes corregidos:

    <PY> -I -B backend/lanzar_focal_R06_R01.py prepare crear --instance <ID> --condition OSCILANTE --execute-fs-only
    <PY> -I -B backend/lanzar_focal_R06_R01.py prepare crear --instance <ID> --condition CONTROL --execute-fs-only
    <PY> -I -B backend/lanzar_focal_R06_R01.py prepare importar --instance <ID> --context-sha256 <SHA_FOCAL_REAL> --deadline-utc-epoch 1795037860 --execute-root-only
    <PY> -I -B backend/lanzar_focal_R06_R01.py scenes --private-root <PADRE_DEL_SHORT_RUNTIME> --output <JSON_PRIVADO_NUEVO>
    <PY> -I -B backend/lanzar_focal_R06_R01.py start start --instance <ID_OSC> --minutes 180 --cycles 6 --port 8897 --validation-campaign --execute-real-native
    <PY> -I -B backend/lanzar_focal_R06_R01.py start start --instance <ID_CONTROL> --minutes 180 --cycles 6 --port 8898 --validation-campaign --execute-real-native

El primer start es alias delwrapper; el segundo es subcomando delCLI congelado. Estas órdenes siguen siendo EXCLUSIVAS deRoot. Importar/iniciar pueden abrir Native sólo con sus flags explícitos y guardas originales. Este launcher no autoriza experiencias ni amplía tiempo/saldo; no inicia otra identidad, copia o owner por sí mismo. OSC6debe estar cerrado/drenado/pareja antes deCONTROL. Nunca repetir IDs ni recuperar a ciegas por un fallo.

No usar aquí seal: ya está sellado. Los datos actuales y el cierre siguen bajoRoot.
