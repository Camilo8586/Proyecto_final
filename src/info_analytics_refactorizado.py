# InfoAnalytics - versión refactorizada
#____Librerias____

#Instalar openpyxl para nuevos usuarios
try:
    import pickle
    import re
    from collections import Counter
    import pandas as pd
    from langdetect import detect
    import pdfplumber
    import docx
except ImportError:
    print("Se ha detectado que no se han instalado algunas librerias escenciales")
    print("Sigue los pasos del instructivo.txt en el proyecto de github para instalar las librerias necesarias")

#______Clases_______

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
#Clases de tipo de archivo
        
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
        
    def leer_archivo(self):
        if self.tipo == "csv":
            self.leer_csv()
        elif self.tipo == "xlsx":
            self.leer_excel()


    def leer_csv(self):
        try:
            self.dataframe = pd.read_csv(self.ruta, encoding="utf-8")
        except Exception as e:
            print("Error leyendo CSV:", e)

    def leer_excel(self):
        try:
            self.hojas = pd.read_excel(self.ruta, sheet_name=None)
            primer_nombre = list(self.hojas.keys())[0]
            self.dataframe = self.hojas[primer_nombre]
            self.hoja_actual = primer_nombre
    
        except Exception as e:
            print("Error leyendo Excel:", e)


#Clases de tipo de función

class AnalizadorTexto:
    def __init__(self, archivo):
        self.archivo = archivo
        self.texto = archivo.contenido.lower()
    def contar_palabras(self, devolver_valor=False):
        palabras = re.findall(r'\b[a-záéíóúñü]+', self.texto, re.IGNORECASE)
        total = len(palabras)

        if devolver_valor:
            return total

        return f"Número de palabras: {total}"
    def palabras_frecuentes(self, n=5):
        palabras = re.findall(r'\b[a-záéíóúñü]+', self.texto, re.IGNORECASE)
        contador = Counter(palabras)
        return contador.most_common(n)
    def densidad_lexica(self, devolver_valor=False):
        palabras = re.findall(r'\b[a-záéíóúñü]+\b', self.texto, re.IGNORECASE)

        if not palabras:
            if devolver_valor:
                return 0
            return "El texto no tiene palabras"

        vocabulario = set(palabras)
        densidad = round(len(vocabulario) / len(palabras), 2)

        if devolver_valor:
            return densidad   

      
        if densidad < 0.25:
            interpretacion = "El texto tiene una baja densidad léxica."
        elif densidad < 0.5:
            interpretacion = "El texto tiene una densidad léxica media."
        else:
            interpretacion = "El texto tiene una densidad léxica alta."

        return (
            f"La densidad léxica del texto es {densidad}\n"
            f"La densidad léxica es la cantidad de palabras únicas en tu texto sobre la cantidad de palabras totales.\n"
            f"{interpretacion}"
        )
    def longitud_promedio(self, devolver_valor=False):
        palabras = re.findall(r'\b\w+\b', self.texto, re.UNICODE)

        if not palabras:
            if devolver_valor:
                return 0
            return "No hay palabras en el texto"

        longitudes = [len(p) for p in palabras]
        promedio = round(sum(longitudes) / len(longitudes), 2)

        if devolver_valor:
            return promedio  

      
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

    def estadistica_puntuacion(self, devolver_valor=False):
        texto = self.texto
        idioma = self.detectar_idioma()

        rangos = {
            "Español": (8, 16),
            "Ingles": (10, 20),
            "Francés": (12, 22),
            "Alemán": (10, 18),
            "Portugues": (9, 17)
        }

        signos = r"[.,;:!?¿¡\"'()\[\]{}«»…]"

        signos_encontrados = len(re.findall(signos, texto))
        palabras = len(texto.split())

        if palabras == 0:
            if devolver_valor:
                return 0
            return "No se puede evaluar un texto vacío."

        porcentaje = (signos_encontrados / palabras) * 100

        if devolver_valor:
            return round(porcentaje, 2)  

        if idioma not in rangos:
            return (
                f"El porcentaje de uso de signos de puntuación cada 100 palabras es: {round(porcentaje, 2)}\n"
                f"No hay referencia de puntuación para este idioma."
            )

        r_min, r_max = rangos[idioma]
        esperado = (r_min + r_max) / 2
        desviacion = abs(porcentaje - esperado) / esperado

        if desviacion <= 0.20:
            interpretacion = "Muy buen uso de puntuación."
        elif desviacion <= 0.40:
            interpretacion = "Uso aceptable."
        elif desviacion <= 0.70:
            interpretacion = "Uso mejorable."
        else:
            interpretacion = "Uso deficiente o estilo inusual."

        return (
            f"El porcentaje de uso de signos de puntuación cada 100 palabras es: {round(porcentaje, 2)}\n"
            f"{interpretacion}"
        )


    
