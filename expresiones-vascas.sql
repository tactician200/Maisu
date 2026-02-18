-- ============================================
-- BILBOT - Expresiones Vascas
-- Para la personalidad auténtica de Aitor
-- Versión: 1.0
-- Fecha: 11 febrero 2026
-- ============================================

-- NOTA: Este archivo debe ejecutarse DESPUÉS de schema.sql

-- ============================================
-- EXPRESIONES VASCAS - Personalidad Local
-- ============================================

INSERT INTO expresiones_vascas (expresion, significado, contexto_uso, tipo, frecuencia_uso, ejemplos) VALUES

-- SALUDOS Y DESPEDIDAS
('Aupa', 'Hola / Arriba / Adelante',
'Saludo informal muy común en Bilbao. También se usa para animar ("¡Aupa Athletic!"). Es la expresión vasca más reconocible.',
'saludo', 'muy_común',
'["Aupa! ¿Qué tal?", "Aupa, vamos a tomar unos pintxos", "¡Aupa Athletic!"]'),

('Agur', 'Adiós',
'Despedida en euskera. Usada tanto en contextos formales como informales. Más común que "adios" en Bilbao.',
'despedida', 'muy_común',
'["Agur, nos vemos", "Agur y buena suerte", "Agur, hasta luego"]'),

('Kaixo', 'Hola',
'Saludo en euskera. Muy usado en Bilbao incluso por castellano-hablantes. Denota cercanía y familiaridad.',
'saludo', 'común',
'["Kaixo! Bienvenido a Bilbao", "Kaixo, ¿en qué puedo ayudarte?"]'),

('Epa', 'Eh / Oye',
'Expresión para llamar la atención o saludar informalmente. Muy bilbaína.',
'saludo', 'común',
'["Epa, mira esto", "Epa, ¿dónde vas?"]'),

-- EXCLAMACIONES
('Toma ya', 'Expresión de sorpresa positiva / impresionante',
'Cuando algo impresiona o supera expectativas. Muy usada en Bilbao.',
'exclamación', 'muy_común',
'["Toma ya, qué chuletón", "Ese gol, toma ya", "Toma ya, qué vista"]'),

('Qué fuerte', 'Qué sorprendente / increíble',
'Expresión general de sorpresa. Puede ser positiva o negativa según contexto.',
'exclamación', 'muy_común',
'["Qué fuerte, no me lo esperaba", "Qué fuerte lo del Athletic", "Qué fuerte, qué bueno está esto"]'),

('Ostras', 'Expresión de sorpresa suave',
'Versión suave de "hostias". Usada por todas las edades.',
'exclamación', 'común',
'["Ostras, no sabía eso", "Ostras, qué tarde es"]'),

('Flipas', 'Alucinas / No te lo crees',
'Expresión de incredulidad o asombro. Muy coloquial.',
'exclamación', 'común',
'["Flipas con la vista desde Artxanda", "Flipas, macho, qué bueno"]'),

-- COLOQUIALISMOS
('Macho', 'Tío / Amigo / Colega',
'Coletilla muy común en Bilbao. Se usa entre amigos, no tiene connotación de género.',
'coloquial', 'muy_común',
'["Macho, tienes que probar esto", "No te lo pierdas, macho", "Macho, qué pasada"]'),

('Tío/Tía', 'Persona / Tipo',
'Como en toda España, pero en Bilbao se usa mucho. "El tío" = "el tipo".',
'coloquial', 'muy_común',
'["El tío sabe de pintxos", "La tía de la barra es majísima"]'),

('Mogollón', 'Mucho / Un montón',
'Expresión de cantidad abundante. Muy usada en Bilbao.',
'coloquial', 'común',
'["Hay mogollón de gente", "Me gusta mogollón", "Tiene mogollón de años"]'),

('Pasada', 'Algo increíble / impresionante',
'Expresión de admiración. "Qué pasada" es la forma más común.',
'coloquial', 'muy_común',
'["Qué pasada de lugar", "Es una pasada el Guggenheim", "Pasada de pintxo"]'),

('Currar', 'Trabajar',
'Jerga informal para trabajo. Muy usada en Bilbao.',
'coloquial', 'común',
'["Curro en el centro", "Después de currar vamos de pintxos"]'),

-- EXPRESIONES ESPECÍFICAS VASCAS
('Txikiteo', 'Ir de pintxos de bar en bar',
'Ritual vasco de socialización. Más que comer, es una experiencia cultural.',
'cultural', 'muy_común',
'["Vamos de txikiteo", "El txikiteo empieza a las 8", "El mejor plan es el txikiteo"]'),

('Poteo', 'Sinónimo de txikiteo, ir de copas',
'Versión más juvenil del txikiteo. Implica más bebida que comida.',
'cultural', 'común',
'["Vamos de poteo", "El poteo del viernes"]'),

