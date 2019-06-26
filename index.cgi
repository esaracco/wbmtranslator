#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA 02111-1307, USA.

require './translator-lib.pl';

my $remove = $in{'remove'};
my $ret = '';

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

# remove app from monitor
&trans_set_user_var ("monitor_" . &trans_get_current_app () . "_$remove", 0) if ($remove ne '');

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, "help", 1, 1, 0, undef, undef, undef, "<a href=\"http://wbmtranslator.esaracco.fr\" target=\"_BLANK\">$text{'PROJECT_HOMEPAGE'}</a>&nbsp;|&nbsp;<a href=\"http://download.webmin.com/devel/tarballs/\" target=\"_BLANK\">$text{'LATEST_WEBMIN'}</a>");
print "<hr>\n";

&trans_main_check_config ();
&trans_check_perl_deps ();

print qq(<form action="index.cgi" method="post">);

print qq(<p>$text{'INDEX_DESCRIPTION'}</p>\n);

print qq(<p>$text{'IMPORTANT_NOTICE'}</p>);

print qq(<p>$text{'MOD_NOT_AVAIL_NOTICE'}</p>);

if (($ret = &trans_monitor_news ()) ne '')
{
  print qq(
  <p>
  <table align="center" cellspacing="5" cellpadding="10" width="40%" style="background: silver;font-size: 10px;font-family: Verdana, Arial, Helvetica, sans-serif;color: black;border: 2px blue solid;">
  <tr><td>$text{'MONITOR_NEWS'}</td></tr>
  <tr><td align="center">
  <table border=1 style="background: silver;font-size: 10px;font-family: Verdana, Arial, Helvetica, sans-serif;color: black;border: 1px black solid;">
  $ret
  </table>
  </td></tr>
  </table>
  </p>
    );
}

print qq(<form>);

print qq(<p>);
&icons_table (\@links, \@titles, \@icons);
print qq(</p>);

print qq(<hr/>);
&trans_footer ();
&footer("/", $text{'index'});
