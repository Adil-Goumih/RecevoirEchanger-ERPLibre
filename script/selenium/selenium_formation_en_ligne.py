# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# import time

# def create_elearning_course(driver):
#     try:
#         # Naviguer directement vers la page eLearning
#         driver.get("http://127.0.0.1:8069/web?db=nutrition_libre#action=469&model=slide.channel&view_type=kanban&cids=1&menu_id=299")
        
#         # Attendre que la page soit chargée
#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "o_kanban_view")))
        
#         # Cliquer sur le bouton "Créer"
#         create_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'o_list_button_add') or contains(@class, 'o-kanban-button-new')]"))
#         )
#         create_button.click()
        
#         # Attendre que le formulaire de création soit chargé
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "o_form_view")))
        
#         # Remplir le formulaire
#         course_name = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.NAME, "name"))
#         )
#         course_name.send_keys("Cours de nutrition avancée")
        
#         description = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.NAME, "description"))
#         )
#         description.send_keys("Ce cours couvre les aspects avancés de la nutrition.")
        
#         # Sauvegarder le cours
#         save_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'o_form_button_save')]"))
#         )
#         save_button.click()
        
#         print("Cours eLearning créé avec succès!")
#     except Exception as e:
#         print(f"Une erreur s'est produite lors de la création du cours : {str(e)}")

# def main():
#     # Configuration du webdriver
#     chrome_options = Options()
#     chrome_options.add_argument("--start-maximized")  # Ouvrir Chrome en plein écran
    
#     # Initialiser le driver
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)
    
#     try:
#         # Connexion
#         driver.get("http://127.0.0.1:8069/web/login")
#         print(f"URL actuelle : {driver.current_url}")
#         print(f"Titre de la page : {driver.title}")
        
#         # Attendre que la page de connexion soit chargée
#         # time.sleep(5)
        
#         # Vérifier s'il y a des iframes
#         iframes = driver.find_elements(By.TAG_NAME, "iframe")
#         if iframes:
#             print(f"Nombre d'iframes trouvés : {len(iframes)}")
#             driver.switch_to.frame(iframes[0])
        
#         # Entrer les identifiants
#         try:
#             username = WebDriverWait(driver, 20).until(
#                 EC.element_to_be_clickable((By.ID, "login"))
#             )
#             username.send_keys("admin")
            
#             password = WebDriverWait(driver, 20).until(
#                 EC.element_to_be_clickable((By.ID, "password"))
#             )
#             password.send_keys("admin")
            
#             # Cliquer sur le bouton de connexion
#             login_button = WebDriverWait(driver, 20).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
#             )
#             login_button.click()
#         except TimeoutException:
#             print("Les éléments de connexion n'ont pas été trouvés. Tentative d'utilisation de JavaScript.")
#             driver.execute_script("document.getElementById('login').value='admin';")
#             driver.execute_script("document.getElementById('password').value='admin';")
#             driver.execute_script("document.querySelector('button[type=\"submit\"]').click();")
        
#         # Attendre que la page d'accueil soit chargée
#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "o_home_menu")))
        
#         # Créer le cours eLearning
#         create_elearning_course(driver)
        
#     except Exception as e:
#         print(f"Une erreur s'est produite : {str(e)}")
#         print(f"URL actuelle : {driver.current_url}")
#         print(f"Titre de la page : {driver.title}")
#     finally:
#         # Fermer le navigateur
#         driver.quit()

# if __name__ == "__main__":
#     main()
from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def wait_and_sleep(seconds=2):
    time.sleep(seconds)

def select_database(driver, db_name):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "o_database_list"))
        )
        wait_and_sleep()
        
        db_elements = driver.find_elements(By.CLASS_NAME, "list-group-item")
        
        for element in db_elements:
            if db_name in element.text:
                element.click()
                wait_and_sleep()
                print(f"Base de données '{db_name}' sélectionnée")
                return True
        
        print(f"Base de données '{db_name}' non trouvée")
        return False
    except Exception as e:
        print(f"Erreur lors de la sélection de la base de données : {str(e)}")
        return False

