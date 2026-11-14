"""
Compatibilidad hacia atrás con accesos directos o scripts previos.
Redirige directamente al entrypoint modular main.py.
"""
from main import app, DulceVisor

if __name__ == '__main__':
    visor = DulceVisor()
    visor.mainloop()
