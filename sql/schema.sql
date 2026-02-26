PRAGMA foreign_keys = ON;

CREATE TABLE Leagues (
    league_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    level INTEGER NOT NULL
);

CREATE TABLE Clubs (
    club_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    founded_year INTEGER NOT NULL,
    league_id INTEGER,
    FOREIGN KEY (league_id) REFERENCES Leagues(league_id)
);

CREATE TABLE League_Teams (
    league_team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    season TEXT NOT NULL,
    FOREIGN KEY (league_id) REFERENCES Leagues(league_id),
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id)
);

CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    birth_date TEXT NOT NULL,  
    nationality TEXT NOT NULL,
    position TEXT NOT NULL CHECK(position IN ('GK', 'DF', 'MF', 'FW')),
    number INTEGER NOT NULL CHECK(number BETWEEN 1 AND 99),
    status TEXT NOT NULL DEFAULT 'active',
    club_id INTEGER NOT NULL,
    FOREIGN KEY (club_id) REFERENCES clubs(club_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    UNIQUE(club_id, number)
);

CREATE TABLE Transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    from_club_id INTEGER,
    to_club_id INTEGER NOT NULL,
    transfer_date TEXT NOT NULL,
    fee REAL,
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (from_club_id) REFERENCES Clubs(club_id),
    FOREIGN KEY (to_club_id) REFERENCES Clubs(club_id)
);

CREATE TABLE Matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    home_club_id INTEGER NOT NULL,
    away_club_id INTEGER NOT NULL,
    home_goals INTEGER DEFAULT 0,
    away_goals INTEGER DEFAULT 0,
    match_date TEXT NOT NULL,
    league_id INTEGER NOT NULL,
    FOREIGN KEY (home_club_id) REFERENCES Clubs(club_id),
    FOREIGN KEY (away_club_id) REFERENCES Clubs(club_id),
    FOREIGN KEY (league_id) REFERENCES Leagues(league_id)
);

CREATE TABLE Goals (
    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    type TEXT,
    FOREIGN KEY (match_id) REFERENCES Matches(match_id),
    FOREIGN KEY (player_id) REFERENCES Players(player_id)
);

CREATE TABLE Cards (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    minute INTEGER NOT NULL,
    FOREIGN KEY (match_id) REFERENCES Matches(match_id),
    FOREIGN KEY (player_id) REFERENCES Players(player_id)
);
