# create_sample_data.py
from app import create_app        # on importe la factory
from utils.admin import create_sample_data

app = create_app()                # on construit l’app
with app.app_context():           # on « pousse » le contexte
    create_sample_data()
    print("✅ Données d’exemple créées.")