def login(driver, username, password):
    try:
        wait_and_sleep(5)  # Attendre un peu plus longtemps pour le chargement de la page
        
        # Trouver et remplir le champ username
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login"))
        )
        username_field.clear()
        username_field.send_keys(username)
        wait_and_sleep()
        
        # Trouver et remplir le champ password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.clear()
        password_field.send_keys(password)
        wait_and_sleep()
        
        # Trouver et cliquer sur le bouton de connexion
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_button.click()
        wait_and_sleep(5)  # Attendre le chargement après la connexion
        
        print("Tentative de connexion effectuée")
        return True
    except Exception as e:
        print(f"Erreur lors de la connexion : {str(e)}")
        return False
def check_login_success(driver):
    try:
        # Vérifier si nous sommes sur la page de discussion
        WebDriverWait(driver, 10).until(
            EC.title_contains("Odoo - Discussion")
        )
        print("Connexion confirmée, sur la page de discussion")
        return True
    except Exception as e:
        print(f"Erreur lors de la vérification de la connexion : {str(e)}")
        return False

def navigate_to_elearning(driver):
    try:
        # Attendre que le menu soit chargé
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "o_menu_sections"))
        )
        print("Menu principal chargé")

        # Trouver et cliquer sur le menu eLearning
        elearning_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'eLearning')]"))
        )
        elearning_menu.click()
        print("Cliqué sur le menu eLearning")

        # Attendre que la page eLearning se charge
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "o_content"))
        )
        print("Page eLearning chargée")

    except Exception as e:
        print(f"Erreur lors de la navigation vers eLearning : {str(e)}")
        print(f"URL actuelle : {driver.current_url}")
        print(f"Titre de la page : {driver.title}")

def create_elearning_course(driver):
    try:
        # Cliquer sur le bouton "Créer"
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'o_list_button_add') or contains(@class, 'o-kanban-button-new')]"))
        )
        create_button.click()
        print("Cliqué sur le bouton Créer")

        # Attendre que le formulaire de création se charge
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "o_form_view"))
        )
        print("Formulaire de création chargé")

        # Remplir le formulaire du cours
        course_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "name"))
        )
        course_name.send_keys("Cours de test Selenium")
        print("Nom du cours saisi")

        description = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "description"))
        )
        description.send_keys("Ce cours a été créé automatiquement par un script Selenium.")
        print("Description du cours saisie")

        # Sauvegarder le cours
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'o_form_button_save')]"))
        )
        save_button.click()
        print("Cours sauvegardé")

        # Attendre la confirmation de sauvegarde
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "o_form_saved"))
        )
        print("Cours eLearning créé avec succès")

    except Exception as e:
        print(f"Erreur lors de la création du cours eLearning : {str(e)}")
        print(f"URL actuelle : {driver.current_url}")
        print(f"Titre de la page : {driver.title}")
def main():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get("http://localhost:8069")
        wait_and_sleep()
        print(f"URL actuelle : {driver.current_url}")
        print(f"Titre de la page : {driver.title}")
        
        # Sélection de la base de données
        try:
            select_db = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list-group-item"))
            )
            select_db.click()
            wait_and_sleep()
            print("Base de données 'nutrition_libre' sélectionnée")
        except Exception as e:
            print(f"Erreur lors de la sélection de la base de données : {str(e)}")
        
        # Tentative de connexion
        if login(driver, "admin", "admin"):
            if check_login_success(driver):
                print("Connecté avec succès")
                # Ici, vous pouvez ajouter le code pour naviguer vers eLearning et créer un cours
                navigate_to_elearning(driver)
                create_elearning_course(driver)
            else:
                print("La connexion semble avoir échoué ou la page attendue n'a pas été chargée")
        else:
            print("Échec de la connexion")
        
    except Exception as e:
        print(f"Une erreur générale s'est produite : {str(e)}")
    finally:
        wait_and_sleep()
        print(f"URL finale : {driver.current_url}")
        print(f"Titre final de la page : {driver.title}")
        driver.quit()

if __name__ == "__main__":
    main()