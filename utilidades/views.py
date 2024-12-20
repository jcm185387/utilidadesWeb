import qrcode

from django.shortcuts import render

from io import BytesIO
from django.http import HttpResponse


from datetime import datetime, timedelta
import random  # Asegúrate de importar el módulo random
import requests
from spellchecker import SpellChecker  # Instalar con 'pip install pyspellchecker'

import json
import string

from lxml import etree
from django.http import JsonResponse

import base64



def contador_fechas(request):
    resultado = None
    if request.method == 'POST':
        fecha_inicial = request.POST.get('fecha_inicial')
        fecha_final = request.POST.get('fecha_final')
        incluir_inicial = request.POST.get('incluir_inicial') == 'on'

        if fecha_inicial and fecha_final:
            fecha_inicial = datetime.strptime(fecha_inicial, '%Y-%m-%d')
            fecha_final = datetime.strptime(fecha_final, '%Y-%m-%d')

            if incluir_inicial:
                fecha_final += timedelta(days=1)

            dias_corridos = (fecha_final - fecha_inicial).days
            dias_habiles_lun_vie = sum(1 for i in range(dias_corridos) if (fecha_inicial + timedelta(days=i)).weekday() < 5)
            dias_habiles_lun_sab = sum(1 for i in range(dias_corridos) if (fecha_inicial + timedelta(days=i)).weekday() < 6)
            
            semanas = dias_corridos / 7
            meses = dias_corridos / 30.44
            años = dias_corridos / 365.25

            resultado = {
                'dias_corridos': dias_corridos,
                'dias_habiles_lun_vie': dias_habiles_lun_vie,
                'dias_habiles_lun_sab': dias_habiles_lun_sab,
                'semanas': round(semanas, 2),
                'meses': round(meses, 2),
                'años': round(años, 2),
            }
    
    return render(request, 'utilidades/contador_fechas.html', {'resultado': resultado})

def pagina_principal(request):
    return render(request, 'utilidades/pagina_principal.html')

def calculadora_edad(request):
    resultado = None
    fecha_nacimiento = ""
    fecha_fin = ""

    if request.method == "POST":
        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        fecha_fin = request.POST.get("fecha_fin")

        if fecha_nacimiento and fecha_fin:
            fecha_nacimiento_dt = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
            
            # Calcular la diferencia
            diferencia = fecha_fin_dt - fecha_nacimiento_dt
            total_dias = diferencia.days
            
            # Convertir a años, meses y días
            anios = total_dias // 365
            meses = (total_dias % 365) // 30
            dias = (total_dias % 365) % 30

            resultado = {
                "anios": anios,
                "meses": meses,
                "dias": dias,
                "total_dias": total_dias,
            }

    return render(request, "utilidades/calculadora_edad.html", {
        "resultado": resultado,
        "fecha_nacimiento": fecha_nacimiento,
        "fecha_fin": fecha_fin,
    })

def generador_curp(request):
    curp = None
    with open('static/estados_mexico.json', 'r', encoding='utf-8') as file:
        estados = json.load(file)

    if request.method == 'POST':
        # Captura los datos tal cual
        nombre = request.POST.get('nombre')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        sexo = request.POST.get('sexo')
        estado = request.POST.get('estado')

        # Genera la CURP sin modificaciones innecesarias
        curp = generar_curp_falso(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado)

    return render(request, 'utilidades/generador_curp.html', {'curp': curp, 'estados': estados})

def generar_curp_falso(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado):
    # Usa los datos directamente sin cambios
    letras = (apellido_paterno[0:2] + apellido_materno[0:1] + nombre[0:1])
    fecha = fecha_nacimiento.replace("-", "")[2:]
    homoclave = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))
    return f"{letras.upper()}{fecha}{sexo.upper()}{estado.upper()}XX{homoclave}"

def generador_rfc(request):
    rfc = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre', 'JUAN')
        apellido_paterno = request.POST.get('apellido_paterno', 'PEREZ')
        apellido_materno = request.POST.get('apellido_materno', 'GARCIA')
        fecha_nacimiento = request.POST.get('fecha_nacimiento', '1990-01-01')

        rfc = generar_rfc_falso(nombre, apellido_paterno, apellido_materno, fecha_nacimiento)

    return render(request, 'utilidades/generador_rfc.html', {'rfc': rfc})

