-- Copyright (c) 2010-2011 Robin Jarry
--
-- This file is part of EVE Corporation Management.
--
-- EVE Corporation Management is free software: you can redistribute it and/or
-- modify it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or (at your
-- option) any later version.
--
-- EVE Corporation Management is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
-- or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
-- more details.
--
-- You should have received a copy of the GNU General Public License along with
-- EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.


BEGIN;

------------------------------------------
-- CUSTOM blueprints requirements table --
------------------------------------------
CREATE TABLE "ramBlueprintReqs" (
    "id" INT(13),                      -- primary key
    "blueprintTypeID" SMALLINT,       -- id of blueprint using this material
    "activityID" TINYINT UNSIGNED,    -- building, copying, etc
    "requiredTypeID" SMALLINT,        -- id of resource used for this activity
    "quantity" INT,                   -- how many of this resource is used
    "damagePerJob" DOUBLE,            -- how much of the resource is expended
    "baseMaterial" INT,               -- how much is the base material.
                                    -- 0 means unaffected by waste, >=quantity means entirely affected
    PRIMARY KEY ("id")
);

CREATE INDEX "ramBlueprintReqs_IX_blueprintTypeID" ON "ramBlueprintReqs" ("blueprintTypeID");
CREATE INDEX "ramBlueprintReqs_IX_activityID" ON "ramBlueprintReqs" ("activityID");
CREATE INDEX "ramBlueprintReqs_IX_requiredTypeID" on "ramBlueprintReqs" ("requiredTypeID");

-- The following queries take invTypeMaterials and ramTypeRequirements and combine them
-- into a single table showing all the materials a blueprint requires, and how much of each
-- material is affected by waste when building.
-------------------------------------------------------
INSERT INTO "ramBlueprintReqs"
    SELECT  rtr."typeID" * 100000000 + rtr."requiredTypeID" * 100 + rtr."activityID",
            rtr."typeID",
            rtr."activityID",
            rtr."requiredTypeID",
            (rtr."quantity" + IFNULL(itm."quantity", 0)),
            rtr."damagePerJob",
            itm."quantity"
    FROM "invBlueprintTypes" AS b
       INNER JOIN "ramTypeRequirements" AS rtr
           ON rtr."typeID" = b."blueprintTypeID"
          AND rtr."activityID" = 1 -- manufacturing
       LEFT OUTER JOIN "invTypeMaterials" AS itm
           ON itm."typeID" = b."productTypeID"
          AND itm."materialTypeID" = rtr."requiredTypeID"
    WHERE rtr."quantity" > 0
;
----------------------------------------------------------
INSERT INTO "ramBlueprintReqs"
    SELECT  b."blueprintTypeID" * 100000000 + itm."materialTypeID" * 100 + 1,
            b."blueprintTypeID",
            1,  -- manufacturing activityID
            itm."materialTypeID",   -- requiredTypeID
            (itm."quantity" - IFNULL(sub."quantity" * sub."recycledQuantity", 0)),  -- quantity
            1,   -- damagePerJob
            (itm."quantity" - IFNULL(sub."quantity" * sub."recycledQuantity", 0))  -- baseMaterial
    FROM "invBlueprintTypes" AS b
       INNER JOIN "invTypeMaterials" AS itm
           ON itm."typeID" = b."productTypeID"
       LEFT OUTER JOIN "ramBlueprintReqs" m
           ON b."blueprintTypeID" = m."blueprintTypeID"
           AND m."requiredTypeID" = itm."materialTypeID"
       LEFT OUTER JOIN (
           SELECT srtr."typeID" AS "blueprintTypeID", -- tech 2 items recycle into their materials
                  sitm."materialTypeID" AS "recycledTypeID",   -- plus the t1 item's materials
                  srtr."quantity" AS "recycledQuantity",
                  sitm."quantity" AS "quantity"
           FROM "ramTypeRequirements" AS srtr
               INNER JOIN "invTypeMaterials" AS sitm
                   ON srtr."requiredTypeID" = sitm."typeID"
           WHERE srtr."recycle" = 1   -- the recycle flag determines whether or not this requirement's materials are added
             AND srtr."activityID" = 1
       ) AS sub
           ON sub."blueprintTypeID" = b."blueprintTypeID"
           AND sub."recycledTypeID" = itm."materialTypeID"
    WHERE m."blueprintTypeID" IS NULL -- partially waste-affected materials already added
    AND (itm."quantity" - IFNULL(sub."quantity" * sub."recycledQuantity", 0)) > 0 -- ignore negative quantities
