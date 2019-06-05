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
my $filter_modified = $in{'filter_modified'};
my %file_ref = ($webmin_lang eq 'lang') ?
     &trans_get_items ("$root_directory/lang/$ref_lang") :
     &trans_get_items (&trans_get_path ($app, "lang/$ref_lang"));
my %file = ($webmin_lang eq 'lang') ?
     &trans_get_items ("$root_directory/lang/$lang") :
     &trans_get_items (&trans_get_path ($app, "lang/$lang"));
my %removed = &trans_get_hash_diff_removed ($ref_lang, $lang, \%file_ref, \%file);
my %new = &trans_get_hash_diff_new ($ref_lang, $lang, \%file_ref, \%file);
my @updated = &trans_get_array_updated ( 'interface', $ref_lang, $app);

foreach my $key (keys (%removed))
{
  $file_ref{"$key"} = $removed{"$key"};
};

foreach my $key (keys (%new))
{
  delete $file_ref{"$key"};
};

##### POST actions #####
#
# update translation file
if ($in{'update'} ne '')
{
  ($webmin_lang eq 'lang') ?
    open (H, '>', "$root_directory/lang/$lang") :
    open (H, '>', &trans_get_path ($app, "lang/$lang"));
  foreach my $item (sort keys %in)
  {
    if ($item =~ /newitem_/)
    {
      $item =~ s/newitem_//g;
      $in{"newitem_$item"} =~ s/(\r\n|\n)/ /g;
      print H $item.'='.$in{"newitem_$item"}."\n";
    }
  }
  close (H);

  # FIXME
  # do not HTML encode webmin "/lang/*" files
  ($webmin_lang eq 'lang') ?
    &trans_char2ent ("$root_directory/lang/$lang", 'work') :
    &trans_char2ent (&trans_get_path ($app, "lang/$lang"), 'html');

  &redirect ("interface_main.cgi?app=$app&t=$lang&o=update_trans&webmin_lang=$webmin_lang");
  exit;
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, "lang", 1, 0, 0, qq(<b><a href="javascript:translate_console_open ();">$text{'TRANSLATE_CONSOLE_LINK'}</a></b>));
&trans_translate_console_get_javascript ($lang);
print "<hr>\n";

printf qq(<h1>$text{'EDIT_TITLE'}</h1>), $app;

print qq(<p>);
if ($ref_lang ne $lang)
{
  printf qq($text{'EDIT_DESCRIPTION1'}), $ref_lang, $lang;
}
else
{
  printf qq($text{'EDIT_DESCRIPTION2'}), $ref_lang, $lang;
}
print qq(</p>);

print qq(<form action="interface_edit.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="t" value="$lang">);
print qq(<input type="hidden" name="webmin_lang" value="$webmin_lang">);

print qq(<input type="submit" name="filter_modified" value="$text{'ONLY_MODIFIED'}">&nbsp;<input type="submit" value="$text{'DISPLAY_ALL'}">);

print qq(
  <p>
  <table border=0 width="10%">
  <tr>
  <td width="5%" nowrap><img src="images/updated.png"></td>
  <td nowrap>= $text{'MODIFIED'}</td>
  </tr>
  </table>
  </p>
);

print qq(<table border=0 cellspacing=2 cellpadding=2>);
foreach my $key (sort keys %file_ref)
{
  my %hash = ();
  my $panel = '';
  my $modified = 0;
  
  %hash = &trans_get_item_updated (\@updated, $key);
  $modified = ($hash{'key'} eq $key);

  $panel = qq(<tr><td $tb colspan=2><b>$key</b> :</td></tr>);

  # modified
  if ($modified)
  {
    $panel .= qq(<tr><td bgcolor="orange">[<b>$ref_lang</b>]</td>);
    $panel .= qq(<td>
      <table border="1" cellspacing="1" cellpadding="1">
      <tr><td valign="top" nowrap><b>$text{'OLD_STRING'}:</b></td>
      <td valign="top" bgcolor="#FFFF77"><code>);
    $panel .= &html_escape ($hash{'old'});
    $panel .= qq(</code></td></tr><tr><td valign="top" nowrap>
      <b>$text{'NEW_STRING'}:</b></td>
      <td valign="top" bgcolor="#AAFFAA"><code>);
    $panel .= &html_escape ($hash{'new'});
    $panel .= qq(</code></td></tr></table></td></tr>);
  }
  # translated
  else
  {
    $panel .= qq(<tr><td $cb>[<b>$ref_lang</b>]</td><td><code>);
    $panel .= &html_escape ($file_ref{$key}) . qq(</code></td></tr>);
  };

  if ($filter_modified && !$modified) 
  {
    print qq(<input type="hidden" name="newitem_$key" value=");
    print (($in{"newitem_$key"} ne '') ? 
      &html_escape ($in{"newitem_$key"}) : &html_escape ($file{$key}));

    print qq(">);
  }
  else
  {
    print qq(
      $panel
      <tr><td $cb>[<b>$lang</b>]</td><td>
      <textarea name="newitem_$key" rows=5 cols=80>);
    print (($in{"newitem_$key"} ne '') ? 
                           $in{"newitem_$key"} : $file{$key});

    print qq(</textarea></td></tr>);
  }
}

print qq(</table>);
print qq(<p>);
print qq(<input type="submit" name="update" value="$text{'UPDATE_TRANSLATION_FILE'}">);
print qq(</p>);
print qq(</form>);

print qq(<hr>);
&footer("interface_main.cgi?app=$app&webmin_lang=$webmin_lang", $text{'INTERFACE_INDEX'});