def generar_rfc_falso(nombre, apellido_paterno, apellido_materno, fecha_nacimiento):
    # Se toman las primeras letras de los apellidos y del primer nombre
    letras = (apellido_paterno[0:2] + apellido_materno[0:1] + nombre[0:1]).upper()
    
    # Se toma la fecha de nacimiento, sin guiones, y se usan los dos últimos dígitos del año
    fecha = fecha_nacimiento.replace("-", "")[2:]
    
    # Generación de una homoclave aleatoria (tres caracteres alfanuméricos)
    homoclave = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))
    
    # El RFC final es la combinación de las letras, la fecha y la homoclave
    return f"{letras}{fecha}{homoclave}"

def generador_nombres(request):
    nombre_generado = None
    pais = 'México'  # Valor por defecto

    # Verificar si el país está en el POST, de lo contrario, usar el valor por defecto
    pais = request.POST.get('pais', 'México')
    print(f"País seleccionado: {pais}")
    
    # Construir la URL de la API basada en el país seleccionado
    paises_api = {
        "México": "mx",
        "Estados Unidos": "us",
        "España": "es",
        "Brasil": "BR",
        # Puedes agregar más países aquí si lo deseas
    }
    print("Países disponibles en la API:", paises_api)
    
    # Obtener el código del país según la selección del usuario
    pais_code = paises_api.get(pais, "mx")  # Si el país no está en el diccionario, por defecto usa "mx" (México)

    # URL dinámica de la API basada en el país seleccionado
    url_api = f'https://randomuser.me/api/?nat={pais_code}'
    print(f"URL de la API: {url_api}")
    
    try:
        # Hacer la solicitud GET a la API para obtener los datos de los perfiles
        response = requests.get(url_api)
        response.raise_for_status()  # Lanzará una excepción si la solicitud falla

        # Verificar la respuesta y el formato
        data = response.json()
        print("Respuesta de la API:", data)  # Imprimir respuesta de la API para verificar

        # Extraer los datos del primer usuario en la respuesta
        if data['results']:
            user = data['results'][0]
            
            # Extraer la información relevante
            title = user['name']['title']
            first_name = user['name']['first']
            last_name = user['name']['last']
            city = user['location']['city']
            state = user['location']['state']
            country = user['location']['country']
            postcode = user['location']['postcode']
            email = user['email']
            phone = user['phone']
            age = user['dob']['age']

            # Mostrar los datos para depuración
            print(f"Nombre completo: {title} {first_name} {last_name}")
            print(f"Ubicación: {city}, {state}, {country}, {postcode}")
            print(f"Correo electrónico: {email}")
            print(f"Teléfono: {phone}")
            print(f"Edad: {age}")
            
            # Crear un diccionario con los datos a mostrar
            nombre_generado = {
                'title': title,
                'first_name': first_name,
                'last_name': last_name,
                'city': city,
                'state': state,
                'country': country,
                'postcode': postcode,
                'email': email,
                'phone': phone,
                'age': age
            }
        else:
            nombre_generado = "No hay nombres disponibles para este país."

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los nombres de la API: {e}")
        nombre_generado = "Error al obtener datos."

    # Pasar los datos extraídos a la plantilla
    return render(request, 'utilidades/generador_nombres.html', {
        'nombre': nombre_generado, 
        'pais': pais
    })


def contador_palabras(request):
    if request.method == "POST":
        texto = request.POST.get('texto', '')
        num_palabras = len(texto.split()) if texto else 0
        num_caracteres = len(texto) if texto else 0
        return render(request, 'utilidades/contador_palabras.html', {
            'num_palabras': num_palabras,
            'num_caracteres': num_caracteres,
            'texto': texto,
        })
    return render(request, 'utilidades/contador_palabras.html')




