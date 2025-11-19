# InfoAnalytics - versión refactorizada

import pickle
import re
from collections import Counter
import pandas as pd
from langdetect import detect
import pdfplumber
import docx


class ArchivoBase:
    n_archivos = 0

    def __init__(self, ruta, tag, id=None):
        if id is None:
            ArchivoBase.n_archivos += 1
            self.id = ArchivoBase.n_archivos
        else:
            self.id = int(id)
            if ArchivoBase.n_archivos < self.id:
                ArchivoBase.n_archivos = self.id

        self.ruta = self.limpiar_ruta(ruta)
        self.tag = tag

    def limpiar_ruta(self, ruta):
        ruta = ruta.strip()
        idx = ruta.find("C:/")
        if idx != -1:
            return ruta[idx:]
        else:
            return ruta
class ArchivoTexto(ArchivoBase):
    def __init__(self, ruta, tag, id=None):
        super().__init__(ruta, tag, id=id)
        self.tipo = self.detectar_tipo()
        self.contenido = ""

    def detectar_tipo(self):
        ruta = self.ruta.lower()
        if ruta.endswith(".txt"):
            return "txt"
        elif ruta.endswith(".pdf"):
            return "pdf"
        elif ruta.endswith(".docx"):
            return "docx"
        elif ruta.endswith(".csv"):
            return "csv"

    def leer_archivo(self):
        if self.tipo == "txt":
            self.leer_txt()
        elif self.tipo == "pdf":
            self.leer_pdf()
        elif self.tipo == "docx":
            self.leer_docx()
        elif self.tipo == "csv":
            self.leer_txt_csv()
        else:
            raise ValueError("Tipo de archivo no soportado")

    def leer_txt(self):
        with open(self.ruta, "r", encoding="utf-8", errors="ignore") as f:
            self.contenido = f.read()

    def leer_pdf(self):
        texto = ""
        with pdfplumber.open(self.ruta) as pdf:
            for pagina in pdf.pages:
                pag_texto = pagina.extract_text()
                if pag_texto:
                    texto += pag_texto + "\n"
        self.contenido = texto

    def leer_docx(self):
        doc = docx.Document(self.ruta)
        texto = "\n".join([p.text for p in doc.paragraphs])
        self.contenido = texto

    def leer_txt_csv(self):
        with open(self.ruta, "r", encoding="utf-8", errors="ignore") as f:
            self.contenido = f.read()


class ArchivoDatos(ArchivoBase):
    def __init__(self, ruta, tag, id=None):
        super().__init__(ruta, tag, id=id)
        self.dataframe = None
        self.tipo = self.detectar_tipo()

    def detectar_tipo(self):
        ruta = self.ruta.lower()
        if ruta.endswith(".csv"):
            return "csv"
        elif ruta.endswith(".xlsx") or ruta.endswith('.xls'):
            return "xlsx"
        
    def leer_archivo(self, sheet_name=0):
        if self.tipo == "csv":
            self.leer_csv()
        elif self.tipo == "xlsx":
            self.leer_excel(sheet_name=sheet_name)
        else:
            raise ValueError("Tipo de archivo no soportado")

    def leer_csv(self):
        try:
            self.dataframe = pd.read_csv(self.ruta, encoding="utf-8")
        except Exception as e:
            print("Error leyendo CSV:", e)

    def leer_excel(self, sheet_name=0):
        try:
            self.dataframe = pd.read_excel(self.ruta, sheet_name=sheet_name)
        except Exception as e:
            print("Error leyendo Excel:", e)

    def obtener_columnas(self):
        if self.dataframe is not None:
            return list(self.dataframe.columns)
        return []

    def obtener_filas(self, n=5):
        if self.dataframe is not None:
            return self.dataframe.head(n)
        return None


class AnalizadorTexto:
    def __init__(self, archivo):
        self.archivo = archivo
        self.texto = archivo.contenido.lower()

    def contar_palabras(self):
        palabras = re.findall(r'\b[a-záéíóúñü]+', self.texto, re.IGNORECASE)
        return len(palabras)

    def palabras_frecuentes(self, n=5):
        palabras = re.findall(r'\b[a-záéíóúñü]+', self.texto, re.IGNORECASE)
        contador = Counter(palabras)
        return contador.most_common(n)

    def densidad_lexica(self):
        palabras = re.findall(r'\b[a-záéíóúñü]+\b', self.texto, re.IGNORECASE)

        if not palabras:
            return "El texto no tiene palabras"

        vocabulario = set(palabras)
        densidad = round(len(vocabulario) / len(palabras), 2)

        if densidad < 0.25:
            interpretacion = "El texto tiene una baja densidad léxica."
        elif densidad < 0.5:
            interpretacion = "El texto tiene una densidad léxica media."
        else:
            interpretacion = "El texto tiene una densidad léxica alta."

        return (
            f"La densidad léxica del texto es {densidad}\n"
            f"{interpretacion}"
        )

    def longitud_promedio(self):
        palabras = re.findall(r'\b\w+\b', self.texto, re.UNICODE)

        if not palabras:
            return "No hay palabras en el texto"

        longitudes = [len(p) for p in palabras]
        promedio = round(sum(longitudes) / len(longitudes), 2)

        if promedio < 3:
            interpretacion = "El texto usa palabras muy cortas, probablemente muy simple o informal."
        elif promedio < 5:
            interpretacion = "El texto tiene un nivel básico, con palabras relativamente cortas."
        elif promedio < 7:
            interpretacion = "El texto tiene un nivel medio, con vocabulario algo más desarrollado."
        elif promedio < 9:
            interpretacion = "El texto tiene un vocabulario relativamente sofisticado."
        else:
            interpretacion = "El texto utiliza palabras muy largas; parece técnico o especializado."

        return (
            f"Las palabras dentro del texto tienen una longitud promedio de {promedio}\n"
            f"{interpretacion}"
        )

    def detectar_idioma(self):
        codigo = detect(self.texto)
        mapa = {
            "es": "Español",
            "en": "Ingles",
            "fr": "Francés",
            "de": "Alemán",
            "pt": "Portugues"
        }

        return mapa.get(codigo, codigo)


