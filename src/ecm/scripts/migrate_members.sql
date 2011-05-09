------------------------------------------------------------------
-- MIGRATE MEMBERS
------------------------------------------------------------------

-- BACKUP OLD TABLES
CREATE TABLE "roles_memberdiff_old" (
    "id" integer NOT NULL PRIMARY KEY,
    "characterID" bigint NOT NULL,
    "name" varchar(100) NOT NULL,
    "nickname" varchar(256) NOT NULL,
    "new" bool NOT NULL,
    "date" datetime NOT NULL
)
;

CREATE TABLE "roles_member_old" (
    "characterID" bigint NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "nickname" varchar(256) NOT NULL,
    "baseID" bigint NOT NULL,
    "corpDate" datetime NOT NULL,
    "lastLogin" datetime NOT NULL,
    "lastLogoff" datetime NOT NULL,
    "location" varchar(256) NOT NULL,
    "ship" varchar(128) NOT NULL,
    "accessLvl" integer unsigned NOT NULL,
    "corped" bool NOT NULL
)
;

INSERT INTO roles_memberdiff_old(id, characterID, name, nickname, new, date) 
SELECT id, characterID, name, nickname, new, date FROM roles_memberdiff;

INSERT INTO roles_member_old(characterID, name, nickname, baseID, corpDate, lastLogin, 
                             lastLogoff, location, ship, accessLvl, corped) 
SELECT characterID, name, nickname, baseID, corpDate, lastLogin, lastLogoff, 
       location, ship, accessLvl, corped FROM roles_member;

DROP TABLE roles_member;
DROP TABLE roles_memberdiff;

-- here, invoke syncdb to create new tables

-- restore old entries
INSERT INTO roles_member(characterID, name, nickname, baseID, corpDate, lastLogin, 
                             lastLogoff, location, ship, accessLvl, corped) 
SELECT characterID, name, nickname, baseID, corpDate, lastLogin, lastLogoff, 
       location, ship, accessLvl, corped FROM roles_member_old;

INSERT INTO roles_memberdiff(id, member_id, name, nickname, new, date) 
SELECT id, characterID, name, nickname, new, date 
FROM roles_memberdiff_old WHERE characterID IN (SELECT characterID FROM roles_member);

DROP TABLE roles_member_old;
DROP TABLE roles_memberdiff_old;

-- here attach the EVE database

-- resolve locationIDs from locationNames
UPDATE main.roles_member 
SET locationID = 
    IFNULL(
	    (SELECT stationID FROM EVE.staStations WHERE stationName == roles_member.location)
        , 
        IFNULL(
            (SELECT solarSystemID FROM EVE.mapSolarSystems WHERE solarSystemName == roles_member.location)
            ,
            IFNULL(
                (SELECT stationID FROM main.common_outpost WHERE stationName LIKE '%' + roles_member.location + '%')
                ,
                0
            )
        )
    )
WHERE locationID = 0; 