def corrector_ortografico(request):
    corregido = None
    if request.method == "POST":
        texto = request.POST.get('texto', '')
        
        # Crear un objeto SpellChecker para el idioma español
        spell = SpellChecker(language='es')
        
        # Dividir el texto en palabras
        palabras = texto.split()
        
        # Corregir las palabras, comprobando si el resultado es None
        corregidas = [
            spell.correction(palabra) if spell.correction(palabra) is not None else palabra
            for palabra in palabras
        ]
        
        # Unir las palabras corregidas en un solo texto
        corregido = ' '.join(corregidas)
        
        # Renderizar el resultado en la página
        return render(request, 'utilidades/corrector_ortografico.html', {
            'corregido': corregido,
            'texto': texto,
        })
    
    return render(request, 'utilidades/corrector_ortografico.html')



def generador_palabras_clave(request):
    palabras_base = ['SEO', 'optimización', 'marketing', 'contenido', 'estrategia', 'palabras clave', 'redes sociales']
    palabras_generadas = random.sample(palabras_base, len(palabras_base))  # Selecciona palabras aleatorias
    if request.method == 'POST':
        texto = request.POST.get('texto', '')
        # Aquí podrías añadir lógica para generar palabras clave basadas en el texto ingresado.
        palabras_generadas = texto.split()  # Simple ejemplo: dividir el texto en palabras individuales
    return render(request, 'utilidades/generador_palabras_clave.html', {
        'palabras_generadas': palabras_generadas,
    })


def generador_qr(request):
    qr_code = None
    texto = None
    if request.method == 'POST':
        texto = request.POST.get('texto', '')
        if texto:
            # Generar el código QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(texto)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            # Codificar la imagen en base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            qr_code = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'utilidades/generador_qr.html', {'qr_code': qr_code, 'texto': texto})


def minificador_css_js(request):
    minificado = None
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        tipo_archivo = archivo.name.split('.')[-1]
        
        if archivo:
            contenido = archivo.read().decode('utf-8')

            if tipo_archivo == 'css':
                # Minificar CSS
                minificado = contenido.replace('\n', '').replace('  ', '')
            elif tipo_archivo == 'js':
                # Minificar JS
                minificado = contenido.replace('\n', '').replace('  ', '')

    return render(request, 'utilidades/minificador_css_js.html', {'minificado': minificado})


def validador_json_xml(request):
    resultado = None
    resultado_valido = False
    errores = []
    if request.method == 'POST':
        texto = request.POST.get('texto', '')
        if texto:
            try:
                # Attempt to load as JSON
                json.loads(texto)
                resultado = "El texto es un JSON válido."
                resultado_valido = True
            except json.JSONDecodeError as e:
                errores.append(f"Error en JSON: {str(e)}")  

                # Attempt to load as XML if JSON fails
                try:
                    etree.fromstring(texto)
                    resultado = "El texto es un XML válido."
                    resultado_valido = True
                    errores = []  # Clear errors if XML is valid
                except etree.XMLSyntaxError as e:
                    errores.append(f"Error en XML: {str(e)}")

            if not resultado:
                resultado = "El texto no es ni JSON ni XML válido."
                resultado_valido = False

    return render(request, 'utilidades/validador_json_xml.html', {
        'resultado': resultado,
        'errores': errores,
        'resultado_valido': resultado_valido
    })

def generador_contrasenas(request):
    contrasena = ""
    error = None  # Variable para manejar el mensaje de error

    if request.method == 'POST':
        longitud = int(request.POST.get('longitud', 12))
        mayusculas = request.POST.get('mayusculas', 'off')
        minusculas = request.POST.get('minusculas', 'off')
        numeros = request.POST.get('numeros', 'off')
        simbolos = request.POST.get('simbolos', 'off')

        # Validar que al menos un checkbox esté seleccionado
        if mayusculas == 'off' and minusculas == 'off' and numeros == 'off' and simbolos == 'off':
            error = "Debes seleccionar al menos una opción (mayúsculas, minúsculas, números o símbolos)."
        else:
            caracteres = ''
            if mayusculas == 'on':
                caracteres += string.ascii_uppercase
            if minusculas == 'on':
                caracteres += string.ascii_lowercase
            if numeros == 'on':
                caracteres += string.digits
            if simbolos == 'on':
                caracteres += string.punctuation

            contrasena = ''.join(random.choice(caracteres) for _ in range(longitud))

        context = {
            'contrasena': contrasena,
            'longitud': longitud,
            'mayusculas': mayusculas,
            'minusculas': minusculas,
            'numeros': numeros,
            'simbolos': simbolos,
            'error': error,  # Incluimos el mensaje de error en el contexto
        }
    else:
        # Valores por defecto
        longitud = 12
        mayusculas = 'on'
        minusculas = 'on'
        numeros = 'on'
        simbolos = 'on'
        context = {
            'longitud': longitud,
            'mayusculas': mayusculas,
            'minusculas': minusculas,
            'numeros': numeros,
            'simbolos': simbolos,
            'error': error,
        }

    return render(request, 'utilidades/generador_contrasenas.html', context)



