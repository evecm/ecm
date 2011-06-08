
------------------------------------------
-- CUSTOM blueprints requirements table --
------------------------------------------
CREATE TABLE ramBlueprintReqs (
    blueprintTypeID SMALLINT,
    activityID TINYINT UNSIGNED,
    requiredTypeID SMALLINT,
    quantity INT,
    damagePerJob DOUBLE,
    baseMaterial INT,
    CONSTRAINT materials_PK PRIMARY KEY (blueprintTypeID, activityID, requiredTypeID)
);

-- The following queries take invTypeMaterials and ramTypeRequirements and combine them 
-- into a single table showing all the materials a blueprint requires, and how much of each 
-- material is affected by waste when building.
-------------------------------------------------------
INSERT INTO ramBlueprintReqs(blueprintTypeID,
                             activityID,
                             requiredTypeID,
                             quantity,
                             damagePerJob,
                             baseMaterial)
    SELECT  rtr.typeID,
            rtr.activityID,
            rtr.requiredTypeID,
            (rtr.quantity + IFNULL(itm.quantity, 0)),
            rtr.damagePerJob,
            itm.quantity
    FROM invBlueprintTypes AS b
       INNER JOIN ramTypeRequirements AS rtr
           ON rtr.typeID = b.blueprintTypeID
          AND rtr.activityID = 1
       LEFT OUTER JOIN invTypeMaterials AS itm
           ON itm.typeID = b.productTypeID
          AND itm.materialTypeID = rtr.requiredTypeID
    WHERE rtr.quantity > 0;
----------------------------------------------------------
INSERT INTO ramBlueprintReqs(blueprintTypeID, 
                             activityID, 
                             requiredTypeID, 
                             quantity, 
                             damagePerJob, 
                             baseMaterial) 
    SELECT  b.blueprintTypeID, 
            1, 
            itm.materialTypeID, 
            (itm.quantity - IFNULL(sub.quantity * sub.recycledQuantity, 0)), 
            1, 
            (itm.quantity - IFNULL(sub.quantity * sub.recycledQuantity, 0)) 
    FROM invBlueprintTypes AS b 
       INNER JOIN invTypeMaterials AS itm 
           ON itm.typeID = b.productTypeID 
       LEFT OUTER JOIN ramBlueprintReqs m 
           ON b.blueprintTypeID = m.blueprintTypeID 
           AND m.requiredTypeID = itm.materialTypeID 
       LEFT OUTER JOIN ( 
           SELECT srtr.typeID AS blueprintTypeID, 
                  sitm.materialTypeID AS recycledTypeID, 
                  srtr.quantity AS recycledQuantity, 
                  sitm.quantity 
           FROM ramTypeRequirements AS srtr 
               INNER JOIN invTypeMaterials AS sitm 
                   ON srtr.requiredTypeID = sitm.typeID 
           WHERE srtr.recycle = 1 
             AND srtr.activityID = 1 
       ) AS sub 
           ON sub.blueprintTypeID = b.blueprintTypeID 
           AND sub.recycledTypeID = itm.materialTypeID 
    WHERE m.blueprintTypeID IS NULL 
    AND (itm.quantity - IFNULL(sub.quantity * sub.recycledQuantity, 0)) > 0;
----------------------------------------------------------
INSERT INTO ramBlueprintReqs(blueprintTypeID, 
                             activityID, 
                             requiredTypeID, 
                             quantity, 
                             damagePerJob) 
    SELECT  rtr.typeID, 
            rtr.activityID,
            rtr.requiredTypeID, 
            rtr.quantity, 
            rtr.damagePerJob 
    FROM ramTypeRequirements AS rtr 
    WHERE rtr.activityID NOT IN (1);

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
CREATE TABLE "invTypes" (
  "typeID" int(11) NOT NULL,
  "groupID" smallint(6) DEFAULT NULL,
  "typeName" varchar(100) DEFAULT NULL,
  "description" varchar(3000) DEFAULT NULL,
  "volume" double DEFAULT NULL,
  "portionSize" int(11) DEFAULT NULL,
  "basePrice" double DEFAULT NULL,
  "marketGroupID" smallint(6) DEFAULT NULL,
  "icon" varchar(32) DEFAULT NULL,
  "metaGroupID" smallint(6) DEFAULT NULL,
  PRIMARY KEY ("typeID")
);

