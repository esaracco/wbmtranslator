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
my $filter_modified = $in{'filter_modified'};
my @sfile = ();
my @sfile_ref = ();
my %file_ref = ();
my %file = ();
my %removed = ();
my %new = ();
my @updated = ();
my $fref = '';
my $lref = '';

if (-f &trans_get_path ($app, "config.info.$ref_lang"))
{
  $fref = "config.info.$ref_lang";
  $lref = ".$ref_lang";
}
else
{
  $fref = "config.info";
  $lref = '';
}
$fref = (-f &trans_get_path ($app, "config.info.$ref_lang")) ?
  "config.info.$ref_lang" : 'config.info';

@sfile_ref = &trans_get_items_static (&trans_get_path ($app, $fref));
%file_ref = &trans_get_items (&trans_get_path ($app, $fref));
%file = &trans_get_items ((&trans_get_path ($app, 'config.info')) . 
  (($ref_lang eq $lang) ? $lref : ".$lang"));
@updated = &trans_get_array_updated ( 'config', $ref_lang, $app);

##### POST actions #####
#
# update config.info file
if ($in{'update'} ne '')
{
  my $old = (&trans_get_path ($app, 'config.info')) . 
    (($ref_lang eq $lang) ? $lref : ".$lang");
  
  open (H, '>', $old);
  chmod (0755, $old);
  for (my $i = 0; $i < $#sfile_ref + 1; $i++)
  {
    my %h = %{$sfile_ref[$i]};
    my ($k, $v) = each (%h);

    print H "$k=".$in{"$k"}."\n" if ($in{"$k"} ne '');
  }
  close (H);

  &trans_char2ent ("$old", 'html');

  &redirect ("module_config_main.cgi?app=$app&t=$lang&o=update_trans");
  exit;
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0, 0, qq(<b><a href="javascript:translate_console_open ();">$text{'TRANSLATE_CONSOLE_LINK'}</a></b>));
&trans_translate_console_get_javascript ($lang);
print "<hr>\n";

printf qq(<h1>$text{'EDIT_TITLE'}</h1>), $app;

print qq(<p>);
if ($ref_lang ne $lang) {printf qq($text{'EDIT_DESCRIPTION1'}), $fref, $lang;}
  else {printf qq($text{'EDIT_DESCRIPTION2'}), $fref, $lang;}
print qq(</p>);

print qq(<form action="module_config_edit.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="t" value="$lang">);

print qq(<input type="submit" name="filter_modified" value="$text{'ONLY_MODIFIED'}">&nbsp;<input type="submit" value="$text{'DISPLAY_ALL'}">);

print qq(
  <p>
  <table border=0 width="10%">
  <tr>
  <td width="5%" nowrap><img src="images/translated.png"></td>
  <td nowrap>= $text{'TRANSLATED'},</td>
  <td width="5%" nowrap><img src="images/to_translate.png"></td>
  <td nowrap>= $text{'NOT_TRANSLATED'},</td>
  <td width="5%" nowrap><img src="images/updated.png"></td>
  <td nowrap>= $text{'MODIFIED'}</td>
  </tr>
  </table>
  </p>
);

print qq(<table border=0 cellspacing=2 cellpadding=2>);
foreach my $key (keys (%file_ref))
{
  my %hash = ();
  my $panel = '';
  my $modified = 0;
  my $trans_value = &html_escape ($in{"$key"} ne '') ? 
    $in{"$key"} : $file{$key};

  %hash = &trans_get_item_updated (\@updated, $key);
  $modified = ($hash{'key'} eq $key); 

  $panel = qq(<tr><td $tb colspan=2><b>$key</b> :</td></tr>);

  # not translated
  if ($trans_value eq '')
  {
    $panel .= qq(<tr><td bgcolor="red">[<b>$ref_lang</b>]</td><td><code>);
    $panel .= &html_escape ($file_ref{$key});
    $panel .= qq(</code></td></tr>);
  }
  # modified
  elsif ($modified)
  {
    $panel .= qq(<tr><td bgcolor="orange">[<b>$ref_lang</b>]</td>);
    $panel .= qq(<td>
    <table border="1" cellspacing="1" cellpadding="1">
    <tr><td valign="top" nowrap><b>$text{'OLD_STRING'}:</b></td><td valign="top" bgcolor="#FFFF77"><code>);
    $panel .= &html_escape ($hash{'old'});
    $panel .= qq(</code></td></tr>
    <tr><td valign="top" nowrap><b>$text{'NEW_STRING'}:</b></td><td valign="top" bgcolor="#AAFFAA"><code>);
    $panel .= &html_escape ($hash{'new'});
    $panel .= qq(</code></td></tr></table></td></tr>);
  }
  # translated
  else
  {
    $panel .= qq(<tr><td bgcolor="green">[<b>$ref_lang</b>]</td><td><code>);
    $panel .= &html_escape ($file_ref{$key});
    $panel .= qq(</code></td></tr>);
  };
  
  if ($filter_modified && !$modified) 
  {
    print qq(<input type="hidden" name="$key" value=");
    print &html_escape ($trans_value);
    print qq(">);
  }
  else
  {
    print qq($panel<tr><td $cb>[<b>$lang</b>]</td><td>
    <textarea name="$key" rows=5 cols=80>);
    print $trans_value;
    print qq(</textarea></td></tr>);
  }
}
print qq(</table>);
print qq(<p><input type="submit" name="update" value="$text{'UPDATE_TRANSLATION_FILE'}"></p>);
print qq(</form>);

print qq(<hr>);
&footer("module_config_main.cgi?app=$app", $text{'MODULE_CONFIG_INDEX'});
