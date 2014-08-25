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

ALTER TABLE `eve_celestialobject` DISABLE KEYS;
ALTER TABLE `eve_blueprintreq` DISABLE KEYS;
ALTER TABLE `eve_blueprinttype` DISABLE KEYS;
ALTER TABLE `eve_controltowerresource` DISABLE KEYS;
ALTER TABLE `eve_marketgroup` DISABLE KEYS;
ALTER TABLE `eve_type` DISABLE KEYS;
ALTER TABLE `eve_group` DISABLE KEYS;
ALTER TABLE `eve_category` DISABLE KEYS;
ALTER TABLE `eve_skillreq` DISABLE KEYS;
SET FOREIGN_KEY_CHECKS = 0;

-- reset existing data
DELETE FROM `eve_celestialobject`;
DELETE FROM `eve_blueprintreq`;
DELETE FROM `eve_blueprinttype`;
DELETE FROM `eve_controltowerresource`;
DELETE FROM `eve_marketgroup`;
DELETE FROM `eve_type`;
DELETE FROM `eve_group`;
DELETE FROM `eve_category`;
DELETE FROM `eve_skillreq`;



INSERT INTO `eve_category` SELECT * FROM `invCategories`;
INSERT INTO `eve_group` SELECT * FROM `invGroups`;
INSERT INTO `eve_marketgroup` SELECT * FROM `invMarketGroups`;

--
-- PATCH invTypes --
--

-- fill the custom table
INSERT INTO `eve_type`
SELECT  t.`typeID`,
        t.`groupID`,
        gg.`categoryID`,
        t.`typeName`,
        b.`blueprintTypeID`,
        b.`techLevel`,
        t.`description`,
        t.`volume`,
        t.`portionSize`,
        t.`raceID`,
        t.`basePrice`,
        t.`marketGroupID`,
        COALESCE(m.`metaGroupID`, 0),
        t.`published`
FROM `invTypes` t LEFT OUTER JOIN `invBlueprintTypes` b ON t.`typeID` = b.`productTypeID`,
     `invTypes` tt LEFT OUTER JOIN `invMetaTypes` m ON tt.`typeID` = m.`typeID`,
     `invGroups` gg
WHERE t.`typeID` = tt.`typeID`
  AND t.`groupID` = gg.`groupID`
  AND t.`typeID` NOT IN (23693) -- this dummy item has 4 different blueprints,
                                -- if we do not ignore it, the SQL command fails...
;

--
-- ADD A dataInterfaceID TO THE invBlueprintTypes TABLE
--

-- fill the new table
INSERT INTO `eve_blueprinttype`(
         `blueprintTypeID`,
         `parentBlueprintTypeID`,
         `productTypeID`,
         `productionTime`,
         `techLevel`,
         `researchProductivityTime`,
         `researchMaterialTime`,
         `researchCopyTime`, 
         `researchTechTime`,
         `productivityModifier`,
         `materialModifier`,
         `wasteFactor`,
         `maxProductionLimit`) 
  SELECT `blueprintTypeID`,
         `parentBlueprintTypeID`,
         `productTypeID`,
         `productionTime`,
         `techLevel`,
         `researchProductivityTime`,
         `researchMaterialTime`,
         `researchCopyTime`, 
         `researchTechTime`,
         `productivityModifier`,
         `materialModifier`,
         `wasteFactor`,
         `maxProductionLimit`
  FROM `invBlueprintTypes`
;


--
-- UPDATE THE parentBlueprintID FIELD IN THE invBlueprintTypes TABLE
-- FOR TECH II ITEMS BILL OF MATERIALS CALCULATION
--

-- we first set all parentBlueprintTypeID to NULL
-- because some are already set to wrong values
UPDATE `eve_blueprinttype`
SET `parentBlueprintTypeID` = NULL;

-- then we get the parent item (for each tech 2 item)
-- from the `invMetaTypes` table and resolve its blueprint.
UPDATE `eve_blueprinttype`
SET `parentBlueprintTypeID` =
(SELECT sub.`bpID` 
FROM (SELECT b.`blueprintTypeID` AS `bpID`, m.`typeID` AS `typeID`
     FROM `eve_blueprinttype` AS b,
          `invMetaTypes` AS m
     WHERE b.`productTypeID` = m.`parentTypeID`
       AND m.`metaGroupID` = 2 /* only tech2 items are concerned with invention */) AS sub
 WHERE `productTypeID` = sub.`typeID`)