class AnalizadorExtra:
    def __init__(self, archivo):
        self.archivo = archivo
        self.texto = archivo.contenido.lower()
        self.lineas = archivo.contenido.splitlines()

    def encontrar_palabra(self, palabra):
        frecuencia = Counter(
            re.findall(r'\b[a-záéíóúñü]+', self.texto)
        )[palabra.lower()]

        if frecuencia == 0:
            return f"La palabra '{palabra}' no fue encontrada en el texto."

        contextos = []
        palabra_l = palabra.lower()

        for num, linea in enumerate(self.lineas, start=1):
            if palabra_l in linea.lower():
                contexto = linea.strip()
                if len(contexto) > 300:
                    contexto = contexto[:300].rstrip() + "..."
                    contexto = resaltar(contexto, palabra)
                else:
                    contexto += "..."
                    contexto = resaltar(contexto, palabra)

                contextos.append(f"Línea {num}: {contexto}")

            if len(contextos) == 5:
                break

        resultado = f"La palabra '{palabra}' aparece {frecuencia} veces.\n"

        if contextos:
            resultado += "\nPrimeras líneas encontradas con la palabra:\n" + "\n".join(contextos)
        else:
            resultado += "\nNo se encontraron líneas donde aparezca la palabra."

        return resultado


class VolverMenu(Exception):
    pass


#______Funciones utiles__________

def actualizar_contador(archivos):
    if archivos:
        try:
            ArchivoBase.n_archivos = max(int(k) for k in archivos.keys())
        except Exception:
            ArchivoBase.n_archivos = 0
    else:
        ArchivoBase.n_archivos = 0


def eliminar_archivo(id_archivo, archivos_cargados):
    try:
        del archivos_cargados[id_archivo]
        guardar_archivos(archivos_cargados)
        print(f"Archivo {id_archivo} eliminado correctamente.")
    except KeyError:
        print("Error: Archivo no encontrado.")


def guardar_archivos(archivos, archivo_pickle="archivos_guardados.pkl"):
    datos = {}
    for id_arch, obj in archivos.items():
        if isinstance(obj, ArchivoTexto):
            tipo = "texto"
        elif isinstance(obj, ArchivoDatos):
            tipo = "datos"
        else:
            tipo = "base"
        datos[int(id_arch)] = {"class": tipo, "ruta": obj.ruta, "tag": obj.tag}

    with open(archivo_pickle, "wb") as f:
        pickle.dump(datos, f)


def cargar_archivos(archivo_pickle="archivos_guardados.pkl"):
    try:
        with open(archivo_pickle, "rb") as f:
            datos = pickle.load(f)

        archivos = {}
        if isinstance(datos, dict):
            for id_arch, meta in datos.items():
                try:
                    cid = int(id_arch)
                except Exception:
                    cid = id_arch

                if isinstance(meta, dict) and "class" in meta:
                    if meta["class"] == "texto":
                        obj = ArchivoTexto(meta["ruta"], meta["tag"], id=cid)
                    elif meta["class"] == "datos":
                        obj = ArchivoDatos(meta["ruta"], meta["tag"], id=cid)
                    else:
                        obj = ArchivoBase(meta["ruta"], meta["tag"], id=cid)

                    archivos[obj.id] = obj
                else:
                    continue

        else:
            return {}

        return archivos

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


def resaltar(texto, palabra):
    palabra_l = palabra.lower()
    return re.sub(
        palabra_l,
        f"\033[96m{palabra_l}\033[0m",
        texto,
        flags=re.IGNORECASE
    )


def titulo(texto):
    color = "\033[94m"
    reset = "\033[0m"
    return f"""
{color}{'-' * 40}
{texto.center(40)}
{'-' * 40}{reset}
"""


#________Inferfaz del usuario_______

print("Hola! Bienvenido a InfoAnalytics, aquí podrás cargar archivos y generar informes con ellos.")
print("Nota: Puedes volver al menú principal en cualquier momento, solo escribe -1")

