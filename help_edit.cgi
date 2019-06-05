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
my $f1 = $in{'f1'}; $f1 =~ s/[^a-z0-9\-_\.]+//gi;
my $f2 = $in{'f2'}; $f2 =~ s/[^a-z0-9\-_\.]+//gi;
my $content = $in{'content'};
my $more = ($in{'more'} ne '');
my $less = ($in{'less'} ne '');
my $rows = $in{'rows'};
my $path = &trans_get_path ($app, 'help');
my $msg = '';

my @tmp = split (/\./, $f2);
my $lang = ($#tmp == 2) ? $tmp[1] : $tmp[1].'.'.$tmp[2];

$lang ||= $current_lang;

# manage textareas size
$rows = 20 if ($rows eq '');
$rows += 5 if ($more);
$rows -= 5 if ($less);

##### POST actions #####
#
# update the help file (create it if it does not exist)
if ($in{'update'} ne '')
{
  if ($content ne '')
  {
    open (H, '>', "$path/$f2");
    print H $content;
    close (H);
    &trans_char2ent ("$path/$f2", 'html');

    chmod (0755, "$path/$f2");

    &redirect ("help_main.cgi?app=$app&o=update_trans");
    exit;
  }
  else
  {
    $msg = $text{'MSG_TRANSLATION_EMPTY_ERROR'};
  }
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0, 0, qq(<b><a href="javascript:translate_console_open ();">$text{'TRANSLATE_CONSOLE_LINK'}</a></b>));
&trans_translate_console_get_javascript ($lang);
print "<hr>\n";

printf qq(<h1>$text{'EDIT_TITLE'}</h1>), $app;

print qq(<p>);
if ($ref ne $lang)
  {printf qq($text{'EDIT_DESCRIPTION1'}), $fref, $lang;}
else
  {printf qq($text{'EDIT_DESCRIPTION2'}), $fref, $lang;}
print qq(</p>);

print qq(<form action="help_edit.cgi" method="post">);
print qq(<input type="hidden" name="f1" value="$f1">);
print qq(<input type="hidden" name="f2" value="$f2">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="rows" value="$rows">);

print qq(<p><b>$msg</b></p>) if ($msg ne '');

print qq(<table border=0 cellspacing=2 cellpadding=2>);
print qq(<tr><td><input type="submit" name="more" value="$text{'HELP_TEXTAREA_MORE'}">&nbsp;<input type="submit" name="less" value="$text{'HELP_TEXTAREA_LESS'}"></td></tr>);
print qq(<tr><td>&nbsp;</td></tr>);
print qq(<tr><th $tb>$text{'HELP_CONTENT1'}&nbsp;$lang</th></tr>);
print qq(<tr><td><textarea rows="$rows" cols="110" style="color:blue;background:silver">);

# this file is intended to be in english, so no need to
# encode/decode it (our "modified" detection method is based on
# last modified date, so it will break if we write this file here)
open (H, '<', "$path/$f1"); print $_ while (<H>); close (H);
print qq(</textarea></td></tr>);

print qq(<tr><td>&nbsp;</td></tr>);

print qq(<tr><th $tb>$text{'HELP_CONTENT2'}</th></tr>);
print qq(<tr><td><textarea rows="$rows" cols="110" name="content">);
&trans_char2ent ("$path/$f2", 'work');
open (H, '<', "$path/$f2"); print $_ while (<H>); close (H);
&trans_char2ent ("$path/$f2", 'html');
print qq(</textarea></td></tr>);

print qq(</table>);
print qq(<p><input type="submit" name="update" value="$text{'UPDATE_TRANSLATION_FILE'}"></p>);
print qq(</form>);

print qq(<hr>);
&footer("help_main.cgi?app=$app", $text{'HELP_INDEX'});
