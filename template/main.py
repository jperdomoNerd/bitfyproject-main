# -*- coding: utf-8 -*-
"""
Created on Sun May  7 11:37:31 2023

@author: SANTI
"""

from docxtpl import DocxTemplate

doc = DocxTemplate("Plantilla.docx")
topItems = ['Item 6', 'Item 2', 'Item 10']

Accionante = 'YANETH BAUTISTA FERNANDEZ'
Accionado = 'COOMEVA E.P.S.'
Asunto = 'Amparo integral del derecho a la salud, servicio de Home Care, pañales, servicio de enfermería 24 horas, cama hospitalaria, Almipro, crema Lubriderm.'
Presentacion = 'YANETH BAUTISTA FERNANDEZ, ciudadana en ejercicio identificada como aparece al pie de la firma, residente en la ciudad de Cali, actuando a nombre propio y también como agente oficiosa de mi señora madre MARIANITA FERNANDEZ DE BAUTISTA, identificada con la cédula de ciudadanía No. 25.378.323, en ejercicio del artículo 86 Superior y con el lleno de los requisitos del Decreto 2591 de 1991; interpongo ACCIÓN DE TUTELA contra COOMEVA E.P.S. por los siguientes'
Hechos = ['Mi señora madre, MARIANITA FERNANDEZ DE BAUTISTA (afiliada a COOMEVA E.P.S.), debido a su avanzada edad (75 años), se encuentra postrada en cama y se encuentra afectada por múltiples enfermedades que le imposibilitan valerse por sí misma, requiriendo el cuidado permanente de alguien las 24 horas del día. Mi señora madre, además, no controla esfínteres (consta en la historia clínica anexada) y tiene demencia senil tipo Alzheimer. ', 
          'Mediante orden médica del 2 de febrero de 2018 formulada por el médico tratante José Rocha, se determinó que mi señora madre debe tener servicio de Home Care; sin embargo la E.P.S. se negó a la autorización de dicho servicio.', 
          '''Debido a su Difícil estado de salud, a que ella no puede valerse por sí misma (absolutamente todo hay que hacerlo por ella) y debido además a que no controla sus esfínteres: es absolutamente necesario para salvaguardar sus derechos a la salud y a la vida digna que la E.P.S. accionada autorice (a pesar de que no existe orden médica sobre ello) lo siguiente:
-120 Pañales mensuales (se le cambia el pañal 4 veces al día).
-Cama Hospitalaria (es bastante difícil manejarla por su peso y su imposibilidad levantarse voluntariamente y por ello requiere de esto).
-Servicio de enfermería 12 horas (esto lo requiere mi madre porque en este momento no hay quién esté pendiente de ella permanentemente y yo me veo obligada a trabajar para sostener a mi familia y a mí misma por lo que no puedo estar todo el día a su cuidado: siempre tiene que existir una persona a su lado que le suministre sus medicamentos, que la asee y le de comer. Requiere de cuidados especiales. En mi caso, tengo que cumplir con un horario de trabajo extenso para sostener a mi hijo de 15 años y no podría pagarle a una persona para que esté permanentemente al cuidado de mi madre porque es bastante costoso).
''']
Derechos  = ['Derechos a la salud y a la vida digna, a mi señora madre.',
             'Derecho al mínimo vital, a mí y a mi familia (porque se me obliga a dejar de trabajar para poder cuidar a mi madre).']