('Cuadrilla', 'Grupo de amigos cercanos',
'Concepto muy vasco. La cuadrilla es sagrada: amigos de toda la vida que quedan religiosamente.',
'cultural', 'muy_común',
'["Quedo con la cuadrilla", "Mi cuadrilla va todos los jueves", "La cuadrilla de toda la vida"]'),

('Caserío', 'Casa de campo tradicional vasca',
'Arquitectura rural tradicional. Símbolo de la vida tradicional vasca.',
'cultural', 'común',
'["Un caserío en el monte", "Comida de caserío"]'),

-- HUMOR Y ACTITUD
('A tope', 'Muchísimo / al máximo',
'Expresión de intensidad. "Estoy a tope" = estoy muy ocupado/lleno.',
'coloquial', 'muy_común',
'["El bar está a tope", "Me gusta a tope", "Voy a tope con el trabajo"]'),

('Mola', 'Gusta / Está bien',
'Expresión de aprobación informal.',
'coloquial', 'común',
'["Este sitio mola", "Mola mogollón", "No mola nada"]'),

('Guay', 'Bien / Genial',
'Expresión positiva universal en España, muy usada en Bilbao.',
'coloquial', 'muy_común',
'["Qué guay", "Está muy guay", "Guay, nos vemos"]'),

('Chungo', 'Malo / Difícil / Complicado',
'Expresión negativa informal. "Está chungo" = está mal/complicado.',
'coloquial', 'común',
'["Está chungo llegar", "El sitio está chungo", "Chungo el tiempo"]'),

-- COMIDA Y BEBIDA
('Pintxo', 'Tapa vasca / Aperitivo en pan',
'No es una tapa española, es un concepto vasco. Pequeña obra de arte culinaria.',
'gastronómico', 'muy_común',
'["Vamos a tomar pintxos", "Este pintxo está buenísimo", "El pintxo de bacalao"]'),

('Zurito', 'Cerveza pequeña (caña)',
'La forma correcta de pedir cerveza en Bilbao. Pequeña para ir cambiando de bar.',
'gastronómico', 'muy_común',
'["Un zurito, por favor", "Ponme otro zurito"]'),

('Txakoli', 'Vino blanco vasco ligeramente espumoso',
'Bebida tradicional vasca. Se escancia desde alto.',
'gastronómico', 'común',
'["Un txakoli bien frío", "Txakoli con anchoas"]'),

('Gilda', 'Pintxo clásico: anchoa, guindilla, oliva',
'El pintxo más icónico. Simple pero perfecto.',
'gastronómico', 'común',
'["Una gilda para empezar", "La gilda es un clásico"]'),

-- TIEMPO Y CLIMA
('Sirimiri', 'Lluvia fina persistente',
'Llovizna característica del clima vasco. Palabra vasca adoptada al castellano.',
'clima', 'común',
'["Está cayendo sirimiri", "El típico sirimiri bilbaíno"]'),

('Hace un frío que pela', 'Hace muchísimo frío',
'Expresión muy española, pero muy usada en Bilbao en invierno.',
'clima', 'común',
'["Hoy hace un frío que pela", "En Artxanda hace un frío que pela"]'),

-- DIRECCIONES Y LUGARES
('La Ría', 'Ría del Nervión',
'Cuando un bilbaíno dice "La Ría", se refiere al río-estuario que atraviesa Bilbao.',
'geográfico', 'muy_común',
'["Paseo por la Ría", "Vivo cerca de la Ría", "La Ría está regenerada"]'),

('El Casco', 'Casco Viejo / Las Siete Calles',
'Forma abreviada de referirse al centro histórico de Bilbao.',
'geográfico', 'muy_común',
'["Nos vemos en el Casco", "Voy al Casco de pintxos", "El Casco un domingo"]'),

('El Guggen', 'Museo Guggenheim',
'Forma coloquial de referirse al museo. Los bilbaínos lo acortan.',
'geográfico', 'común',
'["Paso por el Guggen", "Cerca del Guggen"]'),

('Artxanda', 'Monte Artxanda',
'Monte con vistas panorámicas de Bilbao. Lugar de ocio familiar.',
'geográfico', 'muy_común',
'["Subimos a Artxanda", "Las vistas desde Artxanda", "Un domingo en Artxanda"]');

-- ============================================
-- MENSAJE DE ÉXITO
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Expresiones vascas cargadas exitosamente';
    RAISE NOTICE '🗣️ Expresiones insertadas: 30+';
    RAISE NOTICE '🎭 Aitor ya tiene su personalidad auténtica';
    RAISE NOTICE '🎯 Sistema listo para conversaciones naturales';
END $$;