# Replace with your API key
API_KEY = 'a8cdeeeefba3e029825fa812'
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest"
API_URLCODES = f"https://v6.exchangerate-api.com/v6/{API_KEY}"
'''
def obtener_monedas_disponibles():
    response = requests.get(f"{API_URL}/USD")  # Usamos USD como base
    if response.status_code == 200:
        data = response.json()
        ##print(data)
        if "conversion_rates" in data:
            return list(data["conversion_rates"].keys())  # Obtener todas las monedas disponibles
    return []

def obtener_tipo_cambio(moneda_origen, moneda_destino):
    # Obtener el tipo de cambio entre las dos monedas seleccionadas
    response = requests.get(f"{API_URL}/{moneda_origen}")
    if response.status_code == 200:
        data = response.json()
        if "conversion_rates" in data and moneda_destino in data["conversion_rates"]:
            return data["conversion_rates"][moneda_destino]
    return None

def conversor_divisas(request):
    mensaje_error = None
    monedas_disponibles = obtener_monedas_disponibles()  # Obtener las monedas disponibles al cargar el formulario

    if request.method == 'POST':
        # Obtener los parámetros del formulario
        moneda_origen = request.POST.get('moneda_origen')
        moneda_destino = request.POST.get('moneda_destino')
        cantidad = float(request.POST.get('cantidad'))

        # Verificar que las monedas no sean iguales
        if moneda_origen == moneda_destino:
            mensaje_error = "La moneda origen no puede ser igual a la moneda destino."
        else:
            # Consultar el tipo de cambio
            tasa = obtener_tipo_cambio(moneda_origen, moneda_destino)

            if tasa is None:
                mensaje_error = "Error al obtener la tasa de cambio. Intenta más tarde."
            else:
                # Realizar la conversión
                resultado = cantidad * tasa
                return render(request, 'utilidades/conversor_divisas.html', {
                    'moneda_origen': moneda_origen,
                    'moneda_destino': moneda_destino,
                    'cantidad': cantidad,
                    'resultado': resultado,
                    'tasa': tasa,
                    'mensaje_error': mensaje_error,
                    'monedas_disponibles': monedas_disponibles
                })

    # Si hay un error o no se ha enviado el formulario, renderizamos el formulario original
    return render(request, 'utilidades/conversor_divisas.html', {
        'mensaje_error': mensaje_error,
        'moneda_origen': 'USD',  # Moneda por defecto
        'moneda_destino': 'MXN',  # Moneda por defecto
        'cantidad': 0,
        'monedas_disponibles': monedas_disponibles
    })
'''
MONEDAS_EN_ES = {
    "AED": "Dirham de los Emiratos Árabes Unidos",
    "AFN": "Afghani afgano",
    "ALL": "Lek albanés",
    "AMD": "Drama armenio",
    "ANG": "Florín antillano neerlandés",
    "AOA": "Kwanza angoleña",
    "ARS": "Peso argentino",
    "AUD": "Dólar australiano",
    "AWG": "Florenio arubeño",
    "AZN": "Manat azerbaiyano",
    "BAM": "Marco convertible de Bosnia y Herzegovina",
    "BBD": "Dólar barbadeño",
    "BDT": "Taka bangladesí",
    "BGN": "Lev búlgaro",
    "BHD": "Dinar bahreiní",
    "BIF": "Franco burundés",
    "BMD": "Dólar bermudeño",
    "BND": "Dólar bruneano",
    "BOB": "Boliviano boliviano",
    "BRL": "Real brasileño",
    "BSD": "Dólar bahameño",
    "BTN": "Ngultrum bhutanés",
    "BWP": "Pula botsuano",
    "BYN": "Rublo bielorruso",
    "BZD": "Dólar beliceño",
    "CAD": "Dólar canadiense",
    "CDF": "Franco congoleño",
    "CHF": "Franco suizo",
    "CLP": "Peso chileno",
    "CNY": "Renminbi chino",
    "COP": "Peso colombiano",
    "CRC": "Colón costarricense",
    "CUP": "Peso cubano",
    "CVE": "Escudo caboverdiano",
    "CZK": "Corona checa",
    "DJF": "Franco yibutiano",
    "DKK": "Corona danesa",
    "DOP": "Peso dominicano",
    "DZD": "Dinar argelino",
    "EGP": "Libra egipcia",
    "ERN": "Nakfa eritreo",
    "ETB": "Birr etíope",
    "EUR": "Euro",
    "FJD": "Dólar fiyiano",
    "FKP": "Libra de las Islas Malvinas",
    "FOK": "Corona de las Islas Feroe",
    "GBP": "Libra esterlina",
    "GEL": "Lari georgiano",
    "GGP": "Libra de Guernsey",
    "GHS": "Cedi ghanés",
    "GIP": "Libra de Gibraltar",
    "GMD": "Dalasi gambiano",
    "GNF": "Franco guineano",
    "GTQ": "Quetzal guatemalteco",
    "GYD": "Dólar guyanés",
    "HKD": "Dólar de Hong Kong",
    "HNL": "Lempira hondureña",
    "HRK": "Kuna croata",
    "HTG": "Gourde haitiano",
    "HUF": "Forinto húngaro",
    "IDR": "Rupia indonesia",
    "ILS": "Nuevo shekel israelí",
    "IMP": "Libra de la Isla de Man",
    "INR": "Rupia india",
    "IQD": "Dinar iraquí",
    "IRR": "Rial iraní",
    "ISK": "Corona islandesa",
    "JEP": "Libra de Jersey",
    "JMD": "Dólar jamaiquino",
    "JOD": "Dinar jordano",
    "JPY": "Yen japonés",
    "KES": "Chelín keniano",
    "KGS": "Som kirguís",
    "KHR": "Riel camboyano",
    "KID": "Dólar de Kiribati",
    "KMF": "Franco comorano",
    "KRW": "Won surcoreano",
    "KWD": "Dinar kuwaití",
    "KYD": "Dólar de las Islas Caimán",
    "KZT": "Tenge kazajo",
    "LAK": "Kip laosiano",
    "LBP": "Libra libanesa",
    "LKR": "Rupia de Sri Lanka",
    "LRD": "Dólar liberiano",
    "LSL": "Loti de Lesoto",
    "LYD": "Dinar libio",
    "MAD": "Dirham marroquí",
    "MDL": "Leu moldavo",
    "MGA": "Ariary malgache",
    "MKD": "Denar macedonio",
    "MMK": "Kyat birmano",
    "MNT": "Tögrög mongol",
    "MOP": "Pataca macanesa",
    "MRU": "Ouguiya mauritano",
    "MUR": "Rupia mauriciana",
    "MVR": "Rufiyaa maldivo",
    "MWK": "Kwacha malawiano",
    "MXN": "Peso mexicano",
    "MYR": "Ringgit malayo",
    "MZN": "Metical mozambiqueño",
    "NAD": "Dólar namibio",
    "NGN": "Naira nigeriana",
    "NIO": "Córdoba nicaragüense",
    "NOK": "Corona noruega",
    "NPR": "Rupia nepalí",
    "NZD": "Dólar neozelandés",
    "OMR": "Rial omaní",
    "PAB": "Balboa panameño",
    "PEN": "Sol peruano",
    "PGK": "Kina papú de Nueva Guinea",
    "PHP": "Peso filipino",
    "PKR": "Rupia pakistaní",
    "PLN": "Zloty polaco",
    "PYG": "Guaraní paraguayo",
    "QAR": "Riyal qatarí",
    "RON": "Leu rumano",
    "RSD": "Dinar serbio",
    "RUB": "Rublo ruso",
    "RWF": "Franco ruandés",
    "SAR": "Riyal saudí",
    "SBD": "Dólar de las Islas Salomón",
    "SCR": "Rupia seychellense",
    "SDG": "Libra sudanesa",
    "SEK": "Corona sueca",
    "SGD": "Dólar singapurense",
    "SHP": "Libra de Santa Elena",
    "SLE": "León de Sierra Leona",
    "SLL": "León de Sierra Leona",
    "SOS": "Chelín somalí",
    "SRD": "Dólar surinamés",
    "SSP": "Libra sursudanesa",
    "STN": "Dobra de Santo Tomé y Príncipe",
    "SYP": "Libra siria",
    "SZL": "Lilangeni de Eswatini",
    "THB": "Baht tailandés",
    "TJS": "Somoni tayiko",
    "TMT": "Manat turcomano",
    "TND": "Dinar tunecino",
    "TOP": "Paʻanga tongano",
    "TRY": "Lira turca",
    "TTD": "Dólar de Trinidad y Tobago",
    "TVD": "Dólar tuvaluano",
    "TWD": "Nuevo dólar taiwanés",
    "TZS": "Chelín tanzano",
    "UAH": "Hryvnia ucraniana",
    "UGX": "Chelín ugandés",
    "USD": "Dólar estadounidense",
    "UYU": "Peso uruguayo",
    "UZS": "So'm uzbeko",
    "VES": "Bolívar venezolano soberano",
    "VND": "Dong vietnamita",
    "VUV": "Vatu vanuatuense",
    "WST": "Tālā samoano",
    "XAF": "Franco CFA central africano",
    "XCD": "Dólar del Caribe oriental",
    "XDR": "Derechos especiales de giro",
    "XOF": "Franco CFA de África Occidental",
    "XPF": "Franco CFP",
    "YER": "Rial yemení",
    "ZAR": "Rand sudafricano",
    "ZMW": "Kwacha zambiano",
    "ZWL": "Dólar zimbabuense"
}

