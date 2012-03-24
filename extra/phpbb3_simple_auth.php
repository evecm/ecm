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
 * It accepts a HTTP POST request with 2 parameters 'username' and 'password'
 * It looks in PHPBB's user table if the username exists. Then it checks if
 * passwords match.
 * If the passwords match, the script returns a HTTP 200 OK response containing
 * the 'user_id'
 *
 * If the user does not exist or if the passwords don't match, it returns an
 * empty HTTP 200 response.
 * If there is an error accessing the DB, a HTTP 500 error is returned.
 ******************************************************************************/


define('IN_PHPBB', true);

$phpbb_root_path = (defined('PHPBB_ROOT_PATH')) ? PHPBB_ROOT_PATH : './';
$phpEx = substr(strrchr(__FILE__, '.'), 1);

include($phpbb_root_path . 'common.' . $phpEx);

define("IN_LOGIN", true);

// Basic parameter data
$username = request_var('username', '');
$password = request_var('password', '');

$result = $auth->login($username, $password);

if ( !$result ) {
    header('HTTP/1.1 500 Internal Server Error');
    message_die(GENERAL_ERROR, 'Error in obtaining userdata', '', __LINE__, __FILE__, '');
}

if( $result['status'] == LOGIN_SUCCESS ) {
    echo $result['user_row']['user_id'];
}
?>
