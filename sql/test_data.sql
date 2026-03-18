-- =========================
-- Клубове
-- =========================
INSERT INTO Clubs (name, city, founded_year, league_id) VALUES
('Левски', 'София', 1914, NULL),
('ЦСКА', 'София', 1948, NULL),
('Лудогорец', 'Разград', 2001, NULL),
('Ботев', 'Пловдив', 1912, NULL);

-- =========================
-- Играч
-- =========================
INSERT INTO Players (full_name, birth_date, nationality, position, number, status, club_id) VALUES
('Иван Петров', '2000-01-01', 'България', 'FW', 9, 'active', 1),
('Георги Иванов', '1999-05-05', 'България', 'MF', 8, 'active', 1),
('Петър Георгиев', '2001-02-02', 'България', 'DF', 4, 'active', 2),
('Мартин Стоянов', '1998-03-03', 'България', 'MF', 6, 'active', 3),
('Александър Иванов', '2002-04-04', 'България', 'FW', 10, 'active', 4),
('Никола Димов', '2001-06-06', 'България', 'GK', 1, 'active', 2);

-- =========================
-- Примерни трансфери
-- =========================
-- Иван Петров: Левски → Лудогорец
INSERT INTO Transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note) VALUES
(1, 1, 3, '2025-01-15', 30000, 'Прехвърлен за нов сезон');

-- Георги Иванов: ЦСКА → Левски
INSERT INTO Transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note) VALUES
(2, 2, 1, '2025-02-20', 50000, 'Междуклубен трансфер');

-- Петър Георгиев: Ботев → ЦСКА
INSERT INTO Transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note) VALUES
(3, 4, 2, '2025-03-10', 25000, NULL);

-- Мартин Стоянов: свободен агент → Лудогорец
INSERT INTO Transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note) VALUES
(4, NULL, 3, '2025-04-05', 0, 'Свободен агент');

-- Александър Иванов: Ботев → Левски
INSERT INTO Transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note) VALUES
(5, 4, 1, '2025-05-12', 40000, 'Летен трансфер');
