-- Leagues
INSERT INTO Leagues (name, country, level) VALUES
('Premier League', 'England', 1),
('La Liga', 'Spain', 1);

-- Clubs
INSERT INTO Clubs (name, city, founded_year, league_id) VALUES
('Manchester United', 'Manchester', 1878, 1),
('Liverpool', 'Liverpool', 1892, 1),
('Real Madrid', 'Madrid', 1902, 2),
('Barcelona', 'Barcelona', 1899, 2);

-- League_Teams
INSERT INTO League_Teams (league_id, club_id, season) VALUES
(1, 1, '2025/2026'),
(1, 2, '2025/2026'),
(2, 3, '2025/2026'),
(2, 4, '2025/2026');

-- Players
INSERT INTO Players (first_name, last_name, position, age, club_id, nationality) VALUES
('Marcus', 'Rashford', 'Forward', 26, 1, 'ENG'),
('Mohamed', 'Salah', 'Forward', 30, 2, 'EGY'),
('Karim', 'Benzema', 'Forward', 35, 3, 'FRA'),
('Robert', 'Lewandowski', 'Forward', 35, 4, 'POL');

-- Transfers
INSERT INTO Transfers (player_id, from_club_id, to_club_id, transfer_date, fee) VALUES
(1, 2, 1, '2023-07-01', 100000000),
(4, 3, 4, '2022-08-15', 50000000);

-- Matches
INSERT INTO Matches (home_club_id, away_club_id, home_goals, away_goals, match_date, league_id) VALUES
(1, 2, 2, 1, '2026-02-20', 1),
(3, 4, 3, 2, '2026-02-21', 2);

-- Goals
INSERT INTO Goals (match_id, player_id, minute, type) VALUES
(1, 1, 15, 'Regular'),
(1, 2, 45, 'Regular'),
(2, 3, 10, 'Regular'),
(2, 4, 20, 'Penalty');

-- Cards
INSERT INTO Cards (match_id, player_id, type, minute) VALUES
(1, 1, 'Yellow', 30),
(1, 2, 'Red', 70),
(2, 3, 'Yellow', 50);
