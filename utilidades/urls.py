from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_principal, name='pagina_principal'),  # Página principal

    path('contador-fechas/', views.contador_fechas, name='contador_fechas'),
    path('calculadora-edad/', views.calculadora_edad, name='calculadora_edad'),

    path('generador-curp/', views.generador_curp, name='generador_curp'),
    path('generador-rfc/', views.generador_rfc, name='generador_rfc'),
    path('generador-nombres/', views.generador_nombres, name='generador_nombres'),


    path('contador_palabras/', views.contador_palabras, name='contador_palabras'),
    path('corrector_ortografico/', views.corrector_ortografico, name='corrector_ortografico'),
    path('generador_palabras_clave/', views.generador_palabras_clave, name='generador_palabras_clave'),

     path('generador_qr/', views.generador_qr, name='generador_qr'),
    path('minificador_css_js/', views.minificador_css_js, name='minificador_css_js'),
    path('generador_contrasenas/', views.generador_contrasenas, name='generador_contrasenas'),
    path('validador_json_xml/', views.validador_json_xml, name='validador_json_xml'),


        # URLs para los conversores
    path('conversor-divisas/', views.conversor_divisas, name='conversor_divisas'),
    path('conversor-unidades/', views.conversor_unidades, name='conversor_unidades'),
    path('conversor-formatos/', views.conversor_formatos, name='conversor_formatos'),
]
