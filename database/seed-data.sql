-- ============================================
-- BILBOT - Datos Iniciales (Seed Data)
-- Lugares reales de Bilbao curados localmente
-- Versión: 1.0
-- Fecha: 11 febrero 2026
-- ============================================

-- NOTA: Este archivo debe ejecutarse DESPUÉS de schema.sql
-- Los embeddings se generarán mediante el workflow de n8n

-- ============================================
-- LUGARES - Restaurantes, Bares, Cafés, Museos
-- ============================================

INSERT INTO places (nombre, tipo, descripcion, descripcion_corta, barrio, direccion, precio_medio, rango_precio, valoracion_local, tags, por_que_es_especial, historia_breve, es_trampa_turistica, recomendado_por_locales, website, acepta_reservas, verified) VALUES

-- BARES Y PINTXOS
('Gure Toki', 'bar',
'Bar de pintxos tradicional vasco en el corazón del Casco Viejo. Frecuentado por bilbaínos que buscan calidad y autenticidad. Los pintxos se preparan al momento con ingredientes frescos del mercado. Ambiente auténtico sin pretensiones turísticas.',
'Bar de pintxos auténtico frecuentado por locales',
'Casco Viejo', 'Plaza Nueva, 12, 48005 Bilbao',
12.00, '€', 4.80,
ARRAY['pintxos', 'auténtico', 'local', 'mercado', 'casero'],
'Los bilbaínos vienen aquí porque los pintxos son caseros y el ambiente es 100% local. No encontrarás grupos de turistas con selfie-sticks.',
'Fundado en los años 80, ha mantenido su filosofía de producto fresco y precios justos para los vecinos del barrio.',
false, true, 'http://guretoki.com', false, true),

('Café Bar Bilbao', 'bar',
'Clásico bar de pintxos en la Plaza Nueva. Famoso por su tortilla de patata y el bacalao al pil-pil. Los domingos se llena de familias bilbaínas después del vermut.',
'Tortilla legendaria y ambiente de domingo en la Plaza Nueva',
'Casco Viejo', 'Plaza Nueva, 6, 48005 Bilbao',
15.00, '€', 4.70,
ARRAY['pintxos', 'tortilla', 'plaza', 'vermut', 'clásico'],
'La tortilla de patata es probablemente la mejor de Bilbao. Jugosa, con punto de cebolla, y servida caliente.',
'Desde 1911 en el mismo local. Ha sobrevivido a guerras, crisis y modas gastronómicas sin cambiar su esencia.',
false, true, null, false, true),

('Txakoli Simon', 'bar',
'Sidrería y bar especializado en txakoli (vino blanco vasco). Perfecto para probar el ritual de "mojar pan" con anchoas del Cantábrico.',
'Txakoli auténtico y anchoas del Cantábrico',
'Bilbao La Vieja', 'Calle Dos de Mayo, 4, 48001 Bilbao',
10.00, '€', 4.60,
ARRAY['txakoli', 'anchoas', 'auténtico', 'vino', 'tradicional'],
'El txakoli se sirve de la barrica directamente. El ritual de escanciado alto es todo un espectáculo.',
'Bar familiar de tercera generación. El abuelo Simon empezó vendiendo txakoli de su caserío.',
false, true, null, false, true),

-- CAFÉS
('Café Iruña', 'café',
'Café histórico modernista fundado en 1903. Los frescos y azulejos originales transportan a la época de la burguesía industrial bilbaína. Hemingway lo menciona en "Fiesta" (The Sun Also Rises). Ambiente elegante pero accesible.',
'Café modernista histórico con frescos de 1903',
'Ensanche', 'Jardines de Albia, 48001 Bilbao',
15.00, '€€', 4.50,
ARRAY['histórico', 'modernista', 'desayuno', 'terraza', 'Hemingway'],
'Los frescos del techo son originales del 1903. Es como tomar café en un museo viviente del modernismo vasco.',
'Inaugurado en 1903, fue el punto de encuentro de la burguesía bilbaína. Ernest Hemingway lo frecuentó en los años 20.',
false, true, 'http://www.cafeiruna.com', false, true),