;
----------------------------------------------------------
INSERT INTO ramBlueprintReqs("id",
                             "blueprintTypeID",
                             "activityID",
                             "requiredTypeID",
                             "quantity",
                             "damagePerJob")
    SELECT  rtr."typeID" * 100000000 + rtr."requiredTypeID" * 100 + rtr."activityID",
            rtr."typeID",
            rtr."activityID",
            rtr."requiredTypeID",
            rtr."quantity",
            rtr."damagePerJob"
    FROM "ramTypeRequirements" AS rtr
    WHERE rtr."activityID" NOT IN (1)
;
----------------------------------------------------------
UPDATE "ramBlueprintReqs" SET "baseMaterial" = 0 WHERE "baseMaterial" IS NULL;

----------------------------------------------------------
-- Add noctis blueprint requirements
INSERT INTO "ramBlueprintReqs"
      --     id             bpTypeID activityID reqTypeID   qty    dmg    base
      SELECT 286400003401, 2864,    1,         34,       3349410, 1.0, 936043 -- Tritanium
UNION SELECT 286400003501, 2864,    1,         35,        936043, 1.0, 936043 -- Pyerite
UNION SELECT 286400003601, 2864,    1,         36,        276936, 1.0, 276936 -- Mexallon
UNION SELECT 286400003701, 2864,    1,         37,         50713, 1.0,  50713 -- Isogen
UNION SELECT 286400003801, 2864,    1,         38,         24630, 1.0,  24630 -- Nocxium
UNION SELECT 286400003901, 2864,    1,         39,          3438, 1.0,   3438 -- Zydrine
UNION SELECT 286400004001, 2864,    1,         40,          1580, 1.0,   1580 -- Megacyte
;

--------------------
-- PATCH invTypes --
--------------------

-- backup invTypes table and delete it
CREATE TABLE "invTypes_temp" (
  "typeID" int(11) NOT NULL,
  "groupID" smallint(6) DEFAULT NULL,
  "typeName" varchar(100) DEFAULT NULL,
  "description" varchar(3000) DEFAULT NULL,
  "graphicID" smallint(6) DEFAULT NULL,
  "radius" double DEFAULT NULL,
  "mass" double DEFAULT NULL,
  "volume" double DEFAULT NULL,
  "capacity" double DEFAULT NULL,
  "portionSize" int(11) DEFAULT NULL,
  "raceID" tinyint(3) DEFAULT NULL,
  "basePrice" double DEFAULT NULL,
  "published" tinyint(1) DEFAULT NULL,
  "marketGroupID" smallint(6) DEFAULT NULL,
  "chanceOfDuplicating" double DEFAULT NULL,
  "iconID" smallint(6) DEFAULT NULL,
  PRIMARY KEY ("typeID")
);
INSERT INTO "invTypes_temp" SELECT * FROM "invTypes";
DROP TABLE "invTypes";

-- create the new patched one
-- this is an optimization of the invTypes table,
-- the icons and corresponding blueprints are directly available without the need for SQL joins
CREATE TABLE "invTypes" (
  "typeID" int(11) NOT NULL,
  "groupID" smallint(6) DEFAULT NULL,
  "categoryID" tinyint(3) DEFAULT NULL,
  "typeName" varchar(100) DEFAULT NULL,
  "blueprintTypeID" int(11) DEFAULT NULL,
  "techLevel" smallint(6) DEFAULT NULL,
  "description" varchar(3000) DEFAULT NULL,
  "volume" double DEFAULT NULL,
  "portionSize" int(11) DEFAULT NULL,
  "raceID" tinyint(3) DEFAULT NULL,
  "basePrice" double DEFAULT NULL,
  "marketGroupID" smallint(6) DEFAULT NULL,
  "metaGroupID" smallint(6) DEFAULT NULL,
  "icon" varchar(32) DEFAULT NULL,
  "published" tinyint(1) DEFAULT NULL,
  PRIMARY KEY ("typeID")
);

CREATE INDEX "invTypes_IX_Group" ON "invTypes" ("groupID");
CREATE INDEX "invTypes_IX_iconID" ON "invTypes" ("icon");
CREATE INDEX "invTypes_IX_marketGroupID" ON "invTypes" ("marketGroupID");
CREATE INDEX "invTypes_IX_techLevel" ON "invTypes" ("techLevel");
CREATE INDEX "invTypes_IX_published" ON "invTypes" ("published");