;

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
INSERT INTO `eve_blueprintreq`

-- This first sub query will select all basic requirements for manufacturing
-- the quantities gathered here are splitted in 2 categories:
--    `quantity` : ME affected quantity for manufacturing (from invTypeMaterials)
--    `extraQuantity` : Non ME-affected quantity for manufacturing (from ramTypeRequirements)
SELECT
    b.`blueprintTypeID` * 100000000 + itm.`materialTypeID` * 100 + 1 AS `id`,
    b.`blueprintTypeID`,
    1 /* manufacturing */ AS `activityID`,
    itm.`materialTypeID` AS `requiredTypeID`,
    -- we need to hack the data to have correct values on t2 items.
	-- CCP uses the table invTypeMaterials as a reprocessing table. It means that
	-- we need to substract t1 values to the t2 items to get correct requirements.
    itm.`quantity` - COALESCE(itm2.`quantity`, 0) AS `quantity`, -- ME affected
    1.0 AS `damagePerJob`,
    0 AS `extraQuantity` -- not affected by ME

  FROM 
    `invBlueprintTypes` AS b
    JOIN `invTypeMaterials` AS itm
       ON itm.`typeID` = b.`productTypeID`
    LEFT OUTER JOIN `invMetaTypes` AS m
       ON b.`productTypeID` = m.`typeID`
    LEFT OUTER JOIN `invTypeMaterials` AS itm2
       ON itm2.`typeID` = m.`parentTypeID` AND itm2.`materialTypeID` = itm.`materialTypeID`

UNION

-- The second sub-query will gather all other requirements (for manufacturing and other activities)
SELECT
    b.`blueprintTypeID` * 100000000 + rtr.`requiredTypeID` * 100 + rtr.`activityID` AS `id`,
    b.`blueprintTypeID`,
    rtr.`activityID`,
    rtr.`requiredTypeID`,
    0 AS `quantity`, -- these are not affected by ME
    rtr.`damagePerJob`,
    rtr.`quantity` AS `extraQuantity`

  FROM
    `invBlueprintTypes` AS b
    JOIN `ramTypeRequirements` AS rtr
        ON rtr.`typeID` = b.`blueprintTypeID`

  WHERE
    -- to exclude the rows already selected from invTypeMaterials
    NOT EXISTS (SELECT *
         FROM
            `invTypeMaterials` AS itm
         WHERE
            itm.`typeID` = b.`productTypeID`
            AND itm.`materialTypeID` = rtr.`requiredTypeID`)

; -- INSERT

-- on some items, the quantities end up negative. We set them to 0
UPDATE `eve_blueprintreq` SET `quantity` = 0 WHERE `quantity` < 0;

-- Then, remove all useless requirements
DELETE FROM `eve_blueprintreq` WHERE `quantity` = 0 AND `extraQuantity` = 0;

--
-- Add noctis blueprint requirements
INSERT INTO `eve_blueprintreq`
      --     id            bpTypeID activityID reqTypeID   qty    dmg    base
      SELECT 286400003401, 2864,    1,         34,       3349410, 1.0, 936043 -- Tritanium
UNION SELECT 286400003501, 2864,    1,         35,        936043, 1.0, 936043 -- Pyerite
UNION SELECT 286400003601, 2864,    1,         36,        276936, 1.0, 276936 -- Mexallon
UNION SELECT 286400003701, 2864,    1,         37,         50713, 1.0,  50713 -- Isogen
UNION SELECT 286400003801, 2864,    1,         38,         24630, 1.0,  24630 -- Nocxium
UNION SELECT 286400003901, 2864,    1,         39,          3438, 1.0,   3438 -- Zydrine
UNION SELECT 286400004001, 2864,    1,         40,          1580, 1.0,   1580 -- Megacyte
;

-- fill the dataInterfaceID field
UPDATE `eve_blueprinttype`
SET `dataInterfaceID` =
  (SELECT r.`requiredTypeID`
     FROM `eve_blueprintreq` AS r,
          `eve_type` AS t
    WHERE `eve_blueprinttype`.`blueprintTypeID` = r.`blueprintTypeID`
      AND r.`requiredTypeID` = t.`typeID`
      AND r.`activityID` = 8 /* invention */
      AND t.`groupID` = 716 /* data interfaces */)
