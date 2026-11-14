# ⚡ Dulce-Visor

Widget de monitoreo flotante ultraligero y estilizado (Fluent / Obsidian Cyberpunk) para la barra de tareas de Windows 11.

## 🚀 Características
- **Zero-overhead:** < 30 MB de RAM y 0.0% de uso de CPU en reposo.
- **Métricas en tiempo real:**
  - Uso de RAM con barra de progreso.
  - Botón de optimización / liberación de memoria (RAM Boost con LED verde).
  - Porcentaje de CPU + Temperatura real de CPU en tiempo real vía COM WMI in-process (sin llamadas pesadas a PowerShell).
  - Porcentaje de GPU NVIDIA + Temperatura real de GPU (vía NVML).
  - Gráficos de onda (sparklines) fluidos con suavizado anti-aliasing.
- **Topmost Inteligente:**
  - Anclado permanentemente sobre la barra de tareas de Windows 11 (incluso al abrir aplicaciones o el menú inicio).
  - **Auto-Hide en Juegos:** Se oculta automáticamente cuando una aplicación o juego corre en pantalla completa (ej. *Left 4 Dead 2*) para no tapar el HUD, y reaparece al volver al escritorio.

## 📁 Estructura del Proyecto
```text
dulce-visor/
├── src/
│   ├── app.py          # Clase principal de la aplicación y ciclo de vida
│   ├── config.py       # Paleta de colores, geometría y guardado de coordenadas
│   ├── metrics.py      # Colector de métricas de hardware (RAM, CPU, GPU, Temp)
│   ├── renderer.py     # Motor de renderizado en alta definición PIL (LANCZOS)
│   └── window.py       # Control Win32 (Z-order x64, ToolWindow, auto-hide fullscreen)
├── scripts/
│   └── ver_consumo.bat # Diagnóstico rápido de consumo de RAM del proceso
├── herramientas/       # Skills y directivas del agente
├── config.json         # Coordenadas persistentes del visor
├── requirements.txt    # Dependencias de Python
├── main.py             # Entrypoint principal
├── iniciar.bat         # Inicia el visor en segundo plano
└── detener.bat         # Cierra el visor
```

## ▶️ Uso
- **Iniciar:** Ejecutar `iniciar.bat` (doble clic).
- **Detener:** Ejecutar `detener.bat`.
- **Mover:** Arrastrar con clic izquierdo desde cualquier punto del cuerpo (excepto el botón de rayo).
- **Optimizar RAM:** Clic en el botón del rayo o clic derecho -> "⚡ Optimizar Memoria RAM".
- **Re-centrar:** Clic derecho -> "📌 Re-centrar en la barra".