while True:
    try:
        print(titulo("Menú Principal"))
        n = input_num("Elige una opción:\n1. Cargar o eliminar archivo\n2. Ver archivos actuales\n3. Reporte de texto\n4. Reporte de datos\n5. Funciones Extra\n0. Finalizar\nOpción elegida: ")

        if n == 0:
            print("Programa finalizado.")
            break

        elif n == 1:
            print(titulo("Cargar o guardar archivo"))
            na = input_num("Elige una opción:\n0. Eliminar archivo\n1. Cargar archivo\nRespuesta: ")

            if na == 1:
                print("Carga archivos solo con su ruta en tu computador y un nombre para identificarlo")
                print("Tus archivos cargados persisten luego de parar el código")

                ruta_usuario = input_general("Ruta del archivo: ")
                nombre_ruta = input_general("Nombre para identificar el archivo: ")
                nt = input_num("Escribe el tipo de archivo:\n1.Tipo texto(.txt, .pdf, .docx, .csv de texto)\n2. Tipo Datos (.xlsx, .xls, .csv númerico)\nOpción Elegida: ")

                if nt == 1:
                    nuevo = ArchivoTexto(ruta_usuario, nombre_ruta)
                elif nt == 2:
                    nuevo = ArchivoDatos(ruta_usuario, nombre_ruta)
                else:
                    print("Opción inválida.")
                    continue

                archivos_cargados[nuevo.id] = nuevo
                guardar_archivos(archivos_cargados)

                print("El archivo ha sido cargado correctamente!")
                print(f"Archivo creado con ID {nuevo.id} y nombre '{nuevo.tag}'")

            elif na == 0:
                idb = input_num("ID del archivo que quieres eliminar: ")
                eliminar_archivo(idb, archivos_cargados)

        elif n == 2:
            print(titulo("Archivos cargados"))
            if not archivos_cargados:
                print("No hay archivos cargados actualmente.")
            else:
                for id_archivo, obj in archivos_cargados.items():
                    tipo = "Texto" if isinstance(obj, ArchivoTexto) else ("Datos" if isinstance(obj, ArchivoDatos) else "Base")
                    print(f"ID: {id_archivo} | Nombre: {obj.tag} | Ruta: {obj.ruta} | Tipo: {tipo}")

        elif n == 3:
            print(titulo("Reporte de texto"))
            print("Solo aplica para archivos de tipo texto")

            n3 = input_num("Ingresa el ID del archivo a analizar: ")

            try:
                archivo_obj = archivos_cargados[n3]
            except KeyError:
                print("Error: No existe un archivo con ese ID.")
                continue

            if not isinstance(archivo_obj, ArchivoTexto):
                print("Este tipo de archivo no es compatible con el análisis de texto.")
                continue

            archivo_obj.leer_archivo()
            reporte = AnalizadorTexto(archivo_obj)
            palabras = reporte.contar_palabras()
            frecuencia = reporte.palabras_frecuentes()
            densidad = reporte.densidad_lexica()
            longitud = reporte.longitud_promedio()
            idioma = reporte.detectar_idioma()
            print(titulo("Reporte"))
            print(f"Idioma detectado: {idioma}")
            print(f"Número de palabras: {palabras}")
            print("Palabras más comunes:")
            print(frecuencia)
            print(densidad)
            print(longitud)

        elif n == 4:
            print(titulo("Reporte de datos"))
            n4 = input_num("Ingresa el ID del archivo de datos: ")
            try:
                archivo_obj = archivos_cargados[n4]
            except KeyError:
                print("Error: No existe un archivo con ese ID.")
                continue

            if not isinstance(archivo_obj, ArchivoDatos):
                print("Este archivo no es de tipo datos.")
                continue

            archivo_obj.leer_archivo()
            print("Columnas: ", archivo_obj.obtener_columnas())
            print("Primeras filas:\n", archivo_obj.obtener_filas())

        elif n == 5:
            print(titulo("Funciones extra"))
            n5 = input_num("Ingresa el ID del archivo a analizar: ")
            ne = input_num("Elige una opción, o -1 para volver al menú:\n1. Encontrar Palabra\nFunción elegida: ")
            try:
                archivo_obj = archivos_cargados[n5]
            except KeyError:
                print("Error: No existe un archivo con ese ID.")
                continue

            if not isinstance(archivo_obj, ArchivoTexto):
                print("Las funciones extra de texto aplican solo a archivos de texto.")
                continue

            archivo_obj.leer_archivo()
            extra = AnalizadorExtra(archivo_obj)
            if ne == 1:
                palabra = input_general("Ingresa la palabra que quieres buscar en el texto: ")
                find = extra.encontrar_palabra(palabra)
                print(find)

    except VolverMenu:
        print("\nRegresando al menú principal...\n")

    except KeyError:
        print("Error: No existe un archivo con ese ID.")

    except ValueError:
        print("Entrada inválida. Por favor ingresa un número válido.")