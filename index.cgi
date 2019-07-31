#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

@links = (
  'admin_main.cgi',
  'interface_main.cgi',
  'module_config_main.cgi',
  'module_info_main.cgi',
  'help_main.cgi',
  'send_main.cgi'
);

@titles = (
  $text{'LINK_ADMIN_PAGE'},
  $text{'LINK_INTERFACE_PAGE'},
  $text{'LINK_MODULE_CONFIG_PAGE'},
  $text{'LINK_MODULE_INFO_PAGE'},
  $text{'LINK_HELP_PAGE'},
  $text{'LINK_SEND_PAGE'}
);

@icons = (
  'images/admin.png',
  'images/interface.png',
  'images/module_config.png',
  'images/module_info.png',
  'images/help.png',
  'images/send.png'
);

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, 'index', 1, 1, 0, undef, undef, undef, "<img src='images/icon.gif'/><br/><a href=\"https://wbmtranslator.esaracco.fr\" target=\"_BLANK\">$text{'PROJECT_HOMEPAGE'}</a>&nbsp;|&nbsp;<a href=\"http://download.webmin.com/devel/tarballs/\" target=\"_BLANK\">$text{'LATEST_WEBMIN'}</a>");
&trans_header_extra ();
&trans_main_check_config ();
&trans_check_perl_deps ();

# Warn user when a new wbmclamav release is available
if ($ENV{'HTTP_REFERER'} !~ /$module_name\/[a-z]/i &&
    $config{'trans_check_new'} &&
    (my $v = &trans_check_new_release()))
{
  &trans_display_msg (
    sprintf ($text{'NEW_RELEASE_AVAILABLE'}, $v, $v), 'info', 'bell');
}

print qq(<form action="index.cgi" method="post">);

if ((my $ret = &trans_monitor_news ()) ne '')
{
  $ret = qq(
      <p align=center>$text{'MONITOR_NEWS'}</p>
      <br/><table class="trans header" style="margin:auto">$ret</table>);
  $ret =~ s/\n/ /g;
  &trans_display_msg ($ret, 'info', 'bell');
}

print qq(<p>$text{'INDEX_DESCRIPTION'}</p>\n);

print qq(<p>$text{'IMPORTANT_NOTICE'}</p>);

print qq(<p>$text{'MOD_NOT_AVAIL_NOTICE'}</p>);

print qq(</form>);

print qq(<p>);&icons_table (\@links, \@titles, \@icons);print qq(</p>);

print qq(<hr/>);
print qq(<p><i>wbmtranslator</i> <b>$module_info{'version'}</b></p>);
&footer ('/', $text{'index'});
