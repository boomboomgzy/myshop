from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent

#print(os.path.join(BASE_DIR,'myshop','static'))

class man():
    def a(self):
        print('a')

class boy(man):
    def a(self):
        super().a()
        
        
