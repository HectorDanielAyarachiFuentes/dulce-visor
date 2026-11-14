import sys
import os

# Asegurar que la raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import DulceVisor

if __name__ == '__main__':
    app = DulceVisor()
    app.mainloop()