-- fill the custom table
INSERT INTO "invTypes"
SELECT  t."typeID",
        t."groupID",
        gg."categoryID",
        t."typeName",
        b."blueprintTypeID" AS blueprintTypeID,
        b."techLevel",
        t."description",
        t."volume",
        t."portionSize",
        t."raceID",
        t."basePrice",
        t."marketGroupID",
        IFNULL(m."metaGroupID", 0) AS "metaGroupID",
        IFNULL('icon' || g."iconFile", CAST(t."typeID" AS TEXT)) AS "icon",
        t."published"
FROM "invTypes_temp" t LEFT OUTER JOIN "eveIcons" g ON t."graphicID" = g."iconID",
     "invTypes_temp" t2 LEFT OUTER JOIN "invBlueprintTypes" b ON t2."typeID" = b."productTypeID",
     "invTypes_temp" t3 LEFT OUTER JOIN "invMetaTypes" m ON t3."typeID" = m."typeID",
     "invGroups" gg
WHERE t."typeID" = t2."typeID"
  AND t."typeID" = t3."typeID"
  AND t."groupID" = gg."groupID"
  AND t."typeID" NOT IN (23693) -- this dummy item has 4 different blueprints,
                                -- if we do not ignore it, the SQL command fails...
;
-- delete the temp table
DROP TABLE "invTypes_temp";


----------------------------------------------------------
-- CREATE A SPECIAL SYSTEMS, MOONS & PLANETS TABLE for quick name resolution

CREATE TABLE "mapCelestialObjects" (
  "itemID" int(11) NOT NULL,
  "typeID" int(11) DEFAULT NULL,
  "groupID" smallint(6) DEFAULT NULL,
  "solarSystemID" int(11) DEFAULT NULL,
  "regionID" int(11) DEFAULT NULL,
  "itemName" varchar(100) DEFAULT NULL,
  "security" double DEFAULT NULL,
  "x" double DEFAULT NULL,
  "y" double DEFAULT NULL,
  "z" double DEFAULT NULL,
  PRIMARY KEY ("itemID")
);

CREATE INDEX "mapCelestialObjects_IX_region" ON "mapCelestialObjects" ("regionID");
CREATE INDEX "mapCelestialObjects_IX_system" ON "mapCelestialObjects" ("solarSystemID");

INSERT INTO "mapCelestialObjects"
SELECT  "itemID",
        "typeID",
        "groupID",
        "solarSystemID",
        "regionID",
        "itemName",
        "security",
        "x",
        "y",
        "z"
FROM "mapDenormalize"
WHERE "groupID" IN (5 /*Solar System*/, 7 /*Planet*/, 8 /*Moon*/, 15 /*Station*/)
;

UPDATE "mapCelestialObjects"
SET "security" =
    (SELECT "mapSolarSystems"."security"
       FROM "mapSolarSystems"
      WHERE "mapCelestialObjects"."itemID" = "mapSolarSystems"."solarSystemID")
WHERE "security" IS NULL
;

----------------------------------------------------------
-- ADD A dataInterfaceID TO THE invBlueprintTypes TABLE
----------------------------------------------------------
-- backup old table and delete it
CREATE TABLE "invBlueprintTypes_temp" (
  "blueprintTypeID" int(11) NOT NULL,
  "parentBlueprintTypeID" int(11) DEFAULT NULL,
  "productTypeID" int(11) DEFAULT NULL,
  "productionTime" int(11) DEFAULT NULL,
  "techLevel" smallint(6) DEFAULT NULL,
  "researchProductivityTime" int(11) DEFAULT NULL,
  "researchMaterialTime" int(11) DEFAULT NULL,
  "researchCopyTime" int(11) DEFAULT NULL,
  "researchTechTime" int(11) DEFAULT NULL,
  "productivityModifier" int(11) DEFAULT NULL,
  "materialModifier" smallint(6) DEFAULT NULL,
  "wasteFactor" smallint(6) DEFAULT NULL,
  "maxProductionLimit" int(11) DEFAULT NULL,
  PRIMARY KEY ("blueprintTypeID")
);
INSERT INTO "invBlueprintTypes_temp" SELECT * FROM "invBlueprintTypes";
DROP TABLE "invBlueprintTypes";

-- create the new table
CREATE TABLE "invBlueprintTypes" (
  "blueprintTypeID" int(11) NOT NULL,
  "parentBlueprintTypeID" int(11) DEFAULT NULL,
  "productTypeID" int(11) DEFAULT NULL,
  "productionTime" int(11) DEFAULT NULL,
  "techLevel" smallint(6) DEFAULT NULL,
  "dataInterfaceID" smallint(11) DEFAULT NULL,
  "researchProductivityTime" int(11) DEFAULT NULL,
  "researchMaterialTime" int(11) DEFAULT NULL,
  "researchCopyTime" int(11) DEFAULT NULL,
  "researchTechTime" int(11) DEFAULT NULL,
  "productivityModifier" int(11) DEFAULT NULL,
  "materialModifier" smallint(6) DEFAULT NULL,
  "wasteFactor" smallint(6) DEFAULT NULL,
  "maxProductionLimit" int(11) DEFAULT NULL,
  PRIMARY KEY ("blueprintTypeID")
)
;
CREATE INDEX "invBlueprintTypes_IX_parentBlueprintTypeID" ON "invBlueprintTypes" ("parentBlueprintTypeID");
CREATE INDEX "invBlueprintTypes_IX_productTypeID" ON "invBlueprintTypes" ("productTypeID");

-- fill the new table
INSERT INTO "invBlueprintTypes" (
  "blueprintTypeID",
  "parentBlueprintTypeID",
  "productTypeID",
  "productionTime",
  "techLevel",
  "researchProductivityTime",
  "researchMaterialTime",
  "researchCopyTime",
  "researchTechTime",
  "productivityModifier",
  "materialModifier",
  "wasteFactor",
  "maxProductionLimit"
) SELECT * FROM "invBlueprintTypes_temp"
;

-- drop the temp table
DROP TABLE "invBlueprintTypes_temp";

-- fill the dataInterfaceID field
UPDATE "invBlueprintTypes"
SET "dataInterfaceID" =
  (SELECT r."requiredTypeID"
     FROM "ramBlueprintReqs" AS r,
          "invTypes" AS t
    WHERE "invBlueprintTypes"."blueprintTypeID" = r."blueprintTypeID"
      AND r."requiredTypeID" = t."typeID"
      AND r."activityID" = 8 /* invention */
      AND t."groupID" = 716 /* data interfaces*/)
;

----------------------------------------------------------
-- UPDATE THE parentBlueprintID FIELD IN THE invBlueprintTypes TABLE
-- FOR TECH II ITEMS BILL OF MATERIALS CALCULATION
----------------------------------------------------------

-- we first set all parentBlueprintTypeID to NULL
-- because some are already set to wrong values
UPDATE "invBlueprintTypes"
SET "parentBlueprintTypeID" = NULL;

-- then we get the parent item (for each tech 2 item)
-- from the "invMetaTypes" table and resolve its blueprint.
UPDATE "invBlueprintTypes"
SET "parentBlueprintTypeID" =
    (SELECT b."blueprintTypeID"
     FROM "invBlueprintTypes" AS b,
          "invMetaTypes" AS m
     WHERE "invBlueprintTypes"."productTypeID" = m."typeID"
       AND b."productTypeID" = m."parentTypeID"
       AND m."metaGroupID" = 2 /* only tech2 items are concerned with invention */)
;

-- this way, when manufacturing a tech 2 item,
-- we can easily know on which blueprint we need to run an invention job
-- in order to obtain the item's tech 2 BPC

---------------------------------------------------------
-- add a unique primary key to the invControlTowerResources table
---------------------------------------------------------
CREATE TABLE "invControlTowerResources_temp" (
  "controlTowerTypeID" int(11) NOT NULL,
  "resourceTypeID" int(11) NOT NULL,
  "purpose" tinyint(4) DEFAULT NULL,
  "quantity" int(11) DEFAULT NULL,
  "minSecurityLevel" double DEFAULT NULL,
  "factionID" int(11) DEFAULT NULL,
  PRIMARY KEY ("controlTowerTypeID","resourceTypeID")
);
INSERT INTO "invControlTowerResources_temp" SELECT * FROM "invControlTowerResources";
DROP TABLE "invControlTowerResources";

CREATE TABLE "invControlTowerResources" (
  "id" INT(11) NOT NULL,
  "controlTowerTypeID" int(11) NOT NULL,
  "resourceTypeID" int(11) NOT NULL,
  "purpose" tinyint(4) DEFAULT NULL,
  "quantity" int(11) DEFAULT NULL,
  "minSecurityLevel" double DEFAULT NULL,
  "factionID" int(11) DEFAULT NULL,
  PRIMARY KEY ("id")
);

CREATE INDEX "invControlTowerResources_IX_factionID" ON "invControlTowerResources" ("factionID");
CREATE INDEX "invControlTowerResources_IX_purpose" ON "invControlTowerResources" ("purpose");
CREATE INDEX "invControlTowerResources_IX_resourceTypeID" ON "invControlTowerResources" ("resourceTypeID");

INSERT INTO "invControlTowerResources" 
    SELECT  1000000 * "controlTowerTypeID" + "resourceTypeID", 
            "controlTowerTypeID",
            "resourceTypeID",
            "purpose",
            "quantity",
            "minSecurityLevel",
            "factionID"
    FROM "invControlTowerResources_temp";

----------------------------------------------------------
-- DROP UNWANTED TABLES

DROP TABLE "agtAgentTypes";
DROP TABLE "agtAgents";
DROP TABLE "agtResearchAgents";

DROP TABLE "chrAncestries";
DROP TABLE "chrAttributes";
DROP TABLE "chrBloodlines";
DROP TABLE "chrFactions";
DROP TABLE "chrRaces";

DROP TABLE "crpActivities";
DROP TABLE "crpNPCCorporationDivisions";
DROP TABLE "crpNPCCorporationResearchFields";
DROP TABLE "crpNPCCorporationTrades";
DROP TABLE "crpNPCCorporations";
DROP TABLE "crpNPCDivisions";

DROP TABLE "crtCategories";
DROP TABLE "crtCertificates";
DROP TABLE "crtClasses";
DROP TABLE "crtRecommendations";
DROP TABLE "crtRelationships";

DROP TABLE "dgmAttributeCategories";
DROP TABLE "dgmAttributeTypes";
DROP TABLE "dgmEffects";
DROP TABLE "dgmTypeAttributes";
DROP TABLE "dgmTypeEffects";

DROP TABLE "eveGraphics";
DROP TABLE "eveIcons";
DROP TABLE "eveUnits";

-- DROP TABLE "invBlueprintTypes";
-- DROP TABLE "invCategories";
DROP TABLE "invContrabandTypes";
DROP TABLE "invControlTowerResourcePurposes";
-- DROP TABLE "invControlTowerResources";
DROP TABLE "invFlags";
-- DROP TABLE "invGroups";
DROP TABLE "invItems";
-- DROP TABLE "invMarketGroups";
DROP TABLE "invMetaGroups";
DROP TABLE "invMetaTypes";
DROP TABLE "invNames";
DROP TABLE "invPositions";
DROP TABLE "invTypeMaterials";
DROP TABLE "invTypeReactions";
-- DROP TABLE "invTypes";
DROP TABLE "invUniqueNames";

DROP TABLE "mapCelestialStatistics";
DROP TABLE "mapConstellationJumps";
DROP TABLE "mapConstellations";
DROP TABLE "mapDenormalize";
DROP TABLE "mapJumps";
DROP TABLE "mapLandmarks";
DROP TABLE "mapLocationScenes";
DROP TABLE "mapLocationWormholeClasses";
DROP TABLE "mapRegionJumps";
DROP TABLE "mapRegions";
DROP TABLE "mapSolarSystemJumps";
DROP TABLE "mapSolarSystems";
DROP TABLE "mapUniverse";

DROP TABLE "planetSchematics";
DROP TABLE "planetSchematicsPinMap";
DROP TABLE "planetSchematicsTypeMap";

DROP TABLE "ramActivities";
DROP TABLE "ramAssemblyLineStations";
DROP TABLE "ramAssemblyLineTypeDetailPerCategory";
DROP TABLE "ramAssemblyLineTypeDetailPerGroup";
DROP TABLE "ramAssemblyLineTypes";
DROP TABLE "ramAssemblyLines";
DROP TABLE "ramInstallationTypeContents";
DROP TABLE "ramTypeRequirements";

DROP TABLE "staOperationServices";
DROP TABLE "staOperations";
DROP TABLE "staServices";
DROP TABLE "staStationTypes";
DROP TABLE "staStations";

DROP TABLE "translationTables";
DROP TABLE "trnTranslationColumns";
DROP TABLE "trnTranslationLanguages";
DROP TABLE "trnTranslations";

DROP TABLE "warCombatZoneSystems";
DROP TABLE "warCombatZones";

COMMIT;

VACUUM;
