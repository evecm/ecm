------------------------------------------------------------------
-- MIGRATE ASSETS
------------------------------------------------------------------

-- BACKUP OLD TABLES
CREATE TABLE "assets_asset_old" (
    "itemID" bigint NOT NULL PRIMARY KEY,
    "locationID" bigint NOT NULL,
    "hangarID" smallint unsigned NOT NULL,
    "container1" bigint,
    "container2" bigint,
    "typeID" integer unsigned NOT NULL,
    "quantity" integer unsigned NOT NULL,
    "flag" smallint unsigned NOT NULL,
    "singleton" bool NOT NULL,
    "hasContents" bool NOT NULL
);
INSERT INTO assets_asset_old(itemID, locationID, hangarID, container1, container2, typeID, quantity, flag, singleton, hasContents)
SELECT itemID, locationID, hangarID, container1, container2, typeID, quantity, flag, singleton, hasContents FROM assets_dbasset;

CREATE TABLE "assets_assetdiff_old" (
    "id" integer NOT NULL PRIMARY KEY,
    "locationID" bigint NOT NULL,
    "hangarID" smallint unsigned NOT NULL,
    "typeID" integer unsigned NOT NULL,
    "quantity" integer NOT NULL,
    "date" datetime NOT NULL,
    "new" bool NOT NULL
);
INSERT INTO assets_assetdiff_old(id, locationID, hangarID, typeID, quantity, date, new)
SELECT id, locationID, hangarID, typeID, quantity, date, new FROM assets_dbassetdiff;

DROP TABLE assets_dbassetdiff;
DROP TABLE assets_dbasset;


-- HERE, INVOKE syncdb

-- RESTORE OLD ENTRIES INTO NEW TABLES
INSERT INTO assets_asset(itemID, solarSystemID, stationID, hangarID, container1, container2, typeID, quantity, flag, singleton, hasContents)
SELECT itemID, 0, locationID, hangarID, container1, container2, typeID, quantity, flag, singleton, hasContents FROM assets_asset_old;

insert into assets_assetdiff(id, solarSystemID, stationID, hangarID, typeID, quantity, date, new, flag)
select id, 0, locationID, hangarID, typeID, quantity, date, new, 0 from assets_assetdiff_old;

DROP TABLE assets_assetdiff_old;
DROP TABLE assets_asset_old;

-- HERE, ATTACH EVE DATABASE

-- RESOLVE SOLAR SYSTEM IDs 
UPDATE assets_asset 
SET solarSystemID = 
    IFNULL((SELECT eve.solarSystemID 
            FROM EVE.staStations AS eve
            WHERE assets_asset.stationID == eve.stationID)
           , 
            (SELECT out.solarSystemID 
            FROM common_outpost as out
            WHERE assets_asset.stationID == out.stationID)) 
WHERE solarSystemID == 0;

UPDATE assets_assetdiff
SET solarSystemID = 
    IFNULL((SELECT eve.solarSystemID 
            FROM EVE.staStations AS eve
            WHERE assets_assetdiff.stationID == eve.stationID)
           , 
            (SELECT out.solarSystemID 
            FROM common_outpost as out
            WHERE assets_assetdiff.stationID == out.stationID)) 
WHERE solarSystemID = 0;