class AnalizadorDatos:
    def __init__(self, archivo):
        self.archivo = archivo
        self.df = archivo.dataframe
        
    def cambiar_hoja(self, nombre_hoja):
        if nombre_hoja in self.archivo.hojas:
            self.archivo.dataframe = self.archivo.hojas[nombre_hoja]
            self.archivo.hoja_actual = nombre_hoja
        else:
            print("La hoja no existe.")

    
    def listar_hojas(self):
        if hasattr(self.archivo, "hojas"):
            return list(self.archivo.hojas.keys())
        return []



    def resumen_general(self):
        filas, columnas = self.df.shape
        nulos_totales = self.df.isna().sum().sum()

        return (
            f"Filas:{filas}\nColumnas:{columnas}\nCeldas Vacias:{nulos_totales}"
            )

    
    def porcentaje_uso(self):
        filas, columnas = self.df.shape
        total = filas * columnas

        if total == 0:
            return (
                "Porcentaje de utilización: 0%\nEl archivo está vacio"
                )

        nulos = self.df.isna().sum().sum()
        llenas = total - nulos
        porcentaje = round((llenas / total) * 100, 2)

        if porcentaje < 30:
            mensaje = "Tu archivo contiene muchos espacios sin usar."
        elif porcentaje < 60:
            mensaje = "Tu archivo tiene una utilización moderada."
        elif porcentaje < 90:
            mensaje = "Tu archivo está bien aprovechado."
        else:
            mensaje = "Tu archivo tiene excelente utilización."

        return (
            f"Porcentaje de utilización: {porcentaje}\n{mensaje}"
            )
    
    
    def resumen_estadistico(self):
        if self.df is None or self.df.empty:
            return "El archivo no contiene datos para generar un resumen estadístico."

        df_num = self.df.select_dtypes(include="number")
    
        if df_num.empty:
            return "No hay columnas numéricas para generar un resumen estadístico."
    
        resultado = ["\n--- Resumen Estadístico por listas identificadas---\n"]
    
        for col in df_num.columns:
            serie = df_num[col].dropna()
    
            if serie.empty:
                continue
    
            minimo = serie.min()
            maximo = serie.max()
            media = serie.mean()
            mediana = serie.median()
            std = serie.std()
    

            interpretaciones = []

            if std == 0:
                interpretaciones.append("Todos los valores son iguales.")
            elif std < abs(media) * 0.1:
                interpretaciones.append("La variabilidad es muy baja.")
            elif std < abs(media) * 0.3:
                interpretaciones.append("Variabilidad moderada.")
            else:
                interpretaciones.append("Alta variabilidad en los datos.")
    
            if media > mediana * 1.1:
                interpretaciones.append("Distribución sesgada a la derecha (valores altos influyen la media).")
            elif media < mediana * 0.9:
                interpretaciones.append("Distribución sesgada a la izquierda.")
            else:
                interpretaciones.append("Distribución relativamente simétrica.")
    
            rango = maximo - minimo
            if rango > std * 6:
                interpretaciones.append("El rango es muy amplio, posible presencia de outliers.")
            elif rango < std * 2:
                interpretaciones.append("Rango compacto, pocos valores extremos.")
    
            resultado.append(
                f"\nColumna: {col}\n"
                f"  - Mínimo: {minimo}\n"
                f"  - Máximo: {maximo}\n"
                f"  - Media: {round(media, 3)}\n"
                f"  - Mediana: {round(mediana, 3)}\n"
                f"  - Desviación estándar: {round(std, 3)}\n"
                "\n  Interpretación:\n"
                "   • " + "\n   • ".join(interpretaciones) + "\n"
            )
    
        return "".join(resultado)

