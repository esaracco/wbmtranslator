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

my $app = $in{'app'};
my $lang = $in{'t'};
my %file = &trans_get_items (&trans_get_path ($app, "config.info.$lang"));
my %file_ref = &trans_get_items (&trans_get_path ($app, 'config.info'));
my %new = &trans_get_hash_diff_new ($ref_lang, $lang, \%file_ref, \%file);
my %removed = &trans_get_hash_diff_removed ($ref_lang, $lang, \%file_ref, \%file);

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0);
print "<hr>\n";

printf qq(<h1>$text{'MODULE_CONFIG_VIEW_ADDED_TITLE'}</h1>), $app;
printf qq(<p>$text{'MODULE_CONFIG_VIEW_ADDED_DESCRIPTION'}</p>), "config.info.$lang";

print qq(<p>);
print qq(<table border=0 cellspacing=2 cellpadding=2>);
foreach my $key (sort keys %new)
{
  print qq(
    <tr><td $tb colspan=2><b>$key</b> :</td></tr>
    <tr><td $cb>[<b>$ref_lang</b>]</td><td><code>);
  print &html_escape ($new{$key});
  print qq(</code></td></tr>);
}
print qq(</table>);
print qq(</p>);

print qq(<hr>);
&footer("module_config_main.cgi?app=$app", $text{'MODULE_CONFIG_INDEX'});
