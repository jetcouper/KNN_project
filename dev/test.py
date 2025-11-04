# Importation des modules
import sys
from projet.db_credential import PostgreSQLCredential
from projet.klustr_dao import PostgreSQLKlustRDAO
from klustr_widget import KlustRDataSourceViewWidget
from projet.klustr_utils import QtNpConvert
from PySide6 import QtWidgets
import numpy as np
from __feature__ import snake_case, true_property
from Axe2 import Axe2


def metrique1(bytes_images):
    
    qimage = QtNpConvert.qimage_from_png(bytes_images)
    print(qimage)
    
    np_image = QtNpConvert.np_from_qimage(qimage)
    return np_image    
    

app = QtWidgets.QApplication(sys.argv)

credential = PostgreSQLCredential(
    host='localhost',
    port=5432,
    database='postgres',
    user='postgres',
    password='AAAaaa123')

# DAO 
klustr_dao = PostgreSQLKlustRDAO(credential)

# pour prendre les images il faut mettre le nom du dataset (name) ensuite specifier training ou test
images = klustr_dao.image_from_dataset('Alpha-Narrow-Medium', training_image=False)

# prendre la premiere image
img_info = images[0]


# les infos se trouve a la page 9 
nom_image = img_info[3]
classe = img_info[1]
largeur = img_info[4]
hauteur = img_info[5]
bytes_png = img_info[6]

print(f"Nom : {nom_image}")
print(f"Classe : {classe}")

image_np = metrique1(bytes_png)
image_np = 1 - image_np  # Inverser les couleurs si nécessaire



analyse = Axe2.analyze_image(image_np)
# Axe2.draw_circle(image_np, analyse[0], 30)
Axe2.show(image_np, analyse, analyse[1])



source_data_widget = KlustRDataSourceViewWidget(klustr_dao)
source_data_widget.show()


sys.exit(app.exec_())