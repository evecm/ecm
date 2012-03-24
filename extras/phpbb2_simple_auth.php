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
 * PHPBB2 synchronization script for ECM
 *
 * Please read http://code.google.com/p/eve-corp-management/wiki/ExternalAppsSync
 * for installation instructions.
 *
 * It accepts a HTTP POST request with 2 parameters 'username' and 'password'
 * It looks in PHPBB's user table if the username exists. Then it checks if passwords match.
 * If the passwords match, the script returns a HTTP 200 OK response containing the 'user_id'
 *
 * If the user does not exist or if the passwords don't match, it returns an empty HTTP 200 response.
 * If there is an error accessing the DB, a HTTP 500 error is returned.
 ******************************************************************************/

define("IN_LOGIN", true);

define('IN_PHPBB', true);
$phpbb_root_path = './';
include($phpbb_root_path . 'extension.inc');
include($phpbb_root_path . 'common.'.$phpEx);

$username = isset($HTTP_POST_VARS['username']) ? phpbb_clean_username($HTTP_POST_VARS['username']) : '';
$password = isset($HTTP_POST_VARS['password']) ? $HTTP_POST_VARS['password'] : '';

$sql = "SELECT `user_id`, `username`, `user_password`
        FROM " . USERS_TABLE . "
        WHERE username = '" . str_replace("\\'", "''", $username) . "'";

if ( !($result = $db->sql_query($sql)) ) {
    header('HTTP/1.1 500 Internal Server Error');
    message_die(GENERAL_ERROR, 'Error in obtaining userdata', '', __LINE__, __FILE__, $sql);
}

if( $row = $db->sql_fetchrow($result) ) {
    if( md5($password) == $row['user_password'] ) {
        /* authentication successful */
        echo $row['user_id'];
    }
}
?>