class AnalizadorExtra:
    
    def __init__(self, archivo):
        try:
            self.archivo = archivo
            self.texto = archivo.contenido.lower()
            self.lineas = archivo.contenido.splitlines()
        except AttributeError:
            self.archivo = archivo
            self.df = archivo.dataframe
            

    def encontrar_palabra(self, palabra):
        palabra_lower = palabra.lower()

        frecuencia = Counter(
            re.findall(r'\b[a-záéíóúñü]+', self.texto.lower())
        )[palabra_lower]
    
        if frecuencia == 0:
            return f"La palabra '{palabra}' no fue encontrada en el texto."

        contextos = []
    
        for num, linea in enumerate(self.lineas, start=1):
    
            if palabra_lower in linea.lower():
    
                contexto = linea.strip()
    
                if len(contexto) > 300:
                    contexto = contexto[:300].rstrip() + "..."
    
                contextos.append(f"Línea {num}: {contexto}")
    
            if len(contextos) == 5:
                break
    
        resultado = f"La palabra '{palabra}' aparece {frecuencia} veces.\n"
    
        if contextos:
            resultado += "\nPrimeras líneas encontradas con la palabra:\n" + "\n".join(contextos)
        else:
            resultado += "\nNo se encontraron líneas donde aparezca la palabra."
    
        return resultado

    def buscar_valor(self, valor):
        if not hasattr(self.archivo, "dataframe") or self.archivo.dataframe is None:
            return "Error: Este archivo no contiene datos tabulares. Carga un archivo de tipo datos (.xlsx, .xls, .csv)."
    
        df = self.archivo.dataframe
        try:
            valor_busqueda = float(valor)
        except ValueError:
            valor_busqueda = valor.lower().strip()
    
        resultados = []
    
        for fila in range(df.shape[0]):
            for col in range(df.shape[1]):
                celda = df.iat[fila, col]
    
                if isinstance(celda, str):
                    celda_comp = celda.lower().strip()
                else:
                    celda_comp = celda
    
                if celda_comp == valor_busqueda:
                    resultados.append((fila, col))
    
        if not resultados:
            return f"El valor '{valor}' no fue encontrado en el archivo."
    
        respuesta = f"Se encontraron {len(resultados)} coincidencias:\n"
    
        for fila, col in resultados:
            respuesta += f"\n→ Valor encontrado en Fila {fila}, Columna {col}\n"
            
            fila_ini = max(0, fila - 2)
            fila_fin = min(df.shape[0], fila + 3)
            col_ini  = max(0, col - 2)
            col_fin  = min(df.shape[1], col + 3)
    
            contexto = df.iloc[fila_ini:fila_fin, col_ini:col_fin]
            respuesta += f"Filas alrededor:\n{contexto}\n"
    
        return respuesta
    def generar_reporte_extra(self):
       analizador = AnalizadorTexto(self.archivo)
       reporte = {
           "palabras": analizador.contar_palabras(devolver_valor=True),
           "densidad_lexica": analizador.densidad_lexica(devolver_valor=True),
           "longitud_promedio": analizador.longitud_promedio(devolver_valor=True),
           "puntuacion": analizador.estadistica_puntuacion(devolver_valor=True),
           "idioma": analizador.detectar_idioma()  
       }

       return reporte

    def comparar_texto(self, archivo1, archivo2):
        reporte1 = AnalizadorExtra(archivo1).generar_reporte_extra()
        reporte2 = AnalizadorExtra(archivo2).generar_reporte_extra()

        claves_numericas = ["palabras", "densidad_lexica", "longitud_promedio", "puntuacion"]
        
        resultado = ""
        for clave in claves_numericas:
            valor1 = reporte1[clave]
            valor2 = reporte2[clave]

            if valor2 == 0:
                resultado += f"{clave}: No puede compararse (el archivo 2 tiene valor 0)\n"
                continue

            diferencia = ((valor1 - valor2) / valor2) * 100
            signo = "+" if diferencia >= 0 else "-"
            diferencia = abs(round(diferencia, 2))

            resultado += f"{clave}: {signo}{diferencia}%\n"

        if reporte1["idioma"] != reporte2["idioma"]:
            resultado += (
                f"\nIdiomas detectados: {reporte1['idioma']} vs {reporte2['idioma']} "
                "Los idiomas de los textos son diferentes, por lo que algunas comparaciones pueden no ser muy justas o considerables\n"
            )
        else:
            resultado += f"\nAmbos textos están en {reporte1['idioma']}\n"

        return resultado