('Federal Café', 'café',
'Café de especialidad australiano. Tostado propio, métodos alternativos (V60, Chemex, Aeropress). Brunch de fin de semana muy popular entre jóvenes profesionales y extranjeros residentes.',
'Café de especialidad con tostado propio',
'Indautxu', 'Calle Fueros, 6, 48930 Bilbao',
8.00, '€', 4.40,
ARRAY['café especialidad', 'brunch', 'moderno', 'extranjeros'],
'El mejor flat white de Bilbao según los australianos que viven aquí. Tostado local de máxima calidad.',
'Abierto en 2016 por un australiano y un bilbaíno. Pioneros del movimiento de café de especialidad en Bilbao.',
false, false, 'http://federalcafe.es', true, true),

-- RESTAURANTES
('Restaurante Mina', 'restaurante',
'Dos estrellas Michelin. Chef Álvaro Garrido. Cocina vasca moderna con técnica impecable y producto local de temporada. Menú degustación 20 pasos. Experiencia gastronómica de alto nivel sin pretensiones.',
'Dos estrellas Michelin, cocina vasca contemporánea',
'Bilbao La Vieja', 'Muelle Marzana, 48003 Bilbao',
150.00, '€€€', 4.90,
ARRAY['michelin', 'alta cocina', 'degustación', 'producto local'],
'Dos estrellas Michelin bien merecidas. Álvaro Garrido es un maestro de la cocina vasca moderna sin artificios.',
'Abrió en 2014 y ganó su primera estrella Michelin en 2016. Segunda estrella en 2018. Ahora es referencia en Euskadi.',
false, false, 'http://restaurantemina.es', true, true),

('Etxanobe', 'restaurante',
'Una estrella Michelin con vistas panorámicas al Guggenheim. Chef Fernando Canales. Cocina vasca moderna con toques creativos. Menú ejecutivo de mediodía excelente relación calidad-precio.',
'Estrella Michelin con vistas al Guggenheim',
'Ensanche', 'Juan de Ajuriaguerra, 8, 48009 Bilbao',
85.00, '€€€', 4.60,
ARRAY['michelin', 'vistas', 'cocina moderna', 'producto'],
'Las vistas desde el comedor son espectaculares: Guggenheim, Ría y montes. Y la cocina está a la altura del escenario.',
'Fernando Canales ganó su estrella Michelin en 2007. Desde entonces mantiene nivel constante.',
false, false, 'http://etxanobe.com', true, true),

('Restaurante Zortziko', 'restaurante',
'Cocina vasca tradicional evolucionada. Chef Daniel García. Ubicado en un palacete del siglo XIX. Bodega con más de 600 referencias. Ambiente elegante pero cálido.',
'Cocina vasca evolucionada en palacete histórico',
'Abando', 'Alameda Mazarredo, 17, 48001 Bilbao',
70.00, '€€€', 4.50,
ARRAY['tradicional', 'bodega', 'palacete', 'elegante'],
'La bodega es impresionante. Más de 600 vinos, muchos de ellos de bodegas pequeñas vascas difíciles de encontrar.',
'El edificio es un palacete de 1891. El restaurante abrió en 1989 y ha mantenido su esencia.',
false, false, 'http://zortziko.es', true, true),

('La Viña del Ensanche', 'restaurante',
'Asador clásico bilbaíno. Chuletón de buey al carbón, alubias de Tolosa, bacalao al pil-pil. Sin pretensiones, producto de calidad y punto de la brasa perfecto.',
'Asador clásico con chuletón legendario',
'Ensanche', 'Diputación, 10, 48008 Bilbao',
45.00, '€€', 4.70,
ARRAY['asador', 'chuletón', 'tradicional', 'carne'],
'El chuletón viene de ganaderías vascas seleccionadas. Maduración de 45 días y brasa de carbón.',
'Abierto desde 1997. Tres generaciones de familia en el mundo de la carne.',
false, true, 'http://lavinadelensanche.com', true, true),

-- MUSEOS Y CULTURA
('Guggenheim Bilbao', 'museo',
'Museo de arte contemporáneo diseñado por Frank Gehry. Símbolo de la regeneración urbana de Bilbao. Colección permanente de arte moderno y exposiciones temporales de nivel mundial. La arquitectura en sí es una obra de arte.',
'Museo icónico de Frank Gehry, arte contemporáneo',
'Abandoibarra', 'Avenida Abandoibarra, 2, 48009 Bilbao',
16.00, '€€', 4.70,
ARRAY['arte', 'arquitectura', 'imprescindible', 'icónico'],
'La arquitectura de titanio de Frank Gehry es tan impresionante como la colección interior. Cambió la historia de Bilbao.',
'Inaugurado en 1997. Su impacto económico y cultural en Bilbao se conoce como "Efecto Guggenheim".',
false, false, 'http://guggenheim-bilbao.eus', false, true),

('Museo de Bellas Artes', 'museo',
'Segunda pinacoteca de España después del Prado. Colección desde el siglo XII hasta arte contemporáneo. Obras de El Greco, Zurbarán, Goya, Gauguin, Francis Bacon. Menos turístico que el Guggenheim pero igual de impresionante.',
'Segunda pinacoteca de España, arte clásico y moderno',
'Abandoibarra', 'Plaza Museo, 2, 48009 Bilbao',
10.00, '€', 4.80,
ARRAY['arte', 'clásico', 'pintura', 'historia'],
'Los bilbaínos vienen aquí más que al Guggenheim. Colección permanente extraordinaria y sin aglomeraciones turísticas.',
'Fundado en 1908. Fusionó el antiguo Museo de Bellas Artes y el Museo de Arte Moderno.',
false, true, 'http://museobilbao.com', false, true),

('Museo Vasco', 'museo',
'Museo etnográfico sobre cultura e historia vasca. Ubicado en un claustro jesuita del siglo XVII. Colección de arte popular, herramientas tradicionales, navegación, y la vida en el caserío vasco.',
'Etnografía y cultura vasca en claustro histórico',
'Casco Viejo', 'Plaza Miguel de Unamuno, 4, 48006 Bilbao',
3.00, '€', 4.40,
ARRAY['historia', 'cultura vasca', 'etnografía', 'tradicional'],
'Para entender la cultura vasca auténtica sin clichés. El claustro del siglo XVII es una joya arquitectónica.',
'Fundado en 1921. El edificio es un antiguo colegio jesuita del siglo XVII.',
false, true, 'http://euskal-museoa.eus', false, true),

-- MERCADOS
('Mercado de la Ribera', 'mercado',
'Mercado municipal art decó sobre la Ría. El más grande de Europa cuando se inauguró en 1929. Producto fresco local: pescado del Cantábrico, verduras de huertas vascas, carnes de ganaderías locales. Hay bares de pintxos en la planta superior.',
'Mercado art decó, el más grande de Europa en su época',
'Casco Viejo', 'Ribera Kalea, 22, 48005 Bilbao',
20.00, '€', 4.60,
ARRAY['mercado', 'producto local', 'art decó', 'pescado'],
'Los chefs de los mejores restaurantes de Bilbao compran aquí. Pescado del Cantábrico de la lonja de Bermeo.',
'Inaugurado en 1929. Edificio art decó sobre la Ría. Fue el mercado cubierto más grande de Europa.',
false, true, 'http://mercadodelaribera.biz', false, true),

-- CASCO VIEJO - LAS SIETE CALLES
('Las Siete Calles', 'zona',
'El casco medieval de Bilbao. Siete calles paralelas entre la Ribera y la Basilica de Begoña. Fundado en 1300. Corazón histórico con bares de pintxos, tiendas tradicionales y arquitectura medieval. Imprescindible para el txikiteo (ir de pintxos).',
'Casco medieval de Bilbao, corazón del txikiteo',
'Casco Viejo', 'Casco Viejo, 48005 Bilbao',
0.00, '€', 4.90,
ARRAY['histórico', 'medieval', 'pintxos', 'txikiteo', 'ambiente'],
'Aquí es donde los bilbaínos hacen el txikiteo de verdad. Cada calle tiene su personalidad y sus bares míticos.',
'Fundado en 1300 por Diego López de Haro. Las siete calles originales siguen intactas desde la época medieval.',
false, true, null, false, true),

-- OTROS LUGARES DE INTERÉS
('Puente Colgante de Vizcaya', 'monumento',
'Puente transbordador declarado Patrimonio de la Humanidad UNESCO. Construido en 1893 por Alberto Palacio (discípulo de Eiffel). Une Portugalete y Getxo. Se puede cruzar en la barquilla o subir a la pasarela superior.',
'Puente transbordador UNESCO de 1893',
'Getxo', 'Las Arenas, 48930 Getxo',
12.00, '€', 4.70,
ARRAY['unesco', 'arquitectura', 'industrial', 'historia'],
'Único puente transbordador en funcionamiento en España. La vista desde la pasarela superior es espectacular.',
'Diseñado por Alberto Palacio e inaugurado en 1893. Patrimonio de la Humanidad UNESCO desde 2006.',
false, true, 'http://puente-colgante.com', false, true),

('San Mamés', 'estadio',
'Estadio del Athletic Club. Conocido como "La Catedral". Capacidad 53.000 espectadores. Visitas guiadas al museo y al estadio. Experiencia imprescindible para entender la cultura deportiva vasca.',
'Estadio del Athletic Club, "La Catedral" del fútbol vasco',
'San Mamés', 'Rafael Moreno Pitxitxi, 48013 Bilbao',
15.00, '€', 4.80,
ARRAY['fútbol', 'deporte', 'cultura', 'Athletic', 'museo'],
'El Athletic Club solo ficha jugadores vascos o formados en Euskadi. Es el último bastión de la filosofía cantera.',
'El nuevo San Mamés se inauguró en 2013. Sustituyó al mítico viejo San Mamés, conocido como "La Catedral".',
false, true, 'http://athletic-club.eus', true, true),

('Playa de Sopelana', 'playa',
'Playa de arena fina con olas. Popular entre surfistas locales. Ambiente relajado, sin masificación turística. Atardecer espectacular sobre el Cantábrico. Varios chiringuitos con cerveza fría y rabas (calamares fritos).',
'Playa de surf con ambiente local',
'Sopelana', 'Sopelana, 48600 Bizkaia',
0.00, '€', 4.50,
ARRAY['playa', 'surf', 'naturaleza', 'atardecer'],
'Los surfistas bilbaínos vienen aquí. Ambiente auténtico de playa vasca, sin chiringuitos de reggaeton.',
'Tradición surfera desde los años 70. Varios campeones de España han aprendido a surfear en estas olas.',
false, true, null, false, true),

('Funicular de Artxanda', 'transporte',
'Funicular histórico que sube al monte Artxanda. Vistas panorámicas de 360° sobre Bilbao y la Ría. Arriba hay varios restaurantes, zonas de picnic y rutas de senderismo. Los bilbaínos suben los domingos en familia.',
'Funicular con vistas panorámicas de Bilbao',
'Zorroza', 'Plaza del Funicular, 48006 Bilbao',
3.00, '€', 4.60,
ARRAY['vistas', 'panorámica', 'histórico', 'naturaleza'],
'La mejor vista panorámica de Bilbao sin duda. Al atardecer es mágico. Los locales suben a tomar vermut los domingos.',
'Inaugurado en 1915. Sigue funcionando con la maquinaria original restaurada.',
false, true, 'http://funiculardearchanda.com', false, true),

('Azkuna Zentroa', 'centro cultural',
'Antiguo almacén de vino reconvertido en centro cultural por Philippe Starck. Cine, exposiciones, gimnasio, biblioteca, terraza. Arquitectura interior espectacular con columnas de estilos diferentes.',
'Centro cultural en almacén reconvertido por Starck',
'Ensanche', 'Plaza Arriquibar, 4, 48010 Bilbao',
0.00, '€', 4.40,
ARRAY['cultura', 'arquitectura', 'Starck', 'moderno'],
'Las 43 columnas diseñadas por diferentes artistas son una obra de arte. El espacio es impresionante.',
'Antiguo almacén municipal de vino (Alhóndiga) de 1909. Reconvertido por Philippe Starck en 2010.',
false, false, 'http://azkunazentroa.eus', false, true);

-- ============================================
-- HISTORIA VASCA - Artículos culturales
-- ============================================

INSERT INTO historia_vasca (tema, titulo, contenido, contenido_corto, epoca, categoria, tags, nivel_detalle, idioma) VALUES

('Athletic Club', 'Historia del Athletic Club de Bilbao',
'El Athletic Club, fundado en 1898 por estudiantes vascos y británicos, es uno de los tres clubes que nunca ha descendido de Primera División en España (junto al Real Madrid y FC Barcelona). Su filosofía cantera es única en el fútbol mundial: solo ficha jugadores vascos o formados en la cantera vasca.

El estadio San Mamés, conocido como "La Catedral", es un templo del fútbol donde los aficionados viven el deporte con pasión intensa. El rugido del estadio es legendario en Europa.

El Athletic ha ganado 8 Ligas, 24 Copas del Rey, y 2 Supercopas de España. Más allá de los títulos, representa la identidad vasca, la continuidad generacional y el arraigo local. Jugadores como Iribar, Zubizarreta, Guerrero, o Muniain son símbolos vivientes de esta filosofía.

La afición es incondicional. Incluso en épocas sin títulos, el estadio se llena. Es más que un club: es un sentimiento de pertenencia.',

'Club fundado en 1898 con filosofía única: solo jugadores vascos. San Mamés es "La Catedral" del fútbol vasco.',
'Siglo XX-XXI', 'deporte',
ARRAY['Athletic', 'fútbol', 'San Mamés', 'cantera', 'identidad'],
'detallado', 'es'),

('Industrialización', 'La Era Industrial de Bilbao',
'A finales del siglo XIX, Bilbao experimentó una transformación radical gracias a la minería del hierro y la industria naval. La Ría del Nervión se llenó de astilleros, altos hornos y fábricas.

Familias como los Ybarra, Echevarría, Martínez Rivas y Chávarri construyeron un imperio industrial que convertiría a Bilbao en la ciudad más rica de España. La exportación de hierro a Inglaterra financió el desarrollo urbano del Ensanche.

Los barrios obreros como Bilbao La Vieja y San Francisco crecieron de forma caótica. La inmigración de otras regiones de España cambió la demografía de la ciudad.

La riqueza industrial permitió construir el Gran Teatro Arriaga, el Puente de Vizcaya, y desarrollar el Ensanche con arquitectura modernista. Bilbao pasó de ser una villa medieval a ser "el Manchester del norte de España".

La crisis industrial de los 80 dejó la Ría contaminada y miles de desempleados. Fue el punto más bajo antes de la regeneración urbana de los 90.',

'Siglo XIX: Bilbao se transforma con minería e industria. Familias como Ybarra construyen imperios. "Manchester del norte".',
'Siglo XIX', 'historia',
ARRAY['industria', 'minería', 'Ría', 'burguesía', 'desarrollo'],
'detallado', 'es'),

('Guggenheim', 'El Efecto Guggenheim',
'La inauguración del Museo Guggenheim en 1997 marcó un antes y un después en la historia de Bilbao. Diseñado por Frank Gehry, el edificio de titanio se convirtió en símbolo mundial de la regeneración urbana.

El "Efecto Guggenheim" es estudiado en escuelas de arquitectura y urbanismo de todo el mundo como ejemplo de transformación post-industrial. La inversión pública de 100 millones de euros se recuperó en impuestos en menos de 3 años.

El museo atrajo turismo cultural de alto nivel. Hoteles, restaurantes y servicios se multiplicaron. Bilbao pasó de ciudad industrial en crisis a destino cultural de referencia europea.

Más allá del turismo, el Guggenheim cambió la autoestima de los bilbaínos. La ciudad recuperó orgullo y proyección internacional.

El debate sigue abierto: ¿Fue una apuesta arriesgada que salió bien o un modelo insostenible basado en arquitectura-espectáculo?',

'1997: Guggenheim transforma Bilbao. "Efecto Guggenheim" estudiado mundialmente. Ciudad industrial → Destino cultural.',
'Siglo XX', 'historia',
ARRAY['Guggenheim', 'arquitectura', 'regeneración', 'turismo', 'cultura'],
'detallado', 'es'),

('Gastronomía', 'Pintxos: Más que Tapas',
'Los pintxos vascos no son tapas. Son miniatura de alta cocina con producto local de primera calidad. Cada bar tiene su especialidad y su competencia es feroz.

El ritual del txikiteo (ir de pintxos) es sagrado: se va de bar en bar, tomando uno o dos pintxos y un zurito (cerveza pequeña) o txakoli. Se come de pie, en la barra, conversando. No se trata de llenar el estómago, sino de socializar.

Los pintxos evolucionan constantemente. De la clásica gilda (anchoa, guindilla, oliva) se ha pasado a creaciones elaboradas con técnicas de vanguardia.

Los mejores bares de pintxos no están en las guías turísticas. Los bilbaínos los conocen de toda la vida y los protegen celosamente.

Tres reglas no escritas del txikiteo:
1. Nunca pidas solo un pintxo en un bar (mínimo dos).
2. El txikiteo es después de las 20h, no antes.
3. Si te invitan a un pintxo, devuelves la invitación en el siguiente bar.',

'Pintxos ≠ tapas. Miniatura de alta cocina. Txikiteo: ritual social vasco de ir de bar en bar.',
'Contemporáneo', 'gastronomía',
ARRAY['pintxos', 'txikiteo', 'gastronomía', 'cocina vasca', 'tradición'],
'detallado', 'es'),

