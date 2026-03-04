-- Leagues
INSERT INTO Leagues (name, country, level) VALUES
('Premier League', 'England', 1),
('La Liga', 'Spain', 1);

-- Clubs (сега подаваме founded_year и league_id)
INSERT INTO Clubs (name, city, founded_year, league_id) VALUES
('Левски', 'София', 1914, 1),
('Лудогорец', 'Разград', 2001, 1),
('Ботев', 'Пловдив', 1912, 2),
('ЦСКА', 'София', 1948, 2);

-- League_Teams
INSERT INTO League_Teams (league_id, club_id, season) VALUES
(1, 1, '2025/2026'),
(1, 2, '2025/2026'),
(2, 3, '2025/2026'),
(2, 4, '2025/2026');

-- Players
INSERT INTO Players
(full_name, birth_date, nationality, position, number, status, club_id)
VALUES
('Иван Петров', '2000-05-10', 'България', 'FW', 9, 'active', 1),
('Георги Стоянов', '1998-03-21', 'България', 'MF', 8, 'active', 1),
('Martin Ivanov', '2002-07-15', 'България', 'GK', 1, 'active', 2);

-- Transfers (поправен player_id)
INSERT INTO Transfers (player_id, from_club_id, to_club_id, transfer_date, fee) VALUES
(1, 2, 1, '2023-07-01', 100000000),
(2, 3, 1, '2022-08-15', 50000000);

-- Matches
INSERT INTO Matches (home_club_id, away_club_id, home_goals, away_goals, match_date, league_id) VALUES
(1, 2, 2, 1, '2026-02-20', 1),
(3, 4, 3, 2, '2026-02-21', 2);

-- Goals (поправен player_id 4 -> 2)
INSERT INTO Goals (match_id, player_id, minute, type) VALUES
(1, 1, 15, 'Regular'),
(1, 2, 45, 'Regular'),
(2, 3, 10, 'Regular');

-- Cards
INSERT INTO Cards (match_id, player_id, type, minute) VALUES
(1, 1, 'Yellow', 30),
(1, 2, 'Red', 70),
(2, 3, 'Yellow', 50);
