Analiza kodu RizomUV Exporter - Zalecane poprawki
1. Problemy z kompatybilnością wersji Cinema 4D
Plik: RizomUV Exporter.pyp
Funkcja: fbx_config()
Problem: Nieprawidłowe warunki sprawdzania wersji
python# Błędny kod:
if c4d.GetC4DVersion() > 21999 < 25999:
    fbx[c4d.FBXEXPORT_MATERIALS] = c4d.FBXEXPORT_MATERIALS_PHONGLAMBERT

# Poprawiony kod:
if 21999 < c4d.GetC4DVersion() < 25999:
    fbx[c4d.FBXEXPORT_MATERIALS] = c4d.FBXEXPORT_MATERIALS_PHONGLAMBERT
2. Niepotrzebna redundancja w sprawdzaniu typu
Plik: RizomUV Exporter.pyp
Funkcja: Options.parser()
Problem: Zbędne sprawdzanie tego samego typu
python# Błędny kod:
if isinstance(v[1], str) or isinstance(v[1], str):  # TEXT

# Poprawiony kod:
if isinstance(v[1], (str, unicode if 'unicode' in dir(__builtins__) else str)):  # TEXT
3. Brak właściwej obsługi błędów
Plik: RizomUV Exporter.pyp
Funkcja: settings_save()
Problem: Nieprawidłowe przechwytywanie wyjątków
python# Błędny kod:
except WindowsError:
    c4d.gui.MessageDialog("Write Settings Failed")
    return False

# Poprawiony kod:
except (OSError, IOError) as e:
    c4d.gui.MessageDialog(f"Błąd zapisu ustawień: {str(e)}")
    return False
4. Problemy z zarządzaniem wątkami
Plik: RizomUV Exporter.pyp
Klasa: WatchThread
Problem: Brak mechanizmu bezpiecznego zatrzymywania wątku
python# Dodaj do klasy WatchThread:
def __init__(self, name, doc, selected_objs, swap_path, t, p, UI):
    Thread.__init__(self, name=name)
    self.doc = doc
    self.selected_objs = selected_objs
    self.swap_path = swap_path
    self.time = t
    self.p = p
    self.UI = UI
    self._stop_event = threading.Event()  # Dodaj flagę stop
    
def stop(self):
    self._stop_event.set()
    
def run(self):
    doc = c4d.documents.GetActiveDocument()
    selected = doc.GetActiveObjects(0)
    printed = 0
    dirt_flag = False

    while not self._stop_event.is_set():  # Sprawdzaj flagę stop
        # reszta kodu...
        if self._stop_event.wait(1):  # Zamiast time.sleep(1)
            break
5. Problemy z zarządzaniem plikami
Plik: RizomUV Exporter.pyp** **Funkcja**: script_save()`
Problem: Brak zamykania plików w przypadku błędu
python# Poprawiony kod:
def script_save(self, name, script, dialog=True, mode="w"):
    if name is None:
        dialog = True

    if dialog:
        script_name = storage.SaveDialog(
            0, "Save *.lua File", "lua", def_path=self.scripts_folder, def_file=name
        )
    else:
        script_name = os.path.join(self.scripts_folder, name)

    if script_name is None:
        return

    if os.path.exists(self.scripts_folder):
        try:
            if mode == "w":
                with open(script_name, "w", encoding='utf-8') as file_:
                    file_.write(script)
            elif mode == "r+":
                with open(script_name, "r+", encoding='utf-8') as file_:
                    lines = file_.readlines()
                    lines.insert(0, script)
                    file_.writelines(lines)
                    
            split_name = os.path.basename(script_name)
            return split_name
        except (IOError, OSError) as e:
            c4d.gui.MessageDialog(f"Błąd zapisu pliku: {str(e)}")
            return None
6. Optymalizacja funkcji rizomuv_indexes
Plik: RizomUV Exporter.pyp
Funkcja: rizomuv_indexes()
Problem: Długa, skomplikowana funkcja - powinna być podzielona
python# Podziel na mniejsze funkcje:
def _process_polygon_edges(self, polygon, polygon_index, uv_data):
    """Przetwarza krawędzie pojedynczego poligonu"""
    # Kod dla pojedynczego poligonu
    pass

def _find_unique_edges(self, points, uvs, pass_edges, pass_uvws):
    """Znajduje unikalne krawędzie"""
    # Logika znajdowania unikalnych krawędzi
    pass

def rizomuv_indexes(op, rizom_index=-1):
    """Główna funkcja - orchestruje proces"""
    # Uproszczona wersja używająca helper functions
    pass
7. Dodanie logowania
Plik: RizomUV Exporter.pyp
Na początku pliku:
pythonimport logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rizomuv_exporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
8. Walidacja konfiguracji
Plik: RizomUV Exporter.pyp
Nowa metoda w klasie Exporter:
pythondef validate_configuration(self):
    """Waliduje konfigurację przed eksportem"""
    errors = []
    
    # Sprawdź ścieżkę do RizomUV
    rizomuv_path = self.ui["TXT_U3D_PATH"][1]
    if not rizomuv_path or not os.path.exists(rizomuv_path):
        errors.append("Nieprawidłowa ścieżka do RizomUV")
    
    # Sprawdź folder skryptów
    if not os.path.exists(self.scripts_folder):
        errors.append("Folder skryptów nie istnieje")
        
    if errors:
        error_msg = "Błędy konfiguracji:\n" + "\n".join(f"- {error}" for error in errors)
        c4d.gui.MessageDialog(error_msg)
        return False
        
    return True
9. Ulepszone zarządzanie błędami subprocess
Plik: RizomUV Exporter.pyp
Funkcja: Starter.rizomuv_run()
python# Poprawiony kod uruchamiania RizomUV:
try:
    self.p = subprocess.Popen(
        param, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    logger.info(f"RizomUV uruchomiony z parametrami: {param}")
except (OSError, subprocess.SubprocessError) as e:
    error_msg = f"Nie można uruchomić RizomUV: {str(e)}"
    c4d.gui.MessageDialog(error_msg)
    logger.error(error_msg)
    return
10. Dodanie mechanizmu backup
Plik: RizomUV Exporter.pyp
Nowa metoda:
pythondef create_backup(self, file_path):
    """Tworzy kopię zapasową pliku przed nadpisaniem"""
    if os.path.exists(file_path):
        backup_path = file_path + ".backup"
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.info(f"Utworzono backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.warning(f"Nie można utworzyć backup: {str(e)}")
    return None
Te poprawki znacznie zwiększą stabilność, czytelność i funkcjonalność pluginu, jednocześnie dodając lepszą obsługę błędów i mechanizmy bezpieczeństwa.