('Semana Grande', 'Aste Nagusia: Semana Grande de Bilbao',
'La Aste Nagusia (Semana Grande) empieza el primer sábado después del 15 de agosto. Durante 9 días, Bilbao se transforma: conciertos gratuitos, fuegos artificiales, teatro callejero, y competiciones tradicionales vascas.

El símbolo de la fiesta es Marijaia, una figura de mujer con los brazos alzados que se instala en el Teatro Arriaga. Cuando Marijaia "llega", la fiesta comienza. Cuando se quema el último día, la ciudad se despide con melancolía.

Las txoznas (casetas) en el Arenal son el corazón social: bebida barata, música en vivo y ambiente festivo hasta las tantas. Cada txozna la gestiona una cuadrilla o grupo de amigos.

Los conciertos en Kobetamendi son gratuitos y de primer nivel: rock, folk, reggae, música vasca. Los bilbaínos suben con bocadillos y cerveza a ver el atardecer mientras suena la música.

Es la única semana del año donde Bilbao se transforma completamente. Los que pueden, se quedan. Los que trabajan, aguantan con ojeras y resaca.',

'Aste Nagusia: 9 días de fiesta en agosto. Marijaia, txoznas, conciertos gratuitos. Bilbao se transforma.',
'Contemporáneo', 'tradición',
ARRAY['Aste Nagusia', 'fiestas', 'Marijaia', 'tradición', 'cultura'],
'detallado', 'es'),

('Idioma Euskera', 'Euskera: La Lengua Misteriosa',
'El euskera (vasco) es el idioma más antiguo de Europa. No tiene relación con ninguna lengua indoeuropea. Su origen es un misterio lingüístico sin resolver.

Durante el franquismo fue prohibido en público. Se hablaba en casa, en el caserío, en secreto. La recuperación del euskera después de la democracia fue un acto político y cultural.

En Bilbao, el euskera se estudia en las ikastolas (escuelas en euskera) y está presente en señales, nombres de calles y espacios públicos. Sin embargo, solo el 15% de la población bilbaína lo habla con fluidez (menos que en Donosti o Vitoria).

Hay dos dialectos principales: vizcaíno y guipuzcoano. El euskera batua es la versión estandarizada para educación y medios.

Expresiones vascas se mezclan en el castellano hablado en Bilbao: "Aupa", "Epa", "Agur" son parte del vocabulario diario. Es una forma de identidad compartida.',

'Euskera: idioma más antiguo de Europa sin relación con otras lenguas. Prohibido en franquismo, recuperado en democracia.',
'Histórico-Contemporáneo', 'cultura',
ARRAY['euskera', 'idioma', 'identidad', 'cultura vasca', 'historia'],
'detallado', 'es'),

('Txakoli', 'Txakoli: El Vino Blanco Vasco',
'El txakoli (txakolina en euskera) es el vino blanco autóctono del País Vasco. Ligeramente espumoso, ácido, refrescante. Graduación baja (10-11%). Perfecto para acompañar pintxos y pescado.

Se produce en tres denominaciones de origen: Getariako Txakolina (Guipúzcoa), Bizkaiko Txakolina (Vizcaya), y Arabako Txakolina (Álava).

La tradición dice que se debe escanciarlo desde alto para airear el vino y activar las burbujas. El ritual de escanciado es todo un espectáculo en los bares tradicionales.

Durante décadas fue un vino "de casa", producido en pequeños caseríos para consumo familiar. En los 90 se profesionalizó con bodegas modernas y D.O.

El mejor maridaje: gildas, anchoas del Cantábrico, chipirones a la plancha, o simplemente pan con aceite y sal.',

'Txakoli: vino blanco vasco ligeramente espumoso. Escanciado desde alto. Maridaje perfecto con pintxos y pescado.',
'Contemporáneo', 'gastronomía',
ARRAY['txakoli', 'vino', 'gastronomía', 'tradición', 'bebida'],
'resumen', 'es');

-- ============================================
-- MENSAJE DE ÉXITO
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Seed data cargado exitosamente';
    RAISE NOTICE '📍 Lugares insertados: 20';
    RAISE NOTICE '📚 Artículos históricos: 7';
    RAISE NOTICE '🎯 Listo para generar embeddings via n8n';
END $$;
