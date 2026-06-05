# Diccionario de Datos Proyecto Osteoporosis

## Variables Sociodemográficas

| Nombre de variable | Descripción | Tipo de variable | Codificación / Categorías |
| :--- | :--- | :--- | :--- |
| 1. Sexo | Sexo autopercibido del participante | Cualitativa dicotómica | 1 = Mujer, 0 = Hombre |
| 2. ECivil | Estado civil | Cualitativa dicotómica | 1 = Con pareja, 0 = Sin pareja |
| 3. Edad | Edad en años cumplidos | Cuantitativa continua | Valor numérico |
| 4. Edad_cat | Edad en grupos etarios | Cualitativa ordinal | 1 = 50–59 años, 2 = 60–69 años, 3 = 70 y más |
| 5. Lnac (Entidad) | Entidad federativa de nacimiento | Cualitativa nominal | Nombre del estado |
| 6. Lnac (Municipio) | Municipio de nacimiento | Cualitativa nominal | Nombre del municipio |
| 7. Lresid (Entidad): | Entidad federativa de residencia actual | Cualitativa nominal | Nombre del estado |
| 8. Lresid (Municipio): | Municipio de residencia actual | Cualitativa dicotómica | 1 = Zona Metropolitana de Guadalajara (ZMG), 0 = Municipios de Jalisco |

## Condiciones materiales de la vida

| Nombre de variable | Descripción | Tipo de variable | Codificación / Categorías |
| :--- | :--- | :--- | :--- |
| 9. Escolaridad | Nivel educativo alcanzado | Cualitativa dicotómica | 1 = Con estudios, 0 = Sin estudios |
| 10. Trabaja | Tiene trabajo actualmente | Cualitativa dicotómica | 0 = No, 1 = Sí |
| 11. Tipo_empleo | Tipo de empleo | Cualitativa politómica nominal | 0 = Sin empleo, 1 = Empleo formal, 2 = Empleo informal |
| 12. Act_empleo | Intensidad de la ocupación reportada | Cualitativa ordinal | 0 = Sin empleo, 1 = Ligeras, 2 = Moderadas, 3 = Intensas |
| 13. Ing_mensual | Rango de ingreso mensual declarado | Cualitativa ordinal | Ej. '0 a 4,999', '5,000 a 7,499' |
| 14. Ing_mensual_cat | Nivel de ingreso mensual categorizado | Cualitativa ordinal | 0 = Sin información, 1 = Bajo, 2 = Medio, 3 = Alto |

## Sistema Sanitario

| Nombre de variable | Descripción | Tipo de variable | Codificación / Categorías |
| :--- | :--- | :--- | :--- |
| 15. Derechohabiente | Institución donde reporta estar afiliado | Cualitativa nominal | IMSS, ISSSTE, SSA/INSABI, Centro de salud, Ninguno |
| 16. Derechohabiente_Cat | Tipo de institución de afiliación | Cualitativa dicotómica | 1 = Con cobertura, 0 = Sin cobertura |
| 17. Salud_Cobertura | Combinación de instituciones de acceso | Cualitativa nominal | Ej. IMSS, SSA/INSABI, Privado |
| 18. Salud_Cobertura_cat | Clasificación de tipo de cobertura en salud | Cualitativa politómica | 1 = Seguridad Social, 2 = Servicios Públicos, 3 = Privado, 4 = Sin cobertura |
| 19. Enfermedad | Enfermedades crónicas reportadas | Cualitativa nominal | Texto libre |
| 20. Enfermedad(cod) | Clasificación general de la enfermedad | Cualitativa politómica | 1=Metabólicos, 2=Cardiovasculares, 3=Osteoarticulares, 4=Autoinmunes, 5=Endocrinas, 6=Neuro/Psiq, 7=Infecciosas, 8=Sano, 9=Otras |
| 21. Enf_cat | Clasificación reducida de la enfermedad | Cualitativa politómica | 0=Sano, 1=Síndrome metabólico, 2=Otras enfermedades |
| 22. Tiempo Dx | Tiempo transcurrido desde el diagnóstico | Cualitativa ordinal | 1=<1 año, 2=1-5 años, 3=5-10 años, 4=+10 años, 5=No aplica |

## Cohesión Social

