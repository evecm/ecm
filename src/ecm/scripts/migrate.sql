CREATE TABLE "roles_memberdiff_old" (
    "id" integer NOT NULL PRIMARY KEY,
    "member_id" bigint NOT NULL REFERENCES "roles_member" ("characterID"),
    "name" varchar(100) NOT NULL,
    "nickname" varchar(256) NOT NULL,
    "new" bool NOT NULL,
    "date" datetime NOT NULL
)
;



insert into roles_memberdiff_old(id, characterID, name, nickname, new, date) 
select id, characterID, name, nickname, new, date from roles_memberdiff;


CREATE TABLE "roles_member_old" (
    "characterID" bigint NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "nickname" varchar(256) NOT NULL,
    "baseID" bigint NOT NULL,
    "corpDate" datetime NOT NULL,
    "lastLogin" datetime NOT NULL,
    "lastLogoff" datetime NOT NULL,
    "locationID" integer NOT NULL,
    "location" varchar(256) NOT NULL,
    "ship" varchar(128) NOT NULL,
    "accessLvl" integer unsigned NOT NULL,
    "corped" bool NOT NULL
)
;


insert into roles_member_old(characterID, name, nickname, baseID, corpDate, lastLogin, lastLogoff, locationID, location, ship, accessLvl, corped) 
select characterID, name, nickname, baseID, corpDate, lastLogin, lastLogoff, 0, location, ship, accessLvl, corped from roles_member;




UPDATE main.roles_member_old SET locationID = IFNULL((SELECT stationID FROM "EVE"."staStations" WHERE stationName == main.roles_member_old.location),0); 


UPDATE main.roles_member_old SET locationID = IFNULL((SELECT solarSystemID FROM "EVE"."mapSolarSystems" WHERE solarSystemName == main.roles_member_old.location),0) WHERE main.roles_member_old.locationID == 0;

UPDATE main.roles_member_old SET locationID = IFNULL((SELECT stationID FROM main.common_outpost WHERE stationName LIKE "%" + main.roles_member_old.location + "%"),0) WHERE main.roles_member_old.locationID == 0;



