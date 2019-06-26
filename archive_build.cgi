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

my $lang = $in{'l'};
my @array_app = split(/\|/, $in{'app'});
my $multiple_modules = (scalar (@array_app) > 1);
my $app = ($multiple_modules) ? $text{'MULTIPLE_MODULES'} : $array_app[0];
my $body = $in{'body'};
my $suffix = '';
my $size = 0;
my $size_print = 0;
my $webmin_version = &get_webmin_version();
my $module_version = ($multiple_modules) ? '' : &trans_get_module_version ($app);
my $file = &trans_get_translation_filename (\@array_app, $lang);
my $filename = $file;
my $hid_mods = '';

##### POST actions #####
#
# send the file to the browser
if ($in{'download'} ne '')
{
  &trans_archive_send_browser ($file);
  exit;
}
# create the file
elsif (not $in{'send'})
{
  &trans_archive_create ($file, $lang, \@array_app);
}
#
########################

$size = -s "/$config{'trans_working_path'}/.translator/$remote_user/archives/$file";
$size_print = &trans_get_string_from_size ($size);

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0);
print "<hr>\n";
printf qq(<h1>$text{'ARCHIVE_TITLE'}</h1>), $app;

print qq(<p>);
print qq(<form action="archive_build.cgi" method="post">);

foreach my $mod (@array_app) {$hid_mods .= "$mod|"}
$hid_mods =~ s/\|$//g;
print qq(<input type="hidden" name="app" value="$in{'app'}">);
  
print qq(<input type="hidden" name="l" value="$lang">);
print qq(
  <p>
  <table border=1>
  <tr><td $cb>$text{'FILENAME'}:</td><td>$filename</td></tr>
  <tr><td $cb>$text{'FILESIZE'}:</td><td>$size_print</td></tr>
  <tr><td colspan="2" align="center">
  <input type="submit" value="$text{'DOWNLOAD'}" name="download">
  </td></tr>
  <tr><th $cb colspan="2">$text{'ARCHIVE_CONTENT'}</th></tr>
  <tr><td colspan="2">);
  &trans_archive_list_content ($file);
  print qq(</td></tr>
  </table>
  </p>
);

print qq(</form>);
print qq(</p>);

print qq(<hr>);

my $url = 'archive_main.cgi?';
foreach my $mod (@array_app) {$hid_mods .= "$mod\0"}
$hid_mods =~ s/\0$//;
$url .= '&app='.&urlize ((scalar(@array_app) == 1) ? $array_app[0] : '' );

&footer($url, $text{'MODULE_INDEX_ARCHIVE'});
