-- Datos de prueba para musica.db
-- 5 usuarios y 10 canciones (las duraciones son aproximadas, en segundos)
-- Ejecutar UNA sola vez: el correo de usuario es único y repetir da error.

INSERT INTO usuario (nombre, correo, fecha_registro) VALUES
  ('Ana Torres',       'ana.torres@example.com',       '2026-11-17 10:00:00.000000'),
  ('Carlos Gómez',     'carlos.gomez@example.com',     '2026-11-17 10:00:00.000000'),
  ('Laura Martínez',   'laura.martinez@example.com',   '2026-11-17 10:00:00.000000'),
  ('Andrés Rojas',     'andres.rojas@example.com',     '2026-11-17 10:00:00.000000'),
  ('Valentina Díaz',   'valentina.diaz@example.com',   '2026-11-17 10:00:00.000000');

INSERT INTO cancion (titulo, artista, album, duracion, "año", genero, fecha_creacion) VALUES
  ('Bohemian Rhapsody',       'Queen',            'A Night at the Opera',                          354, 1975, 'Rock',      '2026-11-17 10:00:00.000000'),
  ('Billie Jean',             'Michael Jackson',  'Thriller',                                      294, 1982, 'Pop',       '2026-11-17 10:00:00.000000'),
  ('Smells Like Teen Spirit', 'Nirvana',          'Nevermind',                                     301, 1991, 'Grunge',    '2026-11-17 10:00:00.000000'),
  ('Imagine',                 'John Lennon',      'Imagine',                                       187, 1971, 'Rock',      '2026-11-17 10:00:00.000000'),
  ('Gasolina',                'Daddy Yankee',     'Barrio Fino',                                   192, 2004, 'Reguetón',  '2026-11-17 10:00:00.000000'),
  ('Hips Don''t Lie',         'Shakira',          'Oral Fixation, Vol. 2',                         218, 2006, 'Pop',       '2026-11-17 10:00:00.000000'),
  ('Despacito',               'Luis Fonsi',       'Vida',                                          229, 2017, 'Reguetón',  '2026-11-17 10:00:00.000000'),
  ('Shape of You',            'Ed Sheeran',       '÷ (Divide)',                                    234, 2017, 'Pop',       '2026-11-17 10:00:00.000000'),
  ('La Bicicleta',            'Carlos Vives',     'Vives',                                         227, 2016, 'Vallenato', '2026-11-17 10:00:00.000000'),
  ('bad guy',                 'Billie Eilish',    'When We All Fall Asleep, Where Do We Go?',      194, 2019, 'Pop',       '2026-11-17 10:00:00.000000');