;

--
-- CREATE A SPECIAL SYSTEMS, MOONS & PLANETS TABLE for quick name resolution

INSERT INTO `eve_celestialobject`
SELECT  `itemID`,
        `typeID`,
        `groupID`,
        `solarSystemID`,
        `regionID`,
        `itemName`,
        `security`,
        `x`,
        `y`,
        `z`
FROM `mapDenormalize`
WHERE `groupID` IN (5 /*Solar System*/, 7 /*Planet*/, 8 /*Moon*/, 15 /*Station*/)
;

UPDATE `eve_celestialobject`
SET `security` =
    (SELECT `mapSolarSystems`.`security`
       FROM `mapSolarSystems`
      WHERE `eve_celestialobject`.`itemID` = `mapSolarSystems`.`solarSystemID`)
WHERE `security` IS NULL
;


--
-- add a unique primary key to the invControlTowerResources table
--
INSERT INTO `eve_controltowerresource` 
    SELECT  1000000 * `controlTowerTypeID` + `resourceTypeID`, 
            `controlTowerTypeID`,
            `resourceTypeID`,
            `purpose`,
            `quantity`,
            `minSecurityLevel`,
            `factionID`
    FROM `invControlTowerResources`
;


--
-- add our enhanced skills reference.
--
INSERT INTO `eve_skillreq`
    SELECT
        t.`typeID` * 100000 + COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) AS `id`,
        t.`typeID` AS `item_id`,
        COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) AS `skill_id`,
        COALESCE(r.`valueInt`, CAST(r.`valueFloat` AS UNSIGNED)) AS `required_level`
    FROM `eve_type` AS t
        JOIN `dgmTypeAttributes` s ON (t.`typeID` = s.`typeID` AND s.`attributeID` = 182)
        JOIN `dgmTypeAttributes` r ON (t.`typeID` = r.`typeID` AND r.`attributeID` = 277)
    WHERE
        t.`published` = 1
      AND
        COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) IN (SELECT `typeID` FROM `eve_type`)
  UNION
    SELECT
        t.`typeID` * 100000 + COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) AS `id`,
        t.`typeID` AS `item_id`,
        COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) AS `skill_id`,
        COALESCE(r.`valueInt`, CAST(r.`valueFloat` AS UNSIGNED)) AS `required_level`
    FROM `eve_type` AS t
        JOIN `dgmTypeAttributes` s ON (t.`typeID` = s.`typeID` AND s.`attributeID` = 183)
        JOIN `dgmTypeAttributes` r ON (t.`typeID` = r.`typeID` AND r.`attributeID` = 278)
    WHERE
        t.`published` = 1
      AND
        COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) IN (SELECT `typeID` FROM `eve_type`)
  UNION
    SELECT
        t.`typeID` * 100000 + COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) AS `id`,
        t.`typeID` AS `item_id`,
        COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) AS `skill_id`,
        COALESCE(r.`valueInt`, CAST(r.`valueFloat` AS UNSIGNED)) AS `required_level`
    FROM `eve_type` AS t
        JOIN `dgmTypeAttributes` s ON (t.`typeID` = s.`typeID` AND s.`attributeID` = 184)
        JOIN `dgmTypeAttributes` r ON (t.`typeID` = r.`typeID` AND r.`attributeID` = 279)
    WHERE
        t.`published` = 1
      AND
        COALESCE(s.`valueInt`, CAST(s.`valueFloat` AS UNSIGNED)) IN (SELECT `typeID` FROM `eve_type`)
;




--
ALTER TABLE `eve_celestialobject` ENABLE KEYS;
ALTER TABLE `eve_blueprintreq` ENABLE KEYS;
ALTER TABLE `eve_blueprinttype` ENABLE KEYS;
ALTER TABLE `eve_controltowerresource` ENABLE KEYS;
ALTER TABLE `eve_marketgroup` ENABLE KEYS;
ALTER TABLE `eve_type` ENABLE KEYS;
ALTER TABLE `eve_group` ENABLE KEYS;
ALTER TABLE `eve_category` ENABLE KEYS;
ALTER TABLE `eve_skillreq` ENABLE KEYS;
SET FOREIGN_KEY_CHECKS = 1;

COMMIT;