def obtener_monedas_disponibles():
    response = requests.get(f"{API_URLCODES}/codes")  # Obtener los códigos de las monedas
    if response.status_code == 200:
        data = response.json()
        if "supported_codes" in data:
            # Convertimos la lista de listas en un diccionario
            monedas_dict = {codigo: descripcion for codigo, descripcion in data["supported_codes"]}
            # Traducimos las descripciones al español usando el diccionario
            monedas_traducidas = {codigo: MONEDAS_EN_ES.get(codigo, descripcion) 
                                  for codigo, descripcion in monedas_dict.items()}
            return monedas_traducidas  # Devolvemos el diccionario con las descripciones en español
    return {}


def obtener_tipo_cambio(moneda_origen, moneda_destino):
    # Obtener el tipo de cambio entre las dos monedas seleccionadas
    response = requests.get(f"{API_URL}/{moneda_origen}")
    if response.status_code == 200:
        data = response.json()
        if "conversion_rates" in data and moneda_destino in data["conversion_rates"]:
            return data["conversion_rates"][moneda_destino]
    return None

def conversor_divisas(request):
    mensaje_error = None
    monedas_disponibles = obtener_monedas_disponibles()  # Obtener las monedas disponibles
    ##print(monedas_disponibles)
    if request.method == 'POST':
        # Obtener los parámetros del formulario
        moneda_origen = request.POST.get('moneda_origen')
        moneda_destino = request.POST.get('moneda_destino')
        cantidad = float(request.POST.get('cantidad'))

        # Verificar que las monedas no sean iguales
        if moneda_origen == moneda_destino:
            mensaje_error = "La moneda origen no puede ser igual a la moneda destino."
        else:
            # Consultar el tipo de cambio
            tasa = obtener_tipo_cambio(moneda_origen, moneda_destino)

            if tasa is None:
                mensaje_error = "Error al obtener la tasa de cambio. Intenta más tarde."
            else:
                # Realizar la conversión
                resultado = cantidad * tasa
                return render(request, 'utilidades/conversor_divisas.html', {
                    'moneda_origen': moneda_origen,
                    'moneda_destino': moneda_destino,
                    'cantidad': cantidad,
                    'resultado': resultado,
                    'tasa': tasa,
                    'mensaje_error': mensaje_error,
                    'monedas_disponibles': monedas_disponibles
                })

    # Si hay un error o no se ha enviado el formulario, renderizamos el formulario original
    return render(request, 'utilidades/conversor_divisas.html', {
        'mensaje_error': mensaje_error,
        'moneda_origen': 'USD',  # Moneda por defecto
        'moneda_destino': 'MXN',  # Moneda por defecto
        'cantidad': 0,
        'monedas_disponibles': monedas_disponibles
    })


