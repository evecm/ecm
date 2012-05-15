BEGIN;

INSERT INTO "main"."eve_category"               SELECT * FROM "eve"."invCategories";
INSERT INTO "main"."eve_group"                  SELECT * FROM "eve"."invGroups";
INSERT INTO "main"."eve_controltowerresource"   SELECT * FROM "eve"."invControlTowerResources";
INSERT INTO "main"."eve_marketgroup"            SELECT * FROM "eve"."invMarketGroups";
INSERT INTO "main"."eve_blueprinttype"          SELECT * FROM "eve"."invBlueprintTypes";
INSERT INTO "main"."eve_type"                   SELECT * FROM "eve"."invTypes";
INSERT INTO "main"."eve_blueprintreq"           SELECT * FROM "eve"."ramBlueprintReqs";
INSERT INTO "main"."eve_celestialobject"        SELECT * FROM "eve"."mapCelestialObjects";

COMMIT;
