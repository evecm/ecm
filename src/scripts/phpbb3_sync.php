<?php
/*
* Copyright (c) 2010-2011 Robin Jarry
*
* This file is part of EVE Corporation Management.
*
* EVE Corporation Management is free software: you can redistribute it and/or
* modify it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or (at your
* option) any later version.
*
* EVE Corporation Management is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
* or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
* more details.
*
* You should have received a copy of the GNU General Public License along with
* EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.
*/

/******************************************************************************
 * PHPBB3 synchronization script for ECM
*
* Please read http://code.google.com/p/eve-corp-management/wiki/ExternalAppsSync
* for installation instructions.
*
* This script is to be run with the php CLI. the "php-curl" package is required.
*
* It will perform the followning tasks:
*
* 	- Request ECM managed groups for the forum
* 	- Get the members that are to be put in these groups
* 	- Update these groups members according to what ECM says
*
* IMPORTANT : do not put this script next to your forum files. Instead, put
* it in a global "admin" scripts folder so that users cannot see or run it by
* mistake.
*
* If you want to run this script periodically (which is pretty much the point ^^)
* The crontab entry should look that way:
*
* 0 * * * * /usr/bin/php -f /root/scripts/phpbb3_sync.php 2>&1 1>>/some/file.log
******************************************************************************/

/*****************************************************************************/
/* CONFIGURATION */
define('ECM_URL',			'http://ecm.yourserver.com');
define('ECM_USER',			'cron');
define('ECM_PASSWORD',		'cron');
define('ECM_EXTERNAL_APP',	'forum');
define('PHPBB_ROOT_PATH',	'/home/sites/forum/');
/*****************************************************************************/

define('IN_PHPBB', true);

$phpbb_root_path = (defined('PHPBB_ROOT_PATH')) ? PHPBB_ROOT_PATH : './';
$phpEx = substr(strrchr(__FILE__, '.'), 1);

include(PHPBB_ROOT_PATH . 'common.' . $phpEx);
include(PHPBB_ROOT_PATH . 'includes/functions_user.' . $phpEx);

/*****************************************************************************/

/**
* Log some text to the console
*
* @param string $text
*/
function logln($text) {
    echo date("Ymd - H:i:s") . " - $text\n";
}


/**
 * Update a phpbb3 group
 *
 * @param int $group_id
 * @param array:int $members_to_remove
 * @param array:int $members_to_add
 */
function update_group($group_id, $members_to_remove, $members_to_add)
{
    if (sizeof($members_to_remove)) {
        $err = group_user_del($group_id, $members_to_remove);
        if ($err) {
            logln("[ERROR] could not remove members: $err");
        } else {
            logln("Removed " . sizeof($members_to_remove)
               . " members: " . implode(', ', $members_to_remove));
        }
    }
    if (sizeof($members_to_add)) {
        $err = group_user_add($group_id, $members_to_add);
        if ($err) {
            logln("[ERROR] could not add members: $err");
        } else {
            logln("Added " . sizeof($members_to_add)
                . " members: " . implode(', ', $members_to_add));
        }
    }
}


/**
 * Get current group members
 *
 * @param int $group_id
 * @return array:int group members
 */
function get_group_members($group_id)
{
    global $db;

    $sql = "SELECT user_id
        FROM " . USER_GROUP_TABLE . "
        WHERE group_id = $group_id";
    $result = $db->sql_query($sql);

    $user_ids = array();
    while ($row = $db->sql_fetchrow($result))
    {
        $user_ids[] = (int) $row['user_id'];
    }
    $db->sql_freeresult($result);

    return $user_ids;
}


/**
 * Get data from ECM and convert it from JSON to a php array
 *
 * @param string $url
 * @return array json decoded data
 */
function fetch_ecm_data($url)
{
    $ch = curl_init();
    curl_setopt_array($ch, array(
        CURLOPT_USERAGENT      => 'ECM PHPBB3 Synchronizer',
        CURLOPT_URL            => $url,
        CURLOPT_HTTPAUTH       => CURLAUTH_BASIC,
        CURLOPT_USERPWD        => ECM_USER . ":" . ECM_PASSWORD,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_AUTOREFERER    => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS      => 10,
    ));

    $content = curl_exec($ch);
    $response = curl_getinfo($ch);
    $error = curl_errno($ch);
    curl_close($ch);

    if ($error) {
        die("URL \"$url\" responded HTTP error: " . var_dump($response));
    } else {
        return json_decode($content, true);
    }
}


/**
 * Update permissions according to what ECM says.
 */
function main()
{
    $url = ECM_URL . '/api/bindings/' . ECM_EXTERNAL_APP . '/groups';
    logln("Fetching data from $url...");
    $groups = fetch_ecm_data($url);
    logln("Fetched " . sizeof($groups) . " groups");

    foreach ($groups as $g) {
        $group_id = (int) $g['group'];
        logln("Updating group $group_id...");
        $new_members = $g['members'];
        $old_members = get_group_members($group_id);

        $members_to_remove = array_diff($old_members, $new_members);
        $members_to_add = array_diff($new_members, $old_members);

        update_group($group_id, $members_to_remove, $members_to_add);
    }
}


main();

?>
