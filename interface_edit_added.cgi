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
my $webmin_lang = $in{'webmin_lang'};
my %file = ($webmin_lang eq 'lang')  ?
  &trans_get_items ("$root_directory/lang/$lang") :
  &trans_get_items (&trans_get_path ($app, "lang/$lang"));
my %file_ref = ($webmin_lang eq 'lang')  ?
  &trans_get_items ("$root_directory/lang/$ref_lang") :
  &trans_get_items (&trans_get_path ($app, "lang/$ref_lang"));
my %new = &trans_get_hash_diff_new ($ref_lang, $lang, \%file_ref, \%file);

##### POST actions #####
#
# add new items in the translation file
if ($in{'update'} ne '')
{
  my $updated = 0;
  my $url = '';
  
  foreach my $item (keys %in)
  {
    if ($item =~ /newitem_/)
    {
      $item =~ s/newitem_//g;
      if ($in{"newitem_$item"} ne '')
      {
        $updated = 1;
        $file{$item} = $in{"newitem_$item"};
      }
    }
  }

  ($webmin_lang eq 'lang')  ?
    open (H, ">$root_directory/lang/$lang") :
    open (H, ">" . (&trans_get_path ($app, "lang/$lang")));
  foreach my $item (sort keys %file)
  {
    next if ($item eq '');
    print H "$item=$file{$item}\n";
  }
  close (H);
  
  # FIXME
  # do not encode webmin "/lang/*" files
  ($webmin_lang eq 'lang')  ?
    &trans_char2ent ("$root_directory/lang/$lang", 'work') :
    &trans_char2ent (&trans_get_path ($app, "lang/$lang"), 'html');

  $url = "interface_main.cgi?app=$app&t=$lang&webmin_lang=$webmin_lang";
  $url .= "&o=add_new" if ($updated);
  
  &redirect ($url);
  exit;
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0, 0, qq(<b><a href="javascript:translate_console_open ();">$text{'TRANSLATE_CONSOLE_LINK'}</a></b>));
&trans_translate_console_get_javascript ();
print "<hr>\n";

printf qq(<h1>$text{'EDIT_ADDED_TITLE'}</h1>), $app;
printf qq(<p>$text{'EDIT_ADDED_DESCRIPTION'}</p>), $ref_lang, $lang;

print qq(<p>);
print qq(<form action="interface_edit_added.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="t" value="$lang">);
print qq(<input type="hidden" name="webmin_lang" value="$webmin_lang">);
print qq(<table border=0 cellspacing=2 cellpadding=2>);
foreach my $key (sort keys %new)
{
  print qq(<tr><td $tb colspan=2><b>$key</b> :</td></tr>
    <tr><td $cb>[<b>$ref_lang</b>]</td><td><code>);
  print &html_escape ($new{"$key"});
  print qq(</code></td></tr><tr><td $cb>[<b>$lang</b>]</td><td>
    <textarea name="newitem_$key" rows=5 cols=80>$in{"newitem_$key"}</textarea>
    </td></tr>);
}
print qq(</table>);
print qq(<p><input type="submit" name="update" value="$text{'UPDATE_TRANSLATION_FILE'}"></p>);
print qq(</form>);
print qq(</p>);

print qq(<hr>);
&footer("interface_main.cgi?app=$app&webmin_lang=$webmin_lang", $text{'INTERFACE_INDEX'});
