-- Copyright (c) 2010-2014 AUTHORS
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

-- reset existing data
DELETE FROM "eve_celestialobject";
DELETE FROM "eve_blueprintreq";
DELETE FROM "eve_blueprinttype";
DELETE FROM "eve_controltowerresource";
DELETE FROM "eve_marketgroup";
DELETE FROM "eve_type";
DELETE FROM "eve_group";
DELETE FROM "eve_category";
DELETE FROM "eve_skillreq";



INSERT INTO "eve_category" SELECT "categoryID","categoryName","description","iconID","published" FROM "invCategories";
INSERT INTO "eve_group" SELECT "groupID","categoryID","groupName","description","iconID","useBasePrice","allowManufacture",
	"allowRecycler","anchored","anchorable","fittableNonSingleton" FROM "invGroups";
INSERT INTO "eve_marketgroup" SELECT "marketGroupID","parentGroupID","marketGroupName","description","iconID","hasTypes" FROM "invMarketGroups";

--
-- PATCH invTypes --
--

-- fill the custom table
INSERT INTO "eve_type"
SELECT  t."typeID",
        t."groupID",
        gg."categoryID",
        t."typeName",
        b."blueprintTypeID",
        b."techLevel",
        t."description",
        t."volume",
        t."portionSize",
        t."raceID",
        t."basePrice",
        t."marketGroupID",
        COALESCE(m."metaGroupID", 0),
        t."published"
FROM "invTypes" t LEFT OUTER JOIN "invBlueprintTypes" b ON t."typeID" = b."productTypeID",
     "invTypes" tt LEFT OUTER JOIN "invMetaTypes" m ON tt."typeID" = m."typeID",
     "invGroups" gg
WHERE t."typeID" = tt."typeID"
  AND t."groupID" = gg."groupID"
  AND t."typeID" NOT IN (23693) -- this dummy item has 4 different blueprints,
                                -- if we do not ignore it, the SQL command fails...
;

--
-- Fill in eve_blueprinttype table
--
INSERT INTO "eve_blueprinttype"(
         "blueprintTypeID",
         "productTypeID",
         "productionTime",
         "researchProductivityTime",
         "researchMaterialTime",
         "researchCopyTime", 
         "inventionTime",
         "maxProductionLimit") 
  SELECT "blueprintTypeID",
         "productTypeID",
         "productionTime",
         "researchProductivityTime",
         "researchMaterialTime",
         "researchCopyTime", 
         "inventionTime",
         "maxProductionLimit"
  FROM "invBlueprintTypes"
;


--
-- UPDATE THE parentBlueprintID FIELD IN THE invBlueprintTypes TABLE
-- FOR TECH II ITEMS BILL OF MATERIALS CALCULATION
--
-- then we get the parent item (for each tech 2 item)
-- from the `invMetaTypes` table and resolve its blueprint.
CREATE TEMPORARY TABLE "temp_bp_table"("blueprintTypeID" INT, "parentID" INT);
INSERT INTO "temp_bp_table"
	SELECT b."blueprintTypeID" AS "blueprintTypeID", m."parentTypeID" AS "parentID"
    FROM "eve_blueprinttype" AS b,
         "invMetaTypes" AS m
    WHERE b."productTypeID" = m."typeID" AND m."metaGroupID" = 2;

UPDATE "eve_blueprinttype"
SET "parentBlueprintTypeID" =
	(SELECT t1bp."blueprintTypeID"
		FROM "temp_bp_table" AS tbpt,
			 "invBlueprintTypes" AS t1bp
		WHERE tbpt."parentID" = t1bp."productTypeID" AND "eve_blueprinttype"."blueprintTypeID" = tbpt."blueprintTypeID");

-- this way, when manufacturing a tech 2 item,
-- we can easily know on which blueprint we need to run an invention job
-- in order to obtain the item's tech 2 BPC

--
-- CUSTOM blueprints requirements table --
--
-- The following queries take invTypeMaterials and ramTypeRequirements and combine them
-- into a single table showing all the materials a blueprint requires, and how much of each
-- material is affected by waste when building.
--
INSERT INTO "eve_blueprintreq" ("id", "blueprintTypeID", "activityID", "requiredTypeID", "quantity")

SELECT
    CAST(b."blueprintTypeID" AS bigint) * 100000000 + CAST(rtr."requiredTypeID" AS bigint) * 100 + CAST(rtr."activityID" AS bigint) AS "id",
    b."blueprintTypeID",
    rtr."activityID",
    rtr."requiredTypeID",
    rtr."quantity"			-- ME affected

  FROM
	"invBlueprintTypes" AS b
    JOIN "ramTypeRequirements" AS rtr ON b."blueprintTypeID" = rtr."typeID"
  WHERE
	rtr."quantity" > 0

