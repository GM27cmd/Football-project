
INSERT INTO Clubs (name, city, founded_year) VALUES
('Manchester United', 'Manchester', 1878),
('Real Madrid', 'Madrid', 1902),
('Bayern Munich', 'Munich', 1900),
('Juventus', 'Turin', 1897),
('Barcelona', 'Barcelona', 1899);


INSERT INTO Players (name, position, age, club_id) VALUES
('Marcus Rashford', 'Forward', 26, 1),
('Luka Modric', 'Midfielder', 38, 2),
('Thomas Muller', 'Forward', 34, 3),
('Dusan Vlahovic', 'Forward', 24, 4),
('Robert Lewandowski', 'Forward', 35, 5);


INSERT INTO Matches (home_club_id, away_club_id, home_goals, away_goals, match_date) VALUES
(1, 2, 2, 1, '2024-03-10'),
(3, 4, 3, 0, '2024-03-12'),
(5, 1, 1, 1, '2024-03-15');