def conversor_formatos(request):    
    resultado = None
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        
        # Aquí se podría agregar la lógica para convertir formatos, como usar alguna librería
        # de conversión de archivos, por ejemplo de PDF a Word.
        if archivo:
            # Ejemplo: convertimos un archivo PDF a texto
            resultado = "Archivo convertido exitosamente a formato Word."

    return render(request, 'utilidades/conversor_formatos.html', {'resultado': resultado})

#Conversor de unidades

CONVERSIONES = {
    "longitud": {
        "metros": 1,
        "kilometros": 0.001,
        "centimetros": 100,
        "milimetros": 1000,
        "millas": 0.000621371,
        "yardas": 1.09361,
        "pies": 3.28084,
        "pulgadas": 39.3701
    },
    "peso": {
        "kilogramos": 1,
        "gramos": 1000,
        "miligramos": 1000000,
        "toneladas": 0.001,
        "libras": 2.20462,
        "onzas": 35.274
    },
    "volumen": {
        "litros": 1,
        "mililitros": 1000,
        "centimetros_cubicos": 1000,
        "metros_cubicos": 0.001,
        "galones_estadounidenses": 0.264172,
        "galones_ingleses": 0.219969,
        "onzas_liquidas": 33.814,
        "tazas": 4.22675
    },
    "temperatura": {
        "celsius": "C",
        "fahrenheit": "F",
        "kelvin": "K"
    },
    "tiempo": {
        "segundos": 1,
        "minutos": 0.0166667,
        "horas": 0.000277778,
        "dias": 0.0000115741,
        "semanas": 0.0000016534,
        "meses": 3.80265e-7,
        "años": 3.17098e-8
    },
    "area": {
        "metros_cuadrados": 1,
        "kilometros_cuadrados": 0.000001,
        "pies_cuadrados": 10.7639,
        "yardas_cuadradas": 1.19599,
        "hectareas": 0.0001,
        "acres": 0.000247105
    },
    "velocidad": {
        "metros_por_segundo": 1,
        "kilometros_por_hora": 3.6,
        "millas_por_hora": 2.23694,
        "nudos": 1.94384
    },
    "almacenamiento": {
        "bytes": 1,
        "kilobytes": 0.001,
        "megabytes": 0.000001,
        "gigabytes": 0.000000001,
        "terabytes": 0.000000000001
    }
}