-- Remove rows with invalid requiredTypeID fields
DELETE FROM "eve_blueprintreq" WHERE "requiredTypeID" NOT IN (SELECT "typeID" from "eve_type");

-- fill the dataInterfaceID field
UPDATE "eve_blueprinttype"
SET "dataInterfaceID" =
  (SELECT r."requiredTypeID"
     FROM "eve_blueprintreq" AS r,
          "eve_type" AS t
    WHERE "eve_blueprinttype"."blueprintTypeID" = r."blueprintTypeID"
      AND r."requiredTypeID" = t."typeID"
      AND r."activityID" = 8 /* invention */
      AND t."groupID" = 716 /* data interfaces */)
;

--
-- CREATE A SPECIAL SYSTEMS, MOONS & PLANETS TABLE for quick name resolution

INSERT INTO "eve_celestialobject"
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

UPDATE "eve_celestialobject"
SET "security" =
    (SELECT "mapSolarSystems"."security"
       FROM "mapSolarSystems"
      WHERE "eve_celestialobject"."itemID" = "mapSolarSystems"."solarSystemID")
WHERE "security" IS NULL
;


--
-- add a unique primary key to the invControlTowerResources table
--
INSERT INTO "eve_controltowerresource" 
    SELECT  1000000 * CAST("controlTowerTypeID" AS bigint) + CAST("resourceTypeID" AS bigint), 
            "controlTowerTypeID",
            "resourceTypeID",
            "purpose",
            "quantity",
            "minSecurityLevel",
            "factionID"
    FROM "invControlTowerResources"
;


--
-- add our enhanced skills reference.
--
INSERT INTO "eve_skillreq"
    SELECT
        CAST(t."typeID" AS BIGINT) * 100000 + CAST(COALESCE(s."valueInt", s."valueFloat") AS BIGINT) AS "id",
        t."typeID" AS "item_id",
        COALESCE(s."valueInt", CAST(s."valueFloat" AS INT)) AS "skill_id",
        COALESCE(r."valueInt", CAST(r."valueFloat" AS INT)) AS "required_level"
    FROM "eve_type" AS t
        JOIN "dgmTypeAttributes" s ON (t."typeID" = s."typeID" AND s."attributeID" = 182)
        JOIN "dgmTypeAttributes" r ON (t."typeID" = r."typeID" AND r."attributeID" = 277)
    WHERE
        t."published" = 1
      AND
        COALESCE(s."valueInt", CAST(s."valueFloat" AS INT)) IN (SELECT "typeID" FROM "eve_type")
  UNION
    SELECT
        CAST(t."typeID" AS BIGINT) * 100000 + CAST(COALESCE(s."valueInt", s."valueFloat") AS BIGINT) AS "id",
        t."typeID" AS "item_id",
        COALESCE(s."valueInt", CAST(s."valueFloat" AS INT)) AS "skill_id",
        COALESCE(r."valueInt", CAST(r."valueFloat" AS INT)) AS "required_level"
    FROM "eve_type" AS t
        JOIN "dgmTypeAttributes" s ON (t."typeID" = s."typeID" AND s."attributeID" = 183)
        JOIN "dgmTypeAttributes" r ON (t."typeID" = r."typeID" AND r."attributeID" = 278)
    WHERE
        t."published" = 1
      AND
        COALESCE(s."valueInt", CAST(s."valueFloat" AS INT)) IN (SELECT "typeID" FROM "eve_type")
  UNION
    SELECT
        CAST(t."typeID" AS BIGINT) * 100000 + CAST(COALESCE(s."valueInt", s."valueFloat") AS BIGINT) AS "id",
        t."typeID" AS "item_id",
        COALESCE(s."valueInt", CAST(s."valueFloat" AS INT)) AS "skill_id",
        COALESCE(r."valueInt", CAST(r."valueFloat" AS INT)) AS "required_level"
    FROM "eve_type" AS t
        JOIN "dgmTypeAttributes" s ON (t."typeID" = s."typeID" AND s."attributeID" = 184)
        JOIN "dgmTypeAttributes" r ON (t."typeID" = r."typeID" AND r."attributeID" = 279)
    WHERE
        t."published" = 1
      AND
        COALESCE(s."valueInt", CAST(s."valueFloat" AS INT)) IN (SELECT "typeID" FROM "eve_type")
;




COMMIT;