Pretenciones  = ['AUTORICE Y SUMINISTRE SERVICIO DE HOMECARE (existe orden médica para esto que ya fue negada).',
                 'AUTORICE Y SUMINISTRE 120 PAÑALES MENSUALES (requiere 4 diarios).',
                 'AUTORICE Y SUMINISTRE UNA CAMA HOSPITALARIA TRES NIVELES PARA ELLA (la requiere urgentemente porque está postrada en cama y es muy difícil moverla).',
                 'AUTORICE Y SUMINISTRE EL SERVICIO DE ENFERMERÍA DOMICILIARIA 12 HORAS (lo requiere porque soy la única persona responsable de su cuidado en este momento y por cuestiones de trabajo no hay nadie que pueda cuidarla permanentemente como se debe. Solamente lo puedo hacer en las noches cuando no estoy en horario laboral y por eso lo solicito por 12 horas).',
                 'UN TARRO MENSUAL DE CREMA ALMIPRO (la requiere para prevenir la pañalitis).',
                 'UN TARRO DE CREMA LUBRIDERM (para que su piel no se reseque).',
                 'Solicito respetuosamente que se ORDENE a la accionada el TRATAMIENTO INTEGRAL de mi señora madre debido a que es una persona de la tercera edad y por tanto sujeto de especial protección constitucional. De esa manera, la EPS deberá autorizar inmediatamente sin dilaciones, negaciones ni restricciones, todo lo que los galenos ordenen para el tratamiento de sus padecimientos, según lo dispuesto en la jurisprudencia de la Corte Constitucional sobre el principio de integralidad en salud. ',
                 ]
Fundamentos  = '''Sentencia No. T- 154 de 2014, Honorable Corte Constitucional, sobre el deber de las E.P.S. de suministrar pañales y otros insumos así no exista formulación médica: 

Ahora bien, este tribunal ha abordado en distintas ocasiones el tema de los insumos que se necesitan para el manejo de personas que padecen pérdida del control de esfínteres (como por ejemplo el uso de pañales desechables), los cuales, a pesar de estar excluidos del POS , constituyen parte del manejo indispensable que a estos pacientes se le debe brindar para garantizarles una vida en condiciones dignas. De esta forma, la Corte ha establecido que para determinar si hay o no lugar al suministro de estos elementos, se debe verificar el cumplimientos (sic) de dichos requisitos.   
 
Sin embargo, también se ha sostenido que en los casos en los que no exista fórmula del médico tratante que prescriba su uso, habrá lugar a ordenar su suministro cuando sea posible deducir que “existe una relación directa entre la dolencia, es decir la pérdida de control de esfínteres y lo pedido, es decir que se puede inferir razonablemente que una persona que padece esta situación requiere para llevar una vida en condiciones dignas los pañales desechables” . Dicho de otro modo, “se trata de que las circunstancias fácticas y médicas permitan concluir forzosamente que, en realidad, el afectado necesita de la provisión de los componentes solicitados ”. A la anterior conclusión se podrá allegar bien sea por lo que consta en la historia clínica del paciente, o por sus propias condiciones .
'''
Anexos   = ['Fotocopias de cédulas de ciudadanía de mi señora madre y la mía.',
            'Fotocopia de historia clínica de mi señora madre.',
            'Fotocopia de orden médica de servicio de Home Care (negada por la E.P.S.)',
            'Fotocopia de registro civil de mi hijo (con el fin de probar que me veo obligada a trabajar para sostenerlo a él económicamente).',
            'Fotocopia de Carta Laboral del establecimiento donde trabajo (con el fin de probar que trabajo todo el día y se me hace difícil cuidar a mi madre permanentemente).']
Notificacion  = '''Las recibiré en la Calle 59A # 3 Bis- 76, barrio Villa del Prado de la ciudad de Cali, teléfono 313 767 8137. También autorizo ser notificada al correo electrónico carlosrojas9506@gmail.com

A la accionada en la CALLE 5A #38D-153 de la ciudad de Cali y al teléfono (2) 5110000.'''
#Presentacion = '8'
TipoDoc  = 'C.C.'
NumeroDoc  = '66.757.602'

context = { 'Accionante' : Accionante, 'Accionado' : Accionado, 'Asunto': Asunto, 'Presentacion':Presentacion,
           'Hechos':Hechos, 'Derechos':Derechos, 'Pretenciones':Pretenciones, 'Fundamentos':Fundamentos,  
           'Anexos':Anexos, 'Notificacion':Notificacion, 'TipoDoc':TipoDoc, 'NumeroDoc':NumeroDoc}
doc.render(context)
doc.save("generated_doc.docx")