class VolverMenu(Exception):
    pass


#______Funciones utiles__________

#Funciones persistencia

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

#Funciones Estilo


def input_general(mensaje):
    respuesta = input(mensaje)
    if respuesta.strip() == "-1":
        raise VolverMenu
    return respuesta


def input_num(mensaje):
    return int(input_general(mensaje))


def titulo(texto):
    linea = "-" * 40
    texto_centrado = texto.center(40)
    return f"\n{linea}\n{texto_centrado}\n{linea}\n"

#Funciones de outputs 

def exportar_reporte(contenido, nombre_archivo="reporte.txt"):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Reporte exportado correctamente como '{nombre_archivo}'")
        print(f"Recuerda que el archivo {nombre_archivo} ha sido creado en la misma carpeta donde ejecutas el programa, tienes que abrirlo manualmente")
    except Exception as e:
        print(f"Error al exportar el archivo: {e}")



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
        #Cargar un archivo

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

        #Ver archivos
        
        elif n == 2:
            print(titulo("Archivos cargados"))
            if not archivos_cargados:
                print("No hay archivos cargados actualmente.")
            else:
                for id_archivo, obj in archivos_cargados.items():
                    tipo = "Texto" if isinstance(obj, ArchivoTexto) else ("Datos" if isinstance(obj, ArchivoDatos) else "Base")
                    print(f"ID: {id_archivo} | Nombre: {obj.tag} | Ruta: {obj.ruta} | Tipo: {tipo}")

        #Analizar un archivo de texto
        
        elif n == 3:
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
            puntuacion = reporte.estadistica_puntuacion()
            reporte_total = (
                f"Idioma detectado: {idioma}\n"
                f"Número de palabras: {palabras}\n"
                f"{puntuacion}\n"
                f"Palabras más comunes:\n{frecuencia}\n\n"
                f"{densidad}\n\n"
                f"{longitud}\n"
            )

            exportar = input_num("¿Deseas exportar este reporte?:\n1. Si (descargarás un archivo .txt)\n2. No (verás el reporte en la consola de python)\nOpción elegida: ")
            if exportar == 1:
                nombre = input("Escribe el nombre del archivo (sin .txt): ").strip()
                exportar_reporte(reporte_total, nombre + ".txt")
            elif exportar == 2:
                print(titulo("Reporte de texto"))
                print(reporte_total)
        
        #Analizar un archivo de datos

        elif n == 4:

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
            reporte = AnalizadorDatos(archivo_obj)
            if archivo_obj.tipo == "xlsx":
                hojas = reporte.listar_hojas()
                if len(hojas) > 1:
                    print("Este archivo tiene múltiples hojas:")
                    for i, h in enumerate(hojas, start=1):
                        print(f"{i}. {h}")
                    eleccion = input_num("¿Qué hoja deseas analizar? Ingresa el número: ")
                    try:
                        nombre_hoja = hojas[eleccion - 1]
                        reporte.cambiar_hoja(nombre_hoja)
                        print(f"Ahora analizando la hoja: {nombre_hoja}")
                    except:
                        print("Selección inválida, se usará la primera hoja.\n")

            general = reporte.resumen_general()
            utilizacion = reporte.porcentaje_uso()
            estadistico = reporte.resumen_estadistico()
            # Construir reporte completo
            reporte_total = (
                f"{general}\n\n"
                f"{utilizacion}\n\n"
                f"{estadistico}\n"
            )
            
            exportar = input_num("¿Deseas exportar este reporte?:\n1. Si (descargarás un archivo .txt)\n2. No (verás el reporte en la consola de python)\nOpción elegida: ")
            if exportar == 1:
               nombre = input("Escribe el nombre del archivo (sin .txt): ").strip()
               exportar_reporte(reporte_total, nombre + ".txt")
            elif exportar == 2:
                print(titulo("Reporte de datos"))
                print(reporte_total)

         #Usar las funciones extra

        elif n == 5:
            print(titulo("Funciones extra"))
            ne = input_num("Elige una opción, o -1 para volver al menú:\n1. Encontrar Palabra (archivos texto)\n2.Encontrar Valor (archivos datos)\n3. Comparar archivos (solo archivos texto)\nFunción elegida: ")
            

            if ne == 1:   
                n5 = input_num("Ingresa el ID del archivo a analizar: ")
                try:
                    archivo_obj = archivos_cargados[n5]
                except KeyError:
                    print("Error: No existe un archivo con ese ID.")
                    continue
                archivo_obj.leer_archivo()
                extra = AnalizadorExtra(archivo_obj)
                archivo_obj.leer_archivo()
                if not isinstance(archivo_obj, ArchivoTexto):
                    print("Error: Esta función solo aplica a archivos de texto.")
                    continue
                palabra = input_general("Ingresa la palabra que quieres buscar en el texto: ")
                find = extra.encontrar_palabra(palabra)
                print(find)
            
            elif ne == 2:  
                n5 = input_num("Ingresa el ID del archivo a analizar: ")
                try:
                    archivo_obj = archivos_cargados[n5]
                except KeyError:
                    print("Error: No existe un archivo con ese ID.")
                    continue
                if not isinstance(archivo_obj, ArchivoDatos):
                    print("Error: Esta función solo aplica a archivos de datos (.xlsx o .csv numéricos).")
                    continue
                archivo_obj.leer_archivo()
                extra = AnalizadorExtra(archivo_obj)
                archivo_obj.leer_archivo()
                valor = input("Ingresa el valor que deseas buscar: ")
                find = extra.buscar_valor(valor)
                print(find)
            elif ne == 3:
                n51 = input_num("Ingresa el ID del primer archivo a comparar: ")
                try:
                    archivo_obj1 = archivos_cargados[n51]
                except KeyError:
                    print("Error: No existe un archivo con ese ID.")
                    continue

                if not isinstance(archivo_obj1, ArchivoTexto):
                    print("Error: Esta función solo aplica a archivos de texto.")
                    continue
                archivo_obj1.leer_archivo()
                archivo1 = AnalizadorExtra(archivo_obj1)
                archivo_obj1.leer_archivo()
                n52 = input_num("Ingresa el ID del segundo archivo a comparar: ")
                try:
                    archivo_obj2 = archivos_cargados[n52]
                except KeyError:
                    print("Error: No existe un archivo con ese ID.")
                    continue

                if not isinstance(archivo_obj2, ArchivoTexto):
                    print("Error: Esta función solo aplica a archivos de texto.")
                    continue
                archivo_obj2.leer_archivo()
                archivo_obj2.leer_archivo()
                comparacion = archivo1.comparar_texto(archivo_obj1, archivo_obj2)
                print(titulo("Comparación de archivos"))
                print("Cada porcentaje tiene un signo + o - al frente\nSi el signo al frente del porcentaje es +, el texto 1 gana la comparación\nSi el signo al frente del porcentaje es -, el texto 2 gana la comparación ")
                print(comparacion)
    except VolverMenu:
        print("\nRegresando al menú principal...\n")

    except KeyError:
        print("Error: No existe un archivo con ese ID.")

    except ValueError:
        print("Entrada inválida. Por favor ingresa un número válido.")