CREATE INDEX "invTypes_IX_Group" ON "invTypes" ("groupID");
CREATE INDEX "invTypes_IX_iconID" ON "invTypes" ("icon");
CREATE INDEX "invTypes_IX_marketGroupID" ON "invTypes" ("marketGroupID");
CREATE INDEX "invTypes_IX_metaGroupID" ON "invTypes" ("metaGroupID");

-- fill the custom table
INSERT INTO "invTypes_ecm"
SELECT  t."typeID", 
        t."groupID", 
        t."typeName", 
        t."description", 
        t."volume", 
        t."portionSize", 
        t."basePrice", 
        t."marketGroupID", 
        IFNULL('icon' || g."iconFile", CAST(t."typeID" AS TEXT)) AS "icon", 
        m."metaGroupID" AS "metaGroupID"
FROM "invTypes" t LEFT OUTER JOIN "eveIcons" g ON t."graphicID" = g."iconID",
     "invTypes" t2 LEFT OUTER JOIN "invMetaTypes" m ON t."typeID" = m."typeID"
WHERE t."typeID" = t2."typeID"
AND t."published" = 1;

-- update the T2 blueprints marketGroups
UPDATE "invTypes"
SET "marketGroupID" = ( SELECT t2."marketGroupID"
        FROM "invBlueprintTypes" b1, "invBlueprintTypes" b2, "invMetaTypes" m, "invTypes" t2
        WHERE "invTypes"."groupID" IN (SELECT "groupID" FROM "invGroups" WHERE "categoryID" = 9)
          AND "invTypes"."marketGroupID" IS NULL
          AND "invTypes"."typeID" = b1."blueprintTypeID"
          AND m."typeID" = b1."productTypeID"
          AND m."parentTypeID" = b2."productTypeID"
          AND t2."typeID" = b2."blueprintTypeID" )
WHERE "invTypes"."marketGroupID" IS NULL
AND EXISTS ( SELECT *
        FROM "invBlueprintTypes" b1, "invBlueprintTypes" b2, "invMetaTypes" m, "invTypes" t2
        WHERE "invTypes"."groupID" IN (SELECT "groupID" FROM "invGroups" WHERE "categoryID" = 9)
          AND "invTypes"."marketGroupID" IS NULL
          AND "invTypes"."typeID" = b1."blueprintTypeID"
          AND m."typeID" = b1."productTypeID"
          AND m."parentTypeID" = b2."productTypeID"
          AND t2."typeID" = b2."blueprintTypeID" );


----------------------------------------------------------
-- DROP UNWANTED TABLES

DROP TABLE "agtAgentTypes";
DROP TABLE "agtAgents";
DROP TABLE "agtConfig";
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
DROP TABLE "eveLocations";
DROP TABLE "eveNames";
DROP TABLE "eveOwners";
DROP TABLE "eveUnits";

-- DROP TABLE "invBlueprintTypes";
-- DROP TABLE "invCategories";
DROP TABLE "invContrabandTypes";
-- DROP TABLE "invControlTowerResourcePurposes";
-- DROP TABLE "invControlTowerResources";
-- DROP TABLE "invFlags";
-- DROP TABLE "invGroups";
DROP TABLE "invItems";
-- DROP TABLE "invMarketGroups";
-- DROP TABLE "invMetaGroups";
-- DROP TABLE "invMetaTypes";
-- DROP TABLE "invTypeMaterials";
-- DROP TABLE "invTypeReactions";
-- DROP TABLE "invTypes";

-- DROP TABLE "mapCelestialStatistics";
-- DROP TABLE "mapConstellationJumps";
-- DROP TABLE "mapConstellations";
DROP TABLE "mapDenormalize";
-- DROP TABLE "mapJumps";
-- DROP TABLE "mapLandmarks";
-- DROP TABLE "mapLocationScenes";
-- DROP TABLE "mapLocationWormholeClasses";
-- DROP TABLE "mapRegionJumps";
-- DROP TABLE "mapRegions";
-- DROP TABLE "mapSolarSystemJumps";
DROP TABLE "mapSolarSystems";
-- DROP TABLE "mapUniverse";

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
-- DROP TABLE "staStationTypes";
-- DROP TABLE "staStations";

DROP TABLE "trnTranslationColumns";
DROP TABLE "trnTranslations";





