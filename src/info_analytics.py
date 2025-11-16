"""
Proyecto final 

"""
#____Librerias_____
import pickle
import re
from collections import Counter
#_____Clases_____
class Archivo:
    n_archivos = 0   

    def __init__(self, ruta, tag):
        Archivo.n_archivos += 1        
        self.id = Archivo.n_archivos   
        self.ruta = ruta
        self.tag = tag
        self.contenido = ""
    def leer_archivo(self):
        match = re.search(r"C:/.*", self.ruta, re.IGNORECASE)
        if match:
            ruta_limpia = match.group(0)
        else:
            ruta_limpia = self.ruta

        with open(ruta_limpia, "r", encoding="utf-8") as archivo:
                self.contenido = archivo.read()
       
class AnalizadorTexto:
        def __init__(self, archivo):
            self.archivo = archivo
            self.texto = archivo.contenido.lower()

        def contar_palabras(self):
            palabras = re.findall(r'\b[a-záéíóúñü]+', self.texto, re.IGNORECASE)
            return len(palabras)

        def palabras_frecuentes(self, n=10):
            palabras = re.findall(r'\b[a-záéíóúñü]+', self.texto, re.IGNORECASE)
            contador = Counter(palabras)
            return contador.most_common(n)

class VolverMenu(Exception):
    pass

        
#______Funciones utiles__________

def actualizar_contador(archivos):
    if archivos:
        Archivo.n_archivos = max(archivos.keys())
    else:
        Archivo.n_archivos = 0

def eliminar_archivo(id_archivo, archivos_cargados):
    try:
        del archivos_cargados[id_archivo]
        guardar_archivos(archivos_cargados)
        print(f"Archivo {id_archivo} eliminado correctamente.")
    except KeyError:
        print("Error: Archivo no encontrado.")
        
def guardar_archivos(archivos, archivo_pickle="archivos_guardados.pkl"):
    with open(archivo_pickle, "wb") as f:
        pickle.dump(archivos, f)


def cargar_archivos(archivo_pickle="archivos_guardados.pkl"):
    try:
        with open(archivo_pickle, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

archivos_cargados = cargar_archivos()
actualizar_contador(archivos_cargados)

def input_general(mensaje):
    respuesta = input(mensaje)
    if respuesta.strip() == "-1":
        raise VolverMenu
    return respuesta

def input_num(mensaje):
    return int(input_general(mensaje))


#________Inferfaz del usuario_______

print("Hola! Bienvenido a InfoAnalytics, aquí podrás cargar archivos y generar informes con ellos.")
print("Nota: Puedes volver al menú principal en cualquier momento, solo escribe -1")

while True:
    try:
        n = input_num("Elige una opción:\n1. Cargar o eliminar archivo\n2. Ver archivos actuales\n3. Reporte de texto\n0. Finalizar\nOpción elegida: ")

        if n == 0:
            print("Programa finalizado.")
            break
        
        elif n == 1:
            print("--- Cargar o eliminar archivo ---")
            na = input_num("Elige una opción:\n0. Eliminar archivo\n1. Cargar archivo\nRespuesta: ")

            if na == 1:
                print("Carga archivos solo con su ruta en tu computador y un nombre para identificarlo")
                print("Tus archivos cargados persisten luego de parar el código")

                ruta_usuario = input_general("Ruta del archivo: ")
                nombre_ruta = input_general("Nombre para identificar el archivo: ")

                nuevo = Archivo(ruta_usuario, nombre_ruta)
                archivos_cargados[nuevo.id] = nuevo
                guardar_archivos(archivos_cargados)

                print("El archivo ha sido cargado correctamente!")
                print(f"Archivo creado con ID {nuevo.id} y nombre '{nuevo.tag}'")

            elif na == 0:
                idb = input_num("ID del archivo que quieres eliminar: ")
                eliminar_archivo(idb,archivos_cargados)
        elif n == 2:
            print("--- Archivos cargados ---")
            if not archivos_cargados:
                print("No hay archivos cargados actualmente.")
            else:
                for id_archivo, obj in archivos_cargados.items():
                    print(f"ID: {id_archivo} | Nombre: {obj.tag} | Ruta: {obj.ruta}")
        elif n == 3:
            print("--- Reporte de Texto ---")
            print("Solo aplica para archivos de tipo texto")

            n3 = input_num("Ingresa el ID del archivo a analizar: ")

            archivo_obj = archivos_cargados[n3]
            archivo_obj.leer_archivo()

            reporte = AnalizadorTexto(archivo_obj)
            palabras = reporte.contar_palabras()
            frecuencia = reporte.palabras_frecuentes()

            print("--- Reporte ---")
            print(f"Número de palabras: {palabras}")
            print("Palabras más comunes:")
            print(frecuencia)

    except VolverMenu:
        print("\nRegresando al menú principal...\n")

    except KeyError:
        print("Error: No existe un archivo con ese ID.")

    except ValueError:
        print("Entrada inválida. Por favor ingresa un número válido.")