| Nombre de variable | Descripción | Tipo de variable | Codificación / Categorías |
| :--- | :--- | :--- | :--- |
| 23. Vive_Con | Personas con quienes vive el participante | Cualitativa nominal | Texto libre |
| 24. Vive_Con_cat | Clasificación del tipo de convivencia | Cualitativa dicotómica | 0 = Vive solo, 1 = Acompañado |
| 25. Ayuda_Enf | Quién brinda apoyo para el manejo de la enfermedad | Cualitativa nominal | Texto libre |
| 26. Ayuda_Enf_cat | Clasificación del tipo de apoyo recibido | Cualitativa dicotómica | 0 = Autocuidado, 1 = Tiene apoyo |
| 27. Disp_Aprendizaje | Disposición a aprender sobre su enfermedad | Cualitativa dicotómica | 1=Sí, 0=No, 2=No aplica |
| 28. Disp_Capacitación | Disposición a recibir capacitación | Cualitativa politómica | 2=Sí, 0=No, 2=No aplica |
| 29. Motivo_No_Conocer | Razón por la que no conoce su diagnóstico | Cualitativa politómica | 1=Falta de interés, 2=Limitación física, 3=No aplica, 4=Trabaja, 5=Vive en otro lugar |
| 30. Grupo_Externo_Enf | Participa en grupo comunitario o externo | Cualitativa dicotómica | 0=No, 1=Sí |
| 31. Tipo_Grupo_Apoyo | Tipo de grupo al que pertenece | Cualitativa politómica | 0=Ninguno, 1=GAM, 2=Sector Público, 3=Privado/ONG |

## Estilos de Vida - Actividad Física

| Nombre de variable | Descripción | Tipo de variable | Codificación / Categorías |
| :--- | :--- | :--- | :--- |
| 32. Realiza_AF | Realiza actividad física actualmente | Cualitativa dicotómica | 0=No, 1=Sí |
| 33. Tipo_AF | Tipo principal de actividad física | Cualitativa politómica | 0=Ninguna, 1=Resistencia, 2=Flexibilidad, 3=Fuerza |
| 34. Frecuencia_AF | Frecuencia semanal de actividad física | Cualitativa ordinal | 0=No aplica, 1=1 vez, 2=2-3 veces, 3=4-5 veces, 4=6+ veces |
| 35. Tiempo_AF | Duración por sesión | Cualitativa ordinal | 0=No aplica, 1=15–30min, 2=30–60min, 3=1–1.5h, 4=2+h |
| 36. Espacio_AF | Tiene espacio adecuado | Cualitativa dicotómica | 0=No, 1=Sí |

## Estilos de Vida - Nutrición

| Nombre de variable | Descripción | Tipo de variable | Codificación / Categorías |
| :--- | :--- | :--- | :--- |
| 37. Plan_Alimenticio | Tiene un plan alimenticio definido | Cualitativa dicotómica | 0=No, 1=Sí |
| 38. Autor_Dieta | Quién creó o dirige su dieta | Cualitativa politómica | 0=No, 1=Geriatra, 2=Médico, 3=Nutriólogo, 4=Yo mismo/otros |
| 39. Factores_favorables_dieta | Factores que favorecen su dieta | Cualitativa nominal | Texto libre |
| 40. Barreras_dieta | Barreras percibidas para seguir dieta | Cualitativa nominal | Texto libre |

## Diagnóstico de Salud Ósea

| Nombre de variable | Descripción | Tipo de variable | Codificación / Categorías |
| :--- | :--- | :--- | :--- |
| 41. Dx_Óseo | Diagnóstico clínico de salud ósea | Cualitativa nominal | Normal, Osteopenia, Osteoporosis |
| 42. Dx_Óseo_cat | Diagnóstico óseo binario | Cualitativa dicotómica | 0=Normal, 1=Osteopenia/Osteoporosis |
| 43. Peso (kg) | Peso corporal del participante | Cuantitativa continua | Valor en kilogramos |
| 44. Altura (cm) | Estatura del participante | Cuantitativa continua | Valor en centímetros |
| 45. IMC | Índice de Masa Corporal | Cuantitativa continua | Valor decimal (peso/talla²) |
| 46. IMC_Cat | Clasificación del estado nutricional | Cualitativa ordinal | 1=Normal, 2=Sobrepeso, 3=Obesidad |