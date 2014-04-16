
-- DROP TABLE GENRE_MTV;
DROP TABLE OPENINGS_WEEK; 
-- DROP TABLE CURRENT_TV_SCHEDULE; 
DROP TABLE MOVIES; 
-- DROP TABLE TV; 
-- DROP TABLE JOBS;
-- DROP TABLE WORKERS; 
-- DROP TABLE MEDIA; 

-- DROP TABLE GENRE;  


-- CREATE TABLE MEDIA(
-- ID serial not null,
-- Entry_ID int NOT NULL,
-- Title VARCHAR(255) NOT NULL,
-- Type boolean NOT NULL,
-- Poster VARCHAR(255),
-- primary key (ID)
-- );

CREATE TABLE MOVIES(
Movie_ID int NOT NULL,
Media_ID int unique REFERENCES Media(ID),
IMDB_ID VARCHAR(255) unique NOT NULL,
Release_Date date,
CRATING int,
URating int,
IMDB_Rating int,
MPAA_RATING VARCHAR(20),
primary key (Movie_ID)
);

-- CREATE TABLE TV(
-- TV_ID int NOT NULL,
-- Media_ID int NOT NULL REFERENCES Media(ID),
-- first_air_date date not null,
-- last_air_date date,
-- Episodes int,
-- Seasons int,
-- primary key (TV_ID)
-- );

CREATE TABLE OPENINGS_WEEK(
M_ID int NOT NULL REFERENCES Movies(Movie_ID),
Premiere_Date date,
Running_Time int,
Description VARCHAR(255),
primary key(M_ID)
);

-- CREATE TABLE CURRENT_TV_SCHEDULE(
-- TV_ID int NOT NULL REFERENCES TV(TV_ID),
-- Time date,
-- Broad_Comp VARCHAR(125),
-- Ep_No int,
-- S_No int,
-- Description VARCHAR(255),
-- primary key (TV_ID, Time)
-- );

-- CREATE TABLE WORKERS(
-- W_ID INT NOT NULL,
-- Name int,
-- primary key(W_ID)
-- );

-- CREATE TABLE JOBS(
-- Media_ID INT  NOT NULL REFERENCES  Media(ID),
-- W_ID INT NOT NULL REFERENCES WORKERS(W_ID),
-- Type boolean NOT NULL,
-- Role VARCHAR(255) NOT NULL,
-- primary key (Media_ID, W_ID, Role)
-- );

-- CREATE TABLE GENRE(
-- ID INT NOT NULL,
-- TITLE VARCHAR(255) NOT NULL,
-- primary key (ID)
-- );

-- CREATE TABLE GENRE_MTV(
-- G_ID INT NOT NULL REFERENCES GENRE(ID),
-- Media_ID INT NOT NULL REFERENCES Media(ID),
-- primary key (G_ID, Media_ID)
-- );