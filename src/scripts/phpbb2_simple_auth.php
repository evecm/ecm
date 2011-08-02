<?php

define("IN_LOGIN", true);

define('IN_PHPBB', true);
$phpbb_root_path = './';
include($phpbb_root_path . 'extension.inc');
include($phpbb_root_path . 'common.'.$phpEx);

$username = isset($HTTP_POST_VARS['username']) ? phpbb_clean_username($HTTP_POST_VARS['username']) : '';
$password = isset($HTTP_POST_VARS['password']) ? $HTTP_POST_VARS['password'] : '';

$sql = "SELECT `user_id`, `username`, `user_password`, `user_active`
        FROM " . USERS_TABLE . "
        WHERE username = '" . str_replace("\\'", "''", $username) . "'";

if ( !($result = $db->sql_query($sql)) ) {
    header('HTTP/1.1 500 Internal Server Error');
    message_die(GENERAL_ERROR, 'Error in obtaining userdata', '', __LINE__, __FILE__, $sql);
}

if( $row = $db->sql_fetchrow($result) ) {
    if( md5($password) == $row['user_password'] && $row['user_active'] ) {
        // authentication successful
        echo $row['user_id'];
    }
}
?>