def conversor_unidades(request):
    resultado = None
    mensaje_error = None

    categorias = CONVERSIONES.keys()
    categoria_seleccionada = 'longitud'
    unidades = CONVERSIONES[categoria_seleccionada]
    
    valor = 0
    unidad_origen = 'metros'
    unidad_destino = 'pies'

    if request.method == 'POST':
        categoria_seleccionada = request.POST.get('categoria')
        unidades = CONVERSIONES.get(categoria_seleccionada, {})
        valor = float(request.POST.get('valor', 0))
        unidad_origen = request.POST.get('unidad_origen')
        unidad_destino = request.POST.get('unidad_destino')

        if unidad_origen == unidad_destino:
            mensaje_error = "La unidad de origen no puede ser igual a la unidad de destino."
        else:
            factor_origen = unidades.get(unidad_origen)
            factor_destino = unidades.get(unidad_destino)

            if factor_origen and factor_destino:
                resultado = valor * (factor_destino / factor_origen)
            else:
                mensaje_error = "Unidades seleccionadas no válidas."

    return render(request, 'utilidades/conversor_unidades.html', {
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
        'unidades': unidades,
        'resultado': resultado,
        'mensaje_error': mensaje_error,
        'valor': valor,
        'unidad_origen': unidad_origen,
        'unidad_destino': unidad_destino
    })


