"""
Proyecto final 

"""
contenido = []
def leer_archivo(ruta):
    """Lee un archivo de texto y devuelve su contenido como una cadena."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        texto = archivo.read()
    try:
        contenido.append(texto)
        return ("El archivo ha sido cargado correctamente!")  
    except FileNotFoundError:
        return ("No se encontró el archivo. Verifica que el nombre o la ruta sean correctos.")
    except UnicodeDecodeError:
        return ("Error de codificación: el archivo no está en formato UTF-8.")
    except Exception as e:
        return(f"Ocurrió un error inesperado: {e}")
        
n = 1
ruta_usuario = input("Hola!,bienvenido a Info Analytics,d escribe la ruta o nombre del archivo que deseas leer para comenzar: ")

print(leer_archivo(ruta_usuario))
    
while n != 0:

    n = int(input("Escribe la opción que quieres realizar: "))
    
    if n == 1:
        print("Haz elegido la opción: cargar nuevo archivo ")
        ruta_usuario = input("Escribe la ruta o nombre del archivo que deseas leer: ")
    
        try:
            contenido.append(leer_archivo(ruta_usuario))
            print("El archivo ha sido cargado correctamente!")
    
        except FileNotFoundError:
            print("No se encontró el archivo. Verifica que el nombre o la ruta sean correctos.")
        except UnicodeDecodeError:
            print("Error de codificación: el archivo no está en formato UTF-8.")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
    
    elif n == 2:
        print("Haz elegido la opción: Ver archivos actuales")
        print(contenido)
        