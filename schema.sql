PRAGMA foreign_keys = ON;

CREATE TABLE Clubs (
    club_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    founded_year INTEGER NOT NULL
);

CREATE TABLE Players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT NOT NULL,
    age INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id)
        ON DELETE CASCADE
);

CREATE TABLE Matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    home_club_id INTEGER NOT NULL,
    away_club_id INTEGER NOT NULL,
    home_goals INTEGER NOT NULL,
    away_goals INTEGER NOT NULL,
    match_date TEXT NOT NULL,
    FOREIGN KEY (home_club_id) REFERENCES Clubs(club_id),
    FOREIGN KEY (away_club_id) REFERENCES Clubs(club_id)
);