#OTROS

#GASOLINA PARA VIAJES:
def gastos_gasolina(request):
    # Inicializamos variables
    precio_premium = 0
    precio_magna = 0
    rendimiento = 0
    distancia = 0
    gasto_total = None
    mensaje_error = None

    if request.method == 'POST':
        try:
            # Capturamos los valores del formulario
            distancia = float(request.POST.get('distancia', 0))
            rendimiento = float(request.POST.get('rendimiento', 0))
            usar_premium = 'usar_premium' in request.POST
            usar_magna = 'usar_magna' in request.POST

            # Validamos los precios
            if usar_premium:
                precio_premium = float(request.POST.get('precio_premium', 0))
            if usar_magna:
                precio_magna = float(request.POST.get('precio_magna', 0))

            # Validación básica
            if distancia <= 0 or rendimiento <= 0:
                mensaje_error = "La distancia y el rendimiento deben ser mayores a 0."
            elif usar_premium and usar_magna and (precio_premium <= 0 or precio_magna <= 0):
                mensaje_error = "Debe ingresar precios válidos para ambas gasolinas."
            elif not usar_premium and not usar_magna:
                mensaje_error = "Debe seleccionar al menos un tipo de gasolina."
            else:
                # Cálculo del gasto total
                litros_necesarios = distancia / rendimiento
                if usar_premium and usar_magna:
                    gasto_total = {
                        'Premium': litros_necesarios * precio_premium,
                        'Magna': litros_necesarios * precio_magna
                    }
                elif usar_premium:
                    gasto_total = {'Premium': litros_necesarios * precio_premium}
                elif usar_magna:
                    gasto_total = {'Magna': litros_necesarios * precio_magna}
        except ValueError:
            mensaje_error = "Por favor, ingrese valores numéricos válidos."

    return render(request, 'utilidades/gastos_gasolina.html', {
        'distancia': distancia,
        'rendimiento': rendimiento,
        'precio_premium': precio_premium,
        'precio_magna': precio_magna,
        'gasto_total': gasto_total,
        'mensaje_error': mensaje_error,
    })



#romanos a decimales y viceversa

# Funciones para convertir números decimales a romanos y viceversa
import re

# Funciones para convertir números decimales a romanos y viceversa
def decimal_a_romano(num):
    valores = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    romano = ""
    for valor, simbolo in valores:
        while num >= valor:
            romano += simbolo
            num -= valor
    return romano

def romano_a_decimal(romano):
    valores = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000
    }
    total = 0
    prev_value = 0
    for letra in reversed(romano):
        value = valores[letra]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    return total

def conversor_numeros(request):
    resultado_decimal = 1  # Valor inicial para la conversión decimal
    resultado_romano = 'I'  # Valor inicial para la conversión romana
    mensaje_error_decimal = None
    mensaje_error_romano = None

    # Para la conversión Decimal a Romano
    if request.method == 'POST':
        decimal = request.POST.get('decimal', '').strip()
        romano = request.POST.get('romano', '').strip()

        if decimal:
            try:
                numero_decimal = int(decimal)
                if numero_decimal <= 0:
                    mensaje_error_decimal = "Por favor ingrese un número decimal mayor que 0."
                else:
                    resultado_romano = decimal_a_romano(numero_decimal)
            except ValueError:
                mensaje_error_decimal = "El valor ingresado no es un número decimal válido."

        if romano:
            if re.match('^[MDCLXVI]+$', romano.upper()):
                try:
                    resultado_decimal = romano_a_decimal(romano.upper())
                except KeyError:
                    mensaje_error_romano = "El número romano ingresado no es válido."
            else:
                mensaje_error_romano = "Por favor ingrese un número romano válido."

    return render(request, 'utilidades/conversor_numeros.html', {
        'resultado_decimal': resultado_decimal,
        'resultado_romano': resultado_romano,
        'mensaje_error_decimal': mensaje_error_decimal,
        'mensaje_error_romano': mensaje_error_romano,
    })
