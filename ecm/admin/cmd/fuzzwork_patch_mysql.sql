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


INSERT INTO `eve_category`
          (`categoryID`, `categoryName`, `description`, `iconID`, `published`)
    SELECT `categoryID`, `categoryName`, `description`, `iconID`, `published`
    FROM `invCategories`;
INSERT INTO `eve_group`
          (`groupID`, `categoryID`, `groupName`, `description`, `iconID`, `useBasePrice`, `allowManufacture`, `allowRecycler`, `anchored`, `anchorable`, `fittableNonSingleton`, `published`)
    SELECT `groupID`, `categoryID`, `groupName`, `description`, `iconID`, `useBasePrice`, `allowManufacture`, `allowRecycler`, `anchored`, `anchorable`, `fittableNonSingleton`, `published`
    FROM `invGroups`;
INSERT INTO `eve_marketgroup`
          (`marketGroupID`, `parentGroupID`, `marketGroupName`, `description`, `iconID`, `hasTypes`)
    SELECT `marketGroupID`, `parentGroupID`, `marketGroupName`, `description`, `iconID`, `hasTypes`
    FROM `invMarketGroups`;

--
-- PATCH invTypes --
--

-- fill the custom table
-- TODO remove techLevel
INSERT INTO `eve_type`
    ( `typeID`, `groupID`, `categoryID`, `typeName`, `blueprintTypeID`, `description`, `volume`, `portionSize`,
    `raceID`, `basePrice`, `marketGroupID`, `metaGroupID`, `published`)
    SELECT  t.`typeID`,
        t.`groupID`,
        g.`categoryID`,
        t.`typeName`,
        iap.`typeID` AS `blueprintTypeID`,
        t.`description`,
        t.`volume`,
        t.`portionSize`,
        t.`raceID`,
        t.`basePrice`,
        t.`marketGroupID`,
        COALESCE(m.`metaGroupID`, 0),
        t.`published`
    FROM `invTypes` t
    LEFT OUTER JOIN `industryActivityProducts` iap ON t.`typeID` = iap.`productTypeID` AND iap.`activityID` = 1
    LEFT OUTER JOIN `invMetaTypes` m ON t.`typeID` = m.`typeID`
    LEFT OUTER JOIN `invGroups` g ON t.`groupID` = g.`groupID`
;

--
-- Fill in eve_blueprinttype table
--
INSERT INTO `eve_blueprinttype`
    (`blueprintTypeID`, `productTypeID`, `productionTime`, `researchProductivityTime`,
    `researchMaterialTime`, `researchCopyTime`, `maxProductionLimit`, `inventionTime`)
    SELECT  bp.`typeID` AS `blueprintTypeID`,
            p.`productTypeID`,
            prTime.`time` AS `productionTime`,
            teTime.`time` AS `researchProductivityTime`,
            meTime.`time` AS `researchMaterialTime`,
            cpTime.`time` AS `researchCopyTime`, 
            bp.`maxProductionLimit`,
            ivTime.`time` AS `inventionTime`
    FROM `industryBlueprints` bp
    LEFT JOIN `industryActivity`    prTime ON bp.`typeID` = prTime.`typeID` AND prTime.`activityID` = 1
    LEFT JOIN `industryActivity`    teTime ON bp.`typeID` = teTime.`typeID` AND teTime.`activityID` = 3
    LEFT JOIN `industryActivity`    meTime ON bp.`typeID` = meTime.`typeID` AND meTime.`activityID` = 4
    LEFT JOIN `industryActivity`    cpTime ON bp.`typeID` = cpTime.`typeID` AND cpTime.`activityID` = 5
    LEFT JOIN `industryActivity`    ivTime ON bp.`typeID` = ivTime.`typeID` AND ivTime.`activityID` = 8
    LEFT JOIN `industryActivityProducts` p ON bp.`typeID` = p.`typeID` AND p.`activityID` = 1
;

--
-- UPDATE THE parentBlueprintID FIELD IN THE eve_blueprinttype TABLE for TechII items
--
UPDATE `eve_blueprinttype` bpt
    JOIN `eve_type` t ON t.`typeID` = bpt.`productTypeID` AND t.`metaGroupID` = 2 
    JOIN `industryActivityProducts` bp ON bp.`productTypeID` = bpt.`blueprintTypeID`
    SET bpt.`parentBlueprintTypeID` = bp.`typeID`;
    
-- UPDATE the inventionBaseChance field for blueprints that can invent
-- Blueprints can invent multiple things, but, the probability should be the same.
UPDATE `eve_blueprinttype` bpt
    JOIN `industryActivityProbabilities` prob ON bpt.`blueprintTypeID` = prob.`typeID`
    SET bpt.`inventionBaseChance` = prob.`probability`;

--
-- CUSTOM blueprints requirements table with primary key --
--
INSERT INTO `eve_blueprintreq`
    (`id`, `blueprintTypeID`, `activityID`, `requiredTypeID`, `quantity`)
    SELECT
        m.`typeID` * 100000000 + m.`materialTypeID` * 100 + m.`activityID` AS `id`,
        m.`typeID` AS `blueprintTypeID`,
        m.`activityID`,
        m.`materialTypeID` AS `requiredTypeID`,
        m.`quantity`
    FROM 
        `industryActivityMaterials` m
;

--
-- CREATE A SPECIAL SYSTEMS, MOONS & PLANETS TABLE for quick name resolution

INSERT INTO `eve_celestialobject`
      (`itemID`, `typeID`, `groupID`, `solarSystemID`, `regionID`, `itemName`, `security`, `x`, `y`, `z`)
SELECT `itemID`, `typeID`, `groupID`, `solarSystemID`, `regionID`, `itemName`, `security`, `x`, `y`, `z`
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
    (`id`, `controlTowerTypeID`, `resourceTypeID`, `purpose`, `quantity`, `minSecurityLevel`, `factionID`)
    SELECT  1000000 * `controlTowerTypeID` + `resourceTypeID`,
            `controlTowerTypeID`, `resourceTypeID`, `purpose`, `quantity`, `minSecurityLevel`, `factionID`
    FROM `invControlTowerResources`
;

--
-- add our enhanced skills reference.
--
INSERT INTO `eve_skillreq` (`id`, `item_id`, `skill_id`, `required_level`)
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

-- DROP the EVE SDE tables now that we've converted them
DROP TABLE `invTypes`;
DROP TABLE `invCategories`;
DROP TABLE `invGroups`;
DROP TABLE `invMarketGroups`;
DROP TABLE `invMetaTypes`;
DROP TABLE `invControlTowerResources`;
DROP TABLE `mapDenormalize`;
DROP TABLE `mapSolarSystems`;
DROP TABLE `dgmTypeAttributes`;
DROP TABLE `industryBlueprints`;
DROP TABLE `industryActivity`;
DROP TABLE `industryActivityProducts`;
DROP TABLE `industryActivityMaterials`;
DROP TABLE `industryActivityProbabilities